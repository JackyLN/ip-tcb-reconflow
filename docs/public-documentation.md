# Public documentation publishing

The application serves `/docs/` anonymously from the dedicated repository directory `public-docs/`.
`docs/` remains internal development/operations documentation; there is no generic file-reading route.

Authors add Markdown below the public root, with `index.md` for section overviews and optional
reading order in `navigation.json`. Discovery includes all non-hidden `.md` files automatically,
including nested folders without index pages. Symlinks and duplicate canonical URLs are rejected
or excluded. Relative Markdown links become public URLs, and publication validation checks page
and heading targets. Assets are limited to the separate `public-docs/assets/` static mount.

The curated public subset includes product/workflow, framing/discovery/business case, architecture,
security boundaries, ADRs, AI/evaluation and rollout/adoption. It carries original synthetic,
assumption, simulation, proposal and unimplemented labels. Internal deployment addresses, root
access instructions, generated accounts/passwords and environment files are not mirrored.
The public tree is reviewed content, not an automatic copy of internal docs; maintainers update
public counterparts when changing shared facts or decisions.

Rendering uses markdown-it-py with raw HTML disabled, standard safe-URL validation, tables,
strikethrough, heading IDs, task lists and footnotes; Pygments highlights fenced code. Mermaid is
bundled from pinned npm dependencies and loaded lazily only for diagrams. Strict mode is enforced;
server-side Markdown does not execute HTML or scripts. Selected generated SVG styling requires
inline style support: this CSP exception applies only to `/docs` and `/docs/…`, never app actions.
JavaScript remains self-only with no unsafe-eval. Diagram source is preserved as a fallback.
Hashed local JS chunks use immutable cache headers; the entry script/content revalidates or reloads.

Checks: `make docs-check`, `make lint test`, `npm run check`, `npm run build`, `npm run docs:browser`.
The docs browser check is anonymous/read-only and supports DOCS_BASE_URL for a deployed origin;
it performs no model calls. The operations smoke queues investigations, so run it only in a no-key
sandbox unless live inference was explicitly authorized. See verification.md for observed results.

References: https://markdown-it-py.readthedocs.io/en/latest/using.html and
https://mermaid.js.org/config/usage.html .


A constrained `video` fence accepts one reviewed local public MP4 path and emits a native player;
raw Markdown HTML stays disabled. The existing static mount serves byte ranges for seeking.
The recorded-demo README and versioned video live under public-docs/product and assets/demo.
Video docs are read-only; playing this recording never queues provider inference.
