"""Discover and render only explicitly published Markdown; never traverse the repository."""

from __future__ import annotations

import json
import posixpath
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from html import escape
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit, urlunsplit

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

PUBLIC_ROOT = Path(__file__).resolve().parents[2] / "public-docs"
MAX_DOCUMENT_BYTES = 256_000


@dataclass(frozen=True)
class Document:
    path: str
    title: str
    source: str

    @property
    def slug(self) -> str:
        parts = PurePosixPath(self.path)
        return (
            str(parts.parent)
            if parts.name == "index.md" and str(parts.parent) != "."
            else ("" if self.path == "index.md" else str(parts.with_suffix("")))
        )

    @property
    def url(self) -> str:
        return "/docs/" + (self.slug + "/" if self.slug else "")


@dataclass
class Navigation:
    title: str
    url: str | None = None
    children: list[Navigation] = field(default_factory=list)
    prefix: str = ""


@dataclass
class Catalog:
    documents: dict[str, Document]
    navigation: list[Navigation]
    ordered: list[Document]

    def by_slug(self, slug: str) -> Document | None:
        return next((doc for doc in self.ordered if doc.slug == slug), None)


def _title(source: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*#*\s*$", source, re.MULTILINE)
    return match.group(1) if match else fallback.replace("-", " ").title()


def catalog(root: Path = PUBLIC_ROOT) -> Catalog:
    """Every non-hidden .md file below this dedicated root is intentionally public."""
    root = root.resolve()
    documents: dict[str, Document] = {}
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        # Refuse symlinks, including a parent directory linked outside the publication root.
        if path.is_symlink() or path.resolve() != root.joinpath(relative):
            continue
        if path.stat().st_size > MAX_DOCUMENT_BYTES:
            raise ValueError("Published Markdown exceeds the document size limit")
        source = path.read_text(encoding="utf-8")
        key = relative.as_posix()
        documents[key] = Document(key, _title(source, path.stem), source)
    config_path = root / "navigation.json"
    config = json.loads(config_path.read_text()) if config_path.is_file() else {}
    order = {path: rank for rank, path in enumerate(config.get("order", []))}
    ordered: list[Document] = []

    def position(path: str) -> tuple[int, str]:
        return order.get(path, len(order)), path

    def children(directory: str) -> list[Navigation]:
        prefix = directory + "/" if directory else ""
        direct = [
            doc
            for key, doc in documents.items()
            if str(PurePosixPath(key).parent) == (directory or ".")
        ]
        folders = {
            key[len(prefix) :].split("/")[0]
            for key in documents
            if key.startswith(prefix) and "/" in key[len(prefix) :]
        }
        entries = [(doc.path, doc) for doc in direct if PurePosixPath(doc.path).name != "index.md"]
        entries += [(prefix + folder + "/index.md", folder) for folder in folders]
        result = []
        for path, item in sorted(entries, key=lambda entry: position(entry[0])):
            if isinstance(item, Document):
                ordered.append(item)
                result.append(Navigation(item.title, item.url))
            else:
                index = documents.get(path)
                if index:
                    ordered.append(index)
                result.append(
                    Navigation(
                        index.title if index else item.replace("-", " ").title(),
                        index.url if index else None,
                        children(prefix + item),
                        prefix + item + "/",
                    )
                )
        return result

    home = documents.get("index.md")
    if home:
        ordered.append(home)
    navigation = ([Navigation(home.title, home.url)] if home else []) + children("")
    if len({doc.slug for doc in ordered}) != len(ordered):
        raise ValueError("Published documents have conflicting URLs")
    return Catalog(documents, navigation, ordered)


def _highlight(code: str, language: str, _attrs: str) -> str:
    try:
        lexer = get_lexer_by_name(language) if language else None
    except ClassNotFound:
        lexer = None
    return highlight(code, lexer, HtmlFormatter(nowrap=True)) if lexer else escape(code)


def parser() -> MarkdownIt:
    """Raw HTML is escaped; default link validation rejects script URLs."""
    return (
        MarkdownIt("commonmark", {"html": False, "highlight": _highlight})
        .enable(["table", "strikethrough"])
        .use(anchors_plugin, min_level=1, max_level=4)
        .use(footnote_plugin)
        .use(tasklists_plugin)
    )


def _tokens(tokens: list[Token]) -> Iterator[Token]:
    for token in tokens:
        yield token
        if token.children:
            yield from _tokens(token.children)


def local_link(href: str, document: Document, published: Catalog) -> str:
    """Resolve Markdown sibling/parent links to public routes, never to private files."""
    url = urlsplit(href)
    if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
        return href
    target = posixpath.normpath(
        posixpath.join(str(PurePosixPath(document.path).parent), unquote(url.path))
    )
    if url.path.endswith(".md") or url.path.endswith("/"):
        if not target.endswith(".md"):
            target = target.rstrip("/") + "/index.md"
        destination = published.documents.get(target)
        if not destination:
            raise ValueError(f"Broken public Markdown link in {document.path}: {url.path}")
        return urlunsplit(("", "", destination.url, url.query, url.fragment))
    if target.startswith("assets/"):
        return urlunsplit(("", "", "/docs-assets/" + target[7:], url.query, url.fragment))
    raise ValueError(f"Unsupported relative public link in {document.path}: {url.path}")


def video_url(source: str, document: Document, published: Catalog) -> str:
    """Accept only one local MP4 asset; never arbitrary HTML, embeds or remote media."""
    href = local_link(source.strip(), document, published)
    url = urlsplit(href)
    if (
        url.scheme
        or url.netloc
        or url.query
        or url.fragment
        or not url.path.startswith("/docs-assets/")
        or not url.path.endswith(".mp4")
        or len(source.strip().splitlines()) != 1
    ):
        raise ValueError("Video fences require a single local public MP4 asset")
    return href


def render(document: Document, published: Catalog) -> tuple[str, list[dict[str, str]]]:
    """Render one page with stable heading IDs and rewritten public cross-document links."""
    md = parser()
    default_fence = md.renderer.rules["fence"]

    def fence(tokens: list[Token], index: int, options: dict, env: dict) -> str:
        token = tokens[index]
        if token.info.strip() != "video":
            return default_fence(tokens, index, options, env)
        src = escape(video_url(token.content, document, published), quote=True)
        return (
            '<figure class="docs-video"><video controls playsinline preload="metadata" '
            'aria-label="Public documentation video">'
            f'<source src="{src}" type="video/mp4">'
            f'Your browser cannot play this video. <a href="{src}">Download the MP4</a>.'
            "</video><figcaption>Use the player controls to play, pause and seek."
            "</figcaption></figure>\n"
        )

    md.renderer.rules["fence"] = fence
    environment: dict = {}
    tokens = md.parse(document.source, environment)
    headings = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag in ("h2", "h3"):
            headings.append(
                {
                    "id": token.attrGet("id") or "",
                    "level": token.tag,
                    "title": tokens[index + 1].content,
                }
            )
    for token in _tokens(tokens):
        if token.type == "link_open":
            token.attrSet("href", local_link(token.attrGet("href") or "", document, published))
        elif token.type == "image":
            token.attrSet("src", local_link(token.attrGet("src") or "", document, published))
    return md.renderer.render(tokens, md.options, environment), headings


def validate(root: Path = PUBLIC_ROOT) -> int:
    """Publication gate: render every page and check document links and fragment targets."""
    published = catalog(root)
    if "index.md" not in published.documents:
        raise ValueError("Public documentation needs index.md")
    for document in published.ordered:
        render(document, published)
        for token in _tokens(parser().parse(document.source)):
            if token.type == "fence" and token.info.strip() == "video":
                rewritten = video_url(token.content, document, published)
            elif token.type in ("link_open", "image"):
                raw = token.attrGet("href" if token.type == "link_open" else "src") or ""
                rewritten = local_link(raw, document, published)
            else:
                continue
            url = urlsplit(rewritten)
            if url.path.startswith("/docs-assets/"):
                asset = root / "assets" / unquote(url.path.removeprefix("/docs-assets/"))
                if not asset.is_file() or not asset.resolve().is_relative_to(
                    (root / "assets").resolve()
                ):
                    raise ValueError("Missing public documentation asset")
            if not url.fragment or url.scheme or url.netloc:
                continue
            destination = (
                document
                if not url.path
                else published.by_slug(url.path.removeprefix("/docs/").strip("/"))
            )
            if destination:
                ids = {
                    t.attrGet("id")
                    for t in parser().parse(destination.source)
                    if t.type == "heading_open"
                }
                if unquote(url.fragment) not in ids:
                    raise ValueError(f"Broken public heading link in {document.path}")
    return len(published.ordered)
