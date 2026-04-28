# Browser QA - CivicNotice v0.1.1 Alignment

Date: 2026-04-28

Scope:

- `docs/index.html`
- Public sample UI rendered from `civicnotice.public_ui.render_public_lookup_page()`

Evidence:

- Docs desktop: `docs/browser-qa-civicnotice-v0.1.1-alignment-desktop.png`
- Docs mobile: `docs/browser-qa-civicnotice-v0.1.1-alignment-mobile.png`
- Public UI desktop: `docs/browser-qa-civicnotice-public-ui-v0.1.1-desktop.png`
- Public UI mobile: `docs/browser-qa-civicnotice-public-ui-v0.1.1-mobile.png`

Checks:

- Version labels show `v0.1.1`.
- Dependency copy names `civiccore==0.3.0`.
- Public UI boundary copy still states CivicNotice does not determine legal sufficiency, publish official notices, provide legal advice, call live LLMs, write back to publication systems, or replace the notice system of record.
- Desktop and mobile captures report no horizontal overflow (`scrollWidth == innerWidth`) in both docs and public UI.

Result: PASS.
