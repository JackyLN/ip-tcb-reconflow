"""Anonymous read-only documentation routes; independent of app authentication and database."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from reconflow.services.public_docs import catalog, render

router = APIRouter(prefix="/docs", include_in_schema=False)
templates = Jinja2Templates(directory="reconflow/templates")


@router.get("")
def docs_redirect() -> RedirectResponse:
    return RedirectResponse("/docs/", status_code=308)


@router.get("/")
@router.get("/{slug:path}")
def documentation(request: Request, slug: str = "") -> HTMLResponse:
    """Serve only catalogued Markdown from public-docs; no caller-controlled filesystem path."""
    published = catalog()
    document = published.by_slug(slug.strip("/"))
    if not document:
        raise HTTPException(404, "Public document not found")
    content, headings = render(document, published)
    position = published.ordered.index(document)
    return templates.TemplateResponse(
        request=request,
        name="docs.html",
        context={
            "title": document.title,
            "document": document,
            "content": content,
            "headings": headings,
            "navigation": published.navigation,
            "documents": published.ordered,
            "is_home": not document.slug,
            "previous": published.ordered[position - 1] if position else None,
            "next": published.ordered[position + 1]
            if position + 1 < len(published.ordered)
            else None,
        },
    )
