"""HTTP adapters: authenticate, authorize, validate, then invoke domain services."""

import hashlib
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from reconflow.config import settings
from reconflow.db import SessionLocal, now
from reconflow.models import (
    Audit,
    BankCredit,
    Case,
    Control,
    Evaluation,
    ImportBatch,
    Investigation,
    Invocation,
    Job,
    LoginSession,
    Match,
    Payment,
    Payout,
    Proposal,
    Provider,
    Run,
)
from reconflow.public_docs import router as public_docs_router
from reconflow.security import csrf, csrf_token, current_user, login, require
from reconflow.services import ai, analytics, controlled, ingestion, reviews
from reconflow.services.audit import append
from reconflow.services.money import display
from reconflow.services.public_docs import PUBLIC_ROOT

app = FastAPI(title="ReconFlow", docs_url=None, redoc_url=None)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings().session_secret,
    https_only=settings().cookie_secure,
    same_site="lax",
    max_age=28800,
)
app.mount("/static", StaticFiles(directory="reconflow/static"), name="static")
app.mount("/docs-assets", StaticFiles(directory=PUBLIC_ROOT / "assets"), name="docs-assets")
app.include_router(public_docs_router)
templates = Jinja2Templates(directory="reconflow/templates")
templates.env.filters["money"] = display
NAV_GROUPS = [
    (
        "Banking operations",
        [
            ("/", "Overview"),
            ("/imports", "Sources & imports"),
            ("/runs", "Reconciliation runs"),
            ("/payouts", "Transactions & payouts"),
            ("/exceptions", "Exceptions"),
            ("/investigations", "AI investigations"),
            ("/review", "Review queue"),
        ],
    ),
    (
        "Reporting & assurance",
        [
            ("/reports/operations", "Operations report"),
            ("/reports/impact", "Business impact"),
            ("/ai/evaluation", "AI evaluation"),
            ("/audit", "Audit trail"),
        ],
    ),
    (
        "Administration",
        [
            ("/operations/health", "Worker health"),
            ("/controls", "Configuration & controls"),
        ],
    ),
    (
        "Resources",
        [
            ("/guide", "Architecture & rollout"),
            ("/docs/", "Public documentation"),
        ],
    ),
]


def database() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db


DB = Annotated[Session, Depends(database)]


def render(request: Request, db: Session, title: str, **context: object) -> Response:
    user = current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="page.html",
        context={
            "title": title,
            "user": user,
            "nav_groups": NAV_GROUPS,
            "csrf": csrf_token(request),
            "path": request.url.path,
            **context,
        },
    )


def redirect(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


def link(label: object, href: str) -> dict:
    return {"label": str(label), "href": href}


@app.middleware("http")
async def headers(request: Request, call_next) -> Response:
    if (
        request.headers.get("content-length", "0").isdigit()
        and int(request.headers.get("content-length", "0")) > 8_100_000
    ):
        return Response("Upload exceeds 8 MB", status_code=413)
    response = await call_next(request)
    # Mermaid emits SVG styling; allow inline styles only for the public reader.
    # Script execution stays restricted to self-hosted assets, with no inline JS/eval.
    style_policy = (
        "'self' 'unsafe-inline'"
        if (request.url.path == "/docs" or request.url.path.startswith("/docs/"))
        else "'self'"
    )
    response.headers.update(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "same-origin",
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; "
            f"style-src {style_policy}; "
            "img-src 'self' data:; frame-ancestors 'none'; form-action 'self'; "
            "object-src 'none'; base-uri 'self'",
        }
    )
    if request.url.path.startswith("/static/docs-chunks/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response


@app.exception_handler(Exception)
async def error(request: Request, exc: Exception) -> Response:
    # Never expose DB errors, inputs or secrets in the browser.
    return HTMLResponse(
        "Unexpected server error. Retry safely or inspect worker health.", status_code=500
    )


@app.exception_handler(ValueError)
async def invalid(request: Request, exc: ValueError) -> Response:
    import html

    return HTMLResponse(
        f"<h1>Action could not complete</h1><p>{html.escape(str(exc))}</p>"
        '<a href="/">Return to overview</a>',
        status_code=400,
    )


@app.exception_handler(PermissionError)
async def forbidden(request: Request, exc: PermissionError) -> Response:
    return HTMLResponse("Role or maker-checker policy denied this action.", status_code=403)


@app.exception_handler(IntegrityError)
async def conflict(request: Request, exc: IntegrityError) -> Response:
    return HTMLResponse(
        "Source identity conflict. No records were partially imported. "
        "Replay the original CSV or refresh the page.",
        status_code=409,
    )


from fastapi import HTTPException  # noqa: E402


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException) -> Response:
    if exc.status_code == 401:
        return redirect("/login")
    import html

    return HTMLResponse(
        f"<h1>{exc.status_code}</h1><p>{html.escape(str(exc.detail))}</p>"
        '<a href="/">Return to overview</a>',
        status_code=exc.status_code,
    )


@app.get("/healthz")
def health(db: DB) -> dict[str, str | bool]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "synthetic_only": True}


@app.get("/readyz")
def ready(db: DB) -> dict[str, str]:
    if not db.get(Control, 1):
        raise HTTPException(503, "Run migration and seed")
    return {"status": "ready"}


@app.get("/login")
def login_page(request: Request) -> Response:
    return templates.TemplateResponse(
        request=request, name="login.html", context={"csrf": csrf_token(request), "error": None}
    )


@app.post("/login")
def sign_in(
    request: Request,
    db: DB,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    csrf_value: Annotated[str, Form()],
) -> Response:
    csrf(request, csrf_value)
    ok = login(request, db, email, password)
    db.commit()
    if ok:
        return redirect("/")
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"csrf": csrf_token(request), "error": "Email or password is incorrect."},
        status_code=400,
    )


@app.post("/logout")
def logout(request: Request, db: DB, csrf_value: Annotated[str, Form()]) -> Response:
    csrf(request, csrf_value)
    user = current_user(request, db)
    token_hash = hashlib.sha256(request.session["sid"].encode()).hexdigest()
    db.delete(db.get(LoginSession, token_hash))
    append(db, user.id, "logout", "authentication")
    db.commit()
    request.session.clear()
    return redirect("/login")


@app.get("/")
def home(request: Request, db: DB) -> Response:
    return render(
        request,
        db,
        "Settlement overview",
        view="overview",
        stats=analytics.overview(db),
        latest=db.scalars(select(Run).order_by(Run.id.desc()).limit(5)).all(),
    )


@app.get("/imports")
def imports(request: Request, db: DB) -> Response:
    rows = [
        [link(i.id, f"/imports/{i.id}"), i.name, i.status, i.created_at, i.digest[:16]]
        for i in db.scalars(select(ImportBatch).order_by(ImportBatch.id.desc()).limit(100))
    ]
    return render(
        request,
        db,
        "Sources & imports",
        view="imports",
        columns=["Batch", "Source", "State", "Imported (UTC)", "SHA-256 prefix"],
        rows=rows,
    )


@app.get("/scenarios/labels.csv")
def labels(request: Request, db: DB, count: int = 1000, scenario: str = "mismatch") -> Response:
    """Export generator expectations, never measured model predictions."""
    current_user(request, db)
    return Response(
        ingestion.scenario_labels(count, scenario),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="synthetic-labels.csv"'},
    )


@app.post("/scenarios")
def launch(
    request: Request,
    db: DB,
    csrf_value: Annotated[str, Form()],
    scenario: Annotated[str, Form()],
    count: Annotated[int, Form()],
) -> Response:
    user = current_user(request, db)
    require(user, "analyst", "admin")
    csrf(request, csrf_value)
    if not settings().demo_mode:
        raise ValueError("Scenario launch requires DEMO_MODE")
    source = ingestion.ingest(
        db,
        ingestion.scenario_csv(count, scenario),
        f"Synthetic {scenario} / {count}",
        user.id,
        scenario == "failure",
    )
    db.commit()
    return redirect(f"/imports/{source.id}")


@app.post("/imports")
async def upload(
    request: Request, db: DB, csrf_value: Annotated[str, Form()], file: UploadFile
) -> Response:
    user = current_user(request, db)
    require(user, "analyst", "admin")
    csrf(request, csrf_value)
    raw = await file.read(8_000_001)
    if len(raw) > 8_000_000:
        raise ValueError("CSV exceeds 8 MB")
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8") from exc
    source = ingestion.ingest(db, decoded, "Synthetic CSV upload", user.id)
    db.commit()
    return redirect(f"/imports/{source.id}")


@app.get("/imports/template.csv")
def csv_template(request: Request, db: DB) -> Response:
    current_user(request, db)
    return Response(
        ingestion.scenario_csv(100, "clean"),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="synthetic-template.csv"'},
    )


@app.get("/imports/{batch_id}")
def import_detail(request: Request, db: DB, batch_id: int) -> Response:
    source = db.get(ImportBatch, batch_id)
    if not source:
        raise HTTPException(404, "Import not found")
    run = db.scalar(select(Run).where(Run.import_id == batch_id))
    return render(
        request,
        db,
        f"Import #{batch_id}",
        view="import_detail",
        source=source,
        run=run,
        columns=["Payout", "Currency", "Declared net"],
        rows=[
            [
                link(p.external_id, f"/payouts/{p.id}"),
                p.currency,
                display(p.declared_net, p.currency),
            ]
            for p in db.scalars(select(Payout).where(Payout.import_id == batch_id).limit(100))
        ],
    )


@app.post("/imports/{batch_id}/replay")
def replay(request: Request, db: DB, batch_id: int, csrf_value: Annotated[str, Form()]) -> Response:
    user = current_user(request, db)
    require(user, "analyst", "admin")
    csrf(request, csrf_value)
    source = db.get(ImportBatch, batch_id)
    if not source:
        raise HTTPException(404, "Import not found")
    ingestion.ingest(db, source.raw_csv, source.name, user.id)
    db.commit()
    return redirect(f"/imports/{batch_id}")


@app.get("/imports/{batch_id}/export")
def export(request: Request, db: DB, batch_id: int) -> Response:
    current_user(request, db)
    source = db.get(ImportBatch, batch_id)
    if not source:
        raise HTTPException(404, "Import not found")
    return Response(
        ingestion.safe_csv(source.raw_csv),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="synthetic-source.csv"'},
    )


@app.get("/runs")
def runs(request: Request, db: DB) -> Response:
    return render(
        request,
        db,
        "Reconciliation runs",
        columns=["Run", "Import", "State", "Rule", "Runtime ms"],
        rows=[
            [
                link(r.id, f"/runs/{r.id}"),
                link(r.import_id, f"/imports/{r.import_id}"),
                r.status,
                r.rule_version,
                r.elapsed_ms,
            ]
            for r in db.scalars(select(Run).order_by(Run.id.desc()).limit(100))
        ],
    )


@app.get("/runs/{run_id}")
def run_detail(request: Request, db: DB, run_id: int) -> Response:
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return render(
        request,
        db,
        f"Run #{run_id} · {run.status}",
        columns=["Payout", "Finding", "Rationale"],
        rows=[
            [link(m.payout_id, f"/payouts/{m.payout_id}"), m.status, m.rationale]
            for m in db.scalars(select(Match).where(Match.run_id == run_id).limit(500))
        ],
    )


@app.get("/payouts")
def payouts(request: Request, db: DB, page: int = 1) -> Response:
    if not 1 <= page <= 10000:
        raise ValueError("Invalid page")
    return render(
        request,
        db,
        "Transactions & payouts",
        page=page,
        paginated=True,
        columns=["Payout", "Currency", "Provider fee", "Declared net", "Settlement (UTC)"],
        rows=[
            [
                link(p.external_id, f"/payouts/{p.id}"),
                p.currency,
                display(p.fee, p.currency),
                display(p.declared_net, p.currency),
                p.settled_at,
            ]
            for p in db.scalars(
                select(Payout).order_by(Payout.id.desc()).offset((page - 1) * 50).limit(50)
            )
        ],
    )


@app.get("/payouts/{payout_id}")
def payout_detail(request: Request, db: DB, payout_id: int) -> Response:
    payout = db.get(Payout, payout_id)
    if not payout:
        raise HTTPException(404, "Payout not found")
    match = db.scalar(select(Match).where(Match.payout_id == payout_id))
    case = db.scalar(select(Case).where(Case.payout_id == payout_id))
    credits = db.scalars(
        select(BankCredit).where(
            BankCredit.import_id == payout.import_id, BankCredit.reference == payout.external_id
        )
    ).all()
    return render(
        request,
        db,
        payout.external_id,
        view="payout",
        payout=payout,
        match=match,
        case=case,
        credits=credits,
        columns=["Payment", "Amount", "Refund"],
        rows=[
            [p.external_id, display(p.amount, payout.currency), display(p.refund, payout.currency)]
            for p in db.scalars(select(Payment).where(Payment.payout_id == payout_id).limit(500))
        ],
    )


@app.get("/exceptions")
def exceptions(request: Request, db: DB) -> Response:
    return render(
        request,
        db,
        "Exceptions",
        columns=["Case", "Payout", "Finding", "State", "Opened (UTC)"],
        rows=[
            [
                link(c.id, f"/exceptions/{c.id}"),
                link(c.payout_id, f"/payouts/{c.payout_id}"),
                c.classification,
                c.status,
                c.created_at,
            ]
            for c in db.scalars(select(Case).order_by(Case.id.desc()).limit(500))
        ],
    )


@app.get("/exceptions/{case_id}")
def case_detail(request: Request, db: DB, case_id: int) -> Response:
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    evidence = ai.evidence_tools(db, case_id)
    return render(
        request,
        db,
        f"Exception #{case.id}",
        view="case",
        case=case,
        evidence=evidence,
        controlled_assessment=controlled.assess(evidence),
        investigations=db.scalars(
            select(Investigation)
            .where(Investigation.case_id == case_id)
            .order_by(Investigation.id.desc())
        ).all(),
        proposals=db.scalars(select(Proposal).where(Proposal.case_id == case_id)).all(),
    )


@app.post("/exceptions/{case_id}/investigate")
def investigate_case(
    request: Request, db: DB, case_id: int, csrf_value: Annotated[str, Form()]
) -> Response:
    user = current_user(request, db)
    require(user, "analyst", "supervisor")
    csrf(request, csrf_value)
    ai.enqueue(db, case_id, user.id)
    db.commit()
    return redirect(f"/exceptions/{case_id}")


@app.post("/exceptions/{case_id}/propose")
def propose(
    request: Request,
    db: DB,
    case_id: int,
    csrf_value: Annotated[str, Form()],
    note: Annotated[str, Form()],
) -> Response:
    user = current_user(request, db)
    csrf(request, csrf_value)
    reviews.propose(db, case_id, user, note)
    db.commit()
    return redirect("/review")


@app.get("/review")
def review(request: Request, db: DB) -> Response:
    current_user(request, db)
    proposals = db.scalars(select(Proposal).order_by(Proposal.id.desc()).limit(100)).all()
    return render(
        request,
        db,
        "Dual-control review",
        view="review",
        proposals=proposals,
        approval_blocks={
            p.id: reviews.approval_block_reason(db, p.case_id)
            for p in proposals
            if p.status == "PENDING"
        },
    )


@app.post("/review/{proposal_id}")
def decision(
    request: Request,
    db: DB,
    proposal_id: int,
    csrf_value: Annotated[str, Form()],
    decision: Annotated[str, Form()],
) -> Response:
    user = current_user(request, db)
    csrf(request, csrf_value)
    reviews.decide(db, proposal_id, user, decision)
    db.commit()
    return redirect("/review")


@app.get("/investigations")
def investigations(request: Request, db: DB) -> Response:
    return render(
        request,
        db,
        "AI investigations",
        columns=["Investigation", "Case", "Mode", "Confidence", "Time (UTC)"],
        rows=[
            [
                i.id,
                link(i.case_id, f"/exceptions/{i.case_id}"),
                i.mode,
                i.report.get("confidence_band", "Controlled contract; uncalibrated"),
                i.created_at,
            ]
            for i in db.scalars(select(Investigation).order_by(Investigation.id.desc()).limit(100))
        ],
    )


@app.get("/reports/operations")
def operations(request: Request, db: DB) -> Response:
    return render(request, db, "Operations report", view="operations", stats=analytics.overview(db))


@app.get("/reports/impact")
def business(
    request: Request,
    db: DB,
    volume: int = 10000,
    minutes: int = 12,
    hourly: int = 15,
    adoption: int = 60,
    automation: int = 50,
    implementation: int = 10000,
    monthly_cost: int = 300,
) -> Response:
    inputs = dict(
        volume=volume,
        minutes=minutes,
        hourly=hourly,
        adoption=adoption,
        automation=automation,
        implementation=implementation,
        monthly_cost=monthly_cost,
    )
    return render(
        request,
        db,
        "Business impact",
        view="impact",
        inputs=inputs,
        projection=analytics.impact(**inputs),
    )


@app.get("/ai/evaluation")
def evaluation(request: Request, db: DB) -> Response:
    return render(
        request,
        db,
        "AI evaluation",
        view="evaluation",
        investigation_visibility=analytics.investigation_visibility(db),
        evaluations=db.scalars(select(Evaluation).order_by(Evaluation.id.desc()).limit(10)).all(),
        columns=[
            "Invocation",
            "Case",
            "Model",
            "Status",
            "Latency ms",
            "Tokens in/out",
            "Est. USD",
        ],
        rows=[
            [
                i.id,
                i.case_id,
                i.model,
                i.status,
                i.latency_ms,
                f"{i.input_tokens}/{i.output_tokens}",
                i.cost_usd,
            ]
            for i in db.scalars(select(Invocation).order_by(Invocation.id.desc()).limit(100))
        ],
    )


@app.get("/ai/evaluation/{evaluation_id}/export")
def export_evaluation(request: Request, db: DB, evaluation_id: int) -> Response:
    """Authenticated synthetic evaluation evidence; never export runtime configuration/secrets."""
    current_user(request, db)
    evaluation = db.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(404, "Evaluation not found")
    return JSONResponse(
        evaluation.results,
        headers={"Content-Disposition": f'attachment; filename="evaluation-{evaluation_id}.json"'},
    )


@app.get("/audit")
def audit(request: Request, db: DB) -> Response:
    return render(
        request,
        db,
        "Audit trail",
        columns=["Event", "Actor ID", "Action", "Entity", "UTC", "Hash prefix"],
        rows=[
            [a.id, a.actor, a.action, a.entity, a.created_at, a.event_hash[:16]]
            for a in db.scalars(select(Audit).order_by(Audit.id.desc()).limit(200))
        ],
    )


@app.get("/operations/health")
def worker_health(request: Request, db: DB) -> Response:
    control = db.get(Control, 1)
    stale = (
        not control
        or not control.worker_heartbeat
        or (now() - control.worker_heartbeat).total_seconds() > 30
    )
    return render(
        request,
        db,
        "Worker health",
        view="health",
        stale=stale,
        control=control,
        columns=["Job", "Kind", "State", "Attempts", "Available (UTC)", "Error"],
        rows=[
            [j.id, j.kind, j.status, j.attempts, j.available_at, j.error or "None"]
            for j in db.scalars(select(Job).order_by(Job.id.desc()).limit(100))
        ],
    )


@app.get("/controls")
def controls(request: Request, db: DB) -> Response:
    return render(
        request,
        db,
        "Configuration & controls",
        view="controls",
        control=db.get(Control, 1),
        providers=db.scalars(select(Provider)).all(),
    )


@app.post("/controls/ai")
def toggle(
    request: Request, db: DB, csrf_value: Annotated[str, Form()], enabled: Annotated[str, Form()]
) -> Response:
    user = current_user(request, db)
    require(user, "admin")
    csrf(request, csrf_value)
    control = db.scalar(select(Control).where(Control.id == 1).with_for_update())
    control.ai_enabled = enabled == "true"
    append(db, user.id, "control.ai_toggled", "ai", enabled=control.ai_enabled)
    db.commit()
    return redirect("/controls")


@app.post("/controls/providers")
def provider(
    request: Request,
    db: DB,
    csrf_value: Annotated[str, Form()],
    name: Annotated[str, Form()],
    fee_bps: Annotated[int, Form()],
    tolerance: Annotated[int, Form()],
) -> Response:
    user = current_user(request, db)
    require(user, "admin")
    csrf(request, csrf_value)
    if not 1 <= len(name) <= 60 or not 0 <= fee_bps <= 10000 or not 0 <= tolerance <= 10000:
        raise ValueError("Invalid provider configuration")
    if db.scalar(select(Provider).where(Provider.name == name)):
        raise ValueError("Create a distinct versioned profile name to preserve historical rules")
    db.add(Provider(name=name, fee_bps=fee_bps, tolerance=tolerance, policy_version="net-v1"))
    append(
        db, user.id, "provider.created", "provider", name=name, fee_bps=fee_bps, tolerance=tolerance
    )
    db.commit()
    return redirect("/controls")


@app.get("/guide")
def guide(request: Request, db: DB) -> Response:
    return render(
        request,
        db,
        "Architecture & 90-day rollout",
        view="guide",
        architecture=Path("docs/architecture.md").read_text(),
        rollout=Path("docs/rollout.md").read_text(),
    )
