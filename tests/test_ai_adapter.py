"""Actual adapter logic with mocked provider HTTP, no network or paid inference."""

import json

import httpx
import pytest

from reconflow.config import settings
from reconflow.db import SessionLocal
from reconflow.evaluation import dataset
from reconflow.services import ai


@pytest.fixture
def fake_provider(monkeypatch):
    cfg = settings()
    monkeypatch.setattr(cfg, "llm_api_key", "unit-test-placeholder")
    monkeypatch.setattr(cfg, "llm_model", "mock-provider")
    original = httpx.Client

    def install(handler):
        monkeypatch.setattr(
            ai.httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(handler), **kw)
        )

    return install


@pytest.mark.parametrize("model", ["mock-provider", "gpt-5.4-mini-2026-03-17"])
def test_adapter_tool_and_validated_report(fake_provider, monkeypatch, model):
    monkeypatch.setattr(settings(), "llm_model", model)
    case = dataset()[0]

    def respond(request):
        body = json.loads(request.content)
        assert body["max_completion_tokens"] == 1200
        assert "max_tokens" not in body
        if model.startswith("gpt-5.4-mini"):
            assert body["reasoning_effort"] == "none"
        else:
            assert "reasoning_effort" not in body
        if len(body["messages"]) == 2:
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call1",
                        "type": "function",
                        "function": {"name": "get_case", "arguments": "{}"},
                    }
                ],
            }
        else:
            payload = ai.simulated_report(case["id"], "FEE_MISMATCH", [f"case:{case['id']}"])
            payload["requires_human_review"] = False
            message = {"role": "assistant", "content": json.dumps(payload)}
        return httpx.Response(
            200,
            json={
                "choices": [{"message": message}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            },
        )

    fake_provider(respond)
    with SessionLocal.begin() as db:
        result, trace = ai.live_report(db, case["id"], case["tools"], evaluation=True)
        assert result["requires_human_review"] is True
        assert len(trace) == 1


def test_adapter_rejects_arbitrary_tool(fake_provider):
    def respond(request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "bad",
                                    "function": {"name": "execute_sql", "arguments": "{}"},
                                }
                            ],
                        }
                    }
                ]
            },
        )

    fake_provider(respond)
    case = dataset()[0]
    with SessionLocal.begin() as db, pytest.raises(ValueError, match="Tool policy"):
        ai.live_report(db, case["id"], case["tools"], evaluation=True)


def test_adapter_rejects_unobserved_citation(fake_provider):
    case = dataset()[0]
    payload = ai.simulated_report(case["id"], "FEE_MISMATCH", ["evidence:SECRET"])
    fake_provider(
        lambda request: httpx.Response(
            200, json={"choices": [{"message": {"content": json.dumps(payload)}}]}
        )
    )
    with SessionLocal.begin() as db, pytest.raises(ValueError, match="unobserved"):
        ai.live_report(db, case["id"], case["tools"], evaluation=True)


def test_adapter_stops_after_four_tools(fake_provider):
    case = dataset()[0]
    calls = []

    def respond(request):
        calls.append(1)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": str(len(calls)),
                                    "function": {"name": "get_case", "arguments": "{}"},
                                }
                            ],
                        }
                    }
                ]
            },
        )

    fake_provider(respond)
    with SessionLocal.begin() as db, pytest.raises(ValueError, match="Tool policy"):
        ai.live_report(db, case["id"], case["tools"], evaluation=True)
    assert len(calls) == 5


def test_adapter_accounts_for_transport_error_without_logging_exception(fake_provider):
    def respond(request):
        raise httpx.ReadTimeout("sensitive diagnostic")

    fake_provider(respond)
    case = dataset()[0]
    from sqlalchemy import select

    from reconflow.models import Invocation

    with SessionLocal.begin() as db:
        with pytest.raises(httpx.ReadTimeout):
            ai.live_report(db, case["id"], case["tools"], evaluation=True)
        db.flush()
        invocation = db.scalar(select(Invocation))
        assert invocation.status == "TRANSPORT_ERROR"
        assert invocation.input_tokens == 0 and invocation.output_tokens == 0
        assert invocation.case_id is None


def test_controlled_adapter_preserves_failed_raw_payload_and_versioned_prompt(fake_provider):
    from reconflow.evaluation_v2 import dataset as dataset_v2
    from reconflow.services import controlled

    case = dataset_v2()[0]
    tools, assessment = controlled.enrich_tools(case["tools"])
    payload = controlled.scripted_report(case["id"], assessment)
    payload["requires_human_review"] = False

    def respond(request):
        body = json.loads(request.content)
        assert controlled.VERSION in body["messages"][0]["content"]
        if len(body["messages"]) == 2:
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": str(i),
                        "type": "function",
                        "function": {"name": name, "arguments": "{}"},
                    }
                    for i, name in enumerate(tools)
                ],
            }
        else:
            message = {"role": "assistant", "content": json.dumps(payload)}
        return httpx.Response(
            200,
            json={
                "choices": [{"message": message}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            },
        )

    fake_provider(respond)
    with SessionLocal.begin() as db:
        report, trace = ai.live_report(
            db, case["id"], tools, evaluation=True, profile=controlled.VERSION
        )
        assert report == payload and report["requires_human_review"] is False
        check = controlled.validate(
            report, case["id"], assessment, {t["result"]["evidence_id"] for t in trace}
        )
        assert "HUMAN_REVIEW_REQUIRED" in check["flags"]


@pytest.mark.parametrize("failure", ["invalid_json", "truncated", "http", "unsafe"])
def test_live_v2_failure_capture_and_accounting(fake_provider, monkeypatch, failure):
    from reconflow import evaluation_v2
    from reconflow.services import controlled

    cfg = settings()
    monkeypatch.setattr(cfg, "llm_input_usd_per_million", "0.75")
    monkeypatch.setattr(cfg, "llm_output_usd_per_million", "4.50")
    requests = []
    original = "{bad JSON: ORIGINAL MODEL OUTPUT"

    def respond(request):
        body = json.loads(request.content)
        requests.append(body)
        system = body["messages"][0]["content"]
        assert system == controlled.SYSTEM_V2 + json.dumps(
            controlled.ControlledReport.model_json_schema()
        )
        assert {t["function"]["name"] for t in body["tools"]} == {
            "get_case",
            "get_payment_and_payout",
            "find_candidate_bank_credits",
            "get_provider_policy",
        }

        # These grading containers are never serialized anywhere in provider requests.
        def inspect(value):
            if isinstance(value, dict):
                assert not {"expected", "family", "split"} & value.keys()
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)
            elif isinstance(value, str) and value.startswith("{"):
                try:
                    parsed = json.loads(value)
                except ValueError:
                    return
                inspect(parsed)

        inspect(body)
        if failure == "http":
            return httpx.Response(429, json={"error": "redacted"})
        if len(body["messages"]) == 2:
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": str(i),
                        "type": "function",
                        "function": {"name": t["function"]["name"], "arguments": "{}"},
                    }
                    for i, t in enumerate(body["tools"])
                ],
            }
            finish = "tool_calls"
        elif failure == "unsafe":
            case_id = evaluation_v2.dataset()[0]["id"]
            tools, assessment = controlled.enrich_tools(evaluation_v2.dataset()[0]["tools"])
            report = controlled.scripted_report(case_id, assessment)
            report["recommended_next_step"] = "APPROVE_AND_PAY"
            message, finish = {"content": json.dumps(report)}, "stop"
        else:
            message, finish = {"content": original}, "length" if failure == "truncated" else "stop"
        return httpx.Response(
            200,
            json={
                "model": "mock-snapshot",
                "choices": [{"message": message, "finish_reason": finish}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            },
        )

    fake_provider(respond)
    with SessionLocal.begin() as db:
        r = evaluation_v2.evaluate(db, live=True, split="development", limit=1, max_cost_usd="2")
        row = r["cases"][0]
        assert r["model_correct"] == 0 and len(r["failures"]) == 1
        if failure == "http":
            assert row["validation"]["flags"] == ["PROVIDER_HTTP_ERROR"]
            assert row["http_status"] == 429
            assert r["status"] == "STOPPED_UNMETERED_REQUEST"
            assert r["usage"]["unmetered_requests"] == 1
        else:
            assert r["usage"]["requests"] == 2
            assert r["usage"]["input_tokens"] == 200 and r["usage"]["output_tokens"] == 40
            assert row["provider_responses"][-1]["model"] == "mock-snapshot"
            if failure == "unsafe":
                assert row["raw_output"]["recommended_next_step"] == "APPROVE_AND_PAY"
                assert set(row["failure_categories"]) == {
                    "SCHEMA_REJECTED",
                    "UNSAFE_RECOMMENDATION",
                }
            else:
                assert row["raw_content"] == original and row["raw_output"] is None
                assert row["validation"]["flags"] == [
                    "OUTPUT_TRUNCATED" if failure == "truncated" else "INVALID_OUTPUT_JSON"
                ]


def test_live_v2_budget_blocks_http_before_first_request(fake_provider, monkeypatch):
    from sqlalchemy import func, select

    from reconflow import evaluation_v2
    from reconflow.models import Invocation

    monkeypatch.setattr(settings(), "llm_input_usd_per_million", "0.75")
    monkeypatch.setattr(settings(), "llm_output_usd_per_million", "4.50")
    fake_provider(lambda request: pytest.fail("Budget must reject before HTTP"))
    with SessionLocal.begin() as db:
        r = evaluation_v2.evaluate(
            db, live=True, split="development", limit=12, max_cost_usd="0.000001"
        )
        assert r["status"] == "STOPPED_BUDGET"
        assert r["usage"]["requests"] == 0
        assert r["cases_run"] == 0 and r["cases_requested"] == 12
        assert r["model_accuracy"] is None and r["live_quality"] == "NOT MEASURED"
        assert r["model_correct"] == 0
        assert db.scalar(select(func.count()).select_from(Invocation)) == 0
