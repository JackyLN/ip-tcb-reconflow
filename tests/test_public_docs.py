"""Public publishing boundary, Markdown features, link integrity and anonymous HTTP access."""

import pytest

from reconflow.services.public_docs import catalog, parser, validate


def test_all_published_pages_render_anonymously(client):
    published = catalog()
    assert validate() == len(published.documents) >= 20
    response = client.get("/docs", follow_redirects=False)
    assert response.status_code == 308 and response.headers["location"] == "/docs/"
    for page in published.ordered:
        response = client.get(page.url)
        assert response.status_code == 200, page.url
        assert page.title in response.text
        assert 'aria-label="Documentation"' in response.text
        assert "/login" not in str(response.url)
    assert "Read the public documentation" in client.get("/login").text


def test_public_reader_does_not_access_database(client, monkeypatch):
    import reconflow.main

    def deny_database():
        raise AssertionError("Public docs must not access authentication/database")

    monkeypatch.setattr(reconflow.main, "SessionLocal", deny_database)
    assert client.get("/docs/engineering/").status_code == 200


@pytest.mark.parametrize(
    "url",
    [
        "/docs/deployment/",
        "/docs/deployment-shared-vps/",
        "/docs/.env.production/",
        "/docs/engineering/%2e%2e/%2e%2e/docs/security.md",
        "/docs/navigation.json",
        "/docs-assets/../.env.production",
        "/docs/README.md",
    ],
)
def test_unpublished_paths_are_not_served(client, url):
    assert client.get(url, follow_redirects=False).status_code == 404


def test_nested_navigation_links_toc_and_previous_next(client):
    response = client.get("/docs/engineering/decisions/004-demo-llm-selection/")
    assert response.status_code == 200
    assert "/docs/ai/evaluation/" in response.text
    assert "/docs/engineering/decisions/002-deterministic-financial-truth/" in response.text
    assert 'aria-label="Adjacent documents"' in response.text
    assert 'href="#decision-and-rationale"' in response.text
    assert '<pre><code class="language-dotenv">' in response.text
    assert '<div class="docs-search' not in response.text  # no untrusted HTML search output


def test_rich_markdown_and_script_rejection():
    html = parser().render("""# A heading

| Column | Value |
| --- | --- |
| good | **yes** |

- [x] Checked

A footnote.[^note]

[^note]: Details.

<script>alert(1)</script>

[unsafe](javascript:alert(1))

```python
print("<script>")
```

```mermaid
flowchart LR
  A --> B
```
""")
    assert "<table>" in html and "task-list-item-checkbox" in html
    assert "footnote" in html and 'id="a-heading"' in html
    assert "<script>" not in html and 'href="javascript:' not in html
    assert "language-mermaid" in html and "language-python" in html


def test_new_nested_page_discovery_and_no_symlink_exposure(tmp_path):
    (tmp_path / "index.md").write_text("# Handbook\n")
    nested = tmp_path / "new-section" / "nested"
    nested.mkdir(parents=True)
    (nested / "new.md").write_text("# Automatically discovered\n")
    secret = tmp_path.parent / "private-publication-test.md"
    secret.write_text("# PRIVATE SHOULD NOT BE PUBLISHED\n")
    (tmp_path / "leak.md").symlink_to(secret)
    published = catalog(tmp_path)
    assert published.by_slug("new-section/nested/new").title == "Automatically discovered"
    assert published.by_slug("leak") is None
    assert validate(tmp_path) == 2
    secret.unlink()


def test_broken_or_private_relative_link_fails_publication(tmp_path):
    (tmp_path / "index.md").write_text("# Home\n[Internal](../docs/deployment.md)\n")
    with pytest.raises(ValueError, match="Broken public Markdown link"):
        validate(tmp_path)


def test_duplicate_url_rejected(tmp_path):
    (tmp_path / "index.md").write_text("# Home")
    (tmp_path / "same.md").write_text("# A")
    (tmp_path / "same").mkdir()
    (tmp_path / "same" / "index.md").write_text("# B")
    with pytest.raises(ValueError, match="conflicting URLs"):
        catalog(tmp_path)


def test_broken_heading_detected(tmp_path):
    (tmp_path / "index.md").write_text("# Home\n[Missing](#missing)")
    with pytest.raises(ValueError, match="Broken public heading"):
        validate(tmp_path)


def test_public_csp_is_scoped_and_assets_are_local(client):
    public = client.get("/docs/")
    login = client.get("/login")
    assert "style-src 'self' 'unsafe-inline'" in public.headers["content-security-policy"]
    assert "script-src 'self';" in public.headers["content-security-policy"]
    assert "unsafe-eval" not in public.headers["content-security-policy"]
    assert "unsafe-inline" not in login.headers["content-security-policy"]
    assert 'src="/static/docs.js"' in public.text
    asset = client.get("/docs-assets/reading-flow.svg")
    assert asset.status_code == 200 and asset.headers["content-type"].startswith("image/svg+xml")


def test_document_size_limit(tmp_path):
    (tmp_path / "index.md").write_text("# Home\n" + "a" * 256001)
    with pytest.raises(ValueError, match="size limit"):
        catalog(tmp_path)


def test_public_video_player_and_range_download(client):
    response = client.get("/docs/product/recorded-demo/")
    assert response.status_code == 200
    assert '<video controls playsinline preload="metadata"' in response.text
    assert 'type="video/mp4"' in response.text
    assert "0.00339525" in response.text and "NOT MEASURED" in response.text
    assert "0.05484750" in response.text and "controlled-v2-results-walkthrough" in response.text
    for filename in ["reconflow-live-demo.mp4", "reconflow-controlled-v2-demo.mp4"]:
        response = client.get(f"/docs-assets/demo/{filename}", headers={"Range": "bytes=0-31"})
        assert response.status_code == 206
        assert response.headers["content-type"] == "video/mp4"
        assert len(response.content) == 32


@pytest.mark.parametrize("source", ["https://example.com/video.mp4", "/login", "assets/a.svg"])
def test_video_fence_rejects_nonlocal_or_nonvideo_sources(tmp_path, source):
    (tmp_path / "index.md").write_text(f"# Home\n```video\n{source}\n```\n")
    with pytest.raises(ValueError, match="Video fences"):
        validate(tmp_path)


def test_video_fence_rejects_missing_asset(tmp_path):
    (tmp_path / "index.md").write_text("# Home\n```video\nassets/missing.mp4\n```\n")
    with pytest.raises(ValueError, match="Missing public documentation asset"):
        validate(tmp_path)
