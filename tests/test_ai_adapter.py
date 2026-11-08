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
