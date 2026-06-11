# Visual Polish: Upbuild Brand Alignment

**Date:** 2026-06-11
**Scope:** Visual/CSS polish only — no structural or behavioral changes
**Status:** Approved

---

## Overview

Apply Upbuild's brand identity (deep purple/indigo `#5E328C`, minimalist sans-serif, calm/contemplative "spiritual + professional" feel, generous white space, understated buttons — per upbuild.com) to the Streamlit app's existing layout. The app's structure, form flow, and program order remain unchanged; only colors, typography, spacing, and section grouping are refined.

---

## Theme Colors (`.streamlit/config.toml`)

| Key | Old | New |
|---|---|---|
| `primaryColor` | `#5E328C` | `#5E328C` (unchanged) |
| `backgroundColor` | `#FFFFFF` | `#FFFFFF` (unchanged) |
| `secondaryBackgroundColor` | `#F5F0FA` | `#F7F5F1` (warm off-white/cream) |
| `textColor` | `#1E1E1E` | `#2B2B2B` (softer near-black) |
| `font` | `sans serif` | `sans serif` (unchanged; "Inter" applied via custom CSS for refinement) |

---

## New File: `ui/styles.py`

A single function `inject_custom_css() -> None` that calls `st.markdown(<style>...</style>, unsafe_allow_html=True)` once. Contents:

1. **Font import**: Google Fonts "Inter" (400/500/600/700 weights), applied to `.stApp` and headers via `font-family: 'Inter', sans-serif`.
2. **Header styling**: Larger `<h1>` (≈2.25rem, slightly tightened letter-spacing), with a thin (`2px`) horizontal rule in `#5E328C` beneath the logo/title area.
3. **Card containers**: CSS targeting Streamlit's bordered containers (`st.container(border=True)` renders as `div[data-testid="stVerticalBlockBorderWrapper"]` with a border) — override to `border-radius: 12px`, soft `box-shadow: 0 1px 4px rgba(0,0,0,0.06)`, white background, `padding: 1.5rem`, and `margin-bottom: 1.25rem`.
4. **Buttons**: `border-radius: 8px` on all `button` elements; primary buttons (`kind="primary"`) filled `#5E328C` with white text and a `:hover` state ~10% darker (`#4D2A75`); secondary buttons/radios remain understated (existing Streamlit defaults with rounded corners only).
5. **Section spacing**: increase gap between top-level blocks in the main content area for a more spacious rhythm (`section.main > div { gap: 1.5rem; }` or equivalent block-container margin).
6. **Inputs**: `border-radius: 8px` on text inputs, number inputs, selectboxes, and text areas.

---

## Layout Changes (`app.py`)

Call `inject_custom_css()` once near the top of `app.py` (after `st.set_page_config`, before rendering any widgets).

Wrap the following existing sections in `st.container(border=True)` — purely a visual grouping change, no reordering, no new steps, no logic changes:

1. **Program & date selection**: program selectbox + session date input
2. **Video source**: source-type radio + file uploader / Drive link input
3. **Program-specific form**: the `FORM_RENDERERS[...]` call and its rendered output (title preview included)
4. **Upload action**: the "Upload to YouTube" button and result/error messages

Each section becomes:
```python
with st.container(border=True):
    # existing widgets for that section, unchanged
```

The header (logo + title) stays outside any card, styled per the "Header styling" rule above.

---

## Out of Scope

- No changes to form logic, validation, AI generation flows, or pipeline behavior.
- No new dependencies (Inter is loaded via CDN `<link>`/`@import` in the injected CSS, no Python package).
- No changes to program-specific form internals (`ui/forms.py` renderers) beyond what's already wrapped by the new `app.py` containers — individual widgets within a renderer are not individually re-styled beyond the global input/button CSS rules.

---

## Testing

- Existing test suite (`pytest -q tests/`) must continue to pass unchanged — this is a CSS/layout-only change with no testable logic.
- Manual smoke test: run the app locally, verify each program (RWWA, Morning Rounds, CTA, etc.) renders within styled cards, buttons/inputs show updated styling, header displays the purple rule, and the full upload flow still works end-to-end (or at least renders without errors, since a full upload requires real credentials/video).
