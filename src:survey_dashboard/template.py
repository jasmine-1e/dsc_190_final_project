"""
Build the self-contained dashboard HTML by injecting survey data directly
into the page so it works without a web server (open as a local file).
"""

from __future__ import annotations

import importlib.resources
import json
from pathlib import Path


# The marker we'll search for inside the template HTML
_DATA_PLACEHOLDER = "// __SURVEY_DATA_PLACEHOLDER__"

# The network-fetch block we replace with inline data
_FETCH_BLOCK = """\
window.addEventListener('DOMContentLoaded', async () => {
  await loadSystemWorkspace();
});

async function loadSystemWorkspace() {
  try {
    const path = 'survey_data.json';
    const resp = await fetch(path);
    if (!resp.ok) throw new Error('Network JSON fetch target failed');
    ALL_DATA = await resp.json();
    initializeApplicationStudio();
  } catch(e) {
    console.error('Error loading JSON data file:', e);
    document.getElementById('row-count').textContent = 'Error loading survey data source configuration.';
  }
}"""

_INLINE_BLOCK_TEMPLATE = """\
// Data embedded at build time — no server required
ALL_DATA = {json_data};
window.addEventListener('DOMContentLoaded', () => {{
  initializeApplicationStudio();
}});"""


def _get_template_html() -> str:
    """Load the bundled dashboard HTML template."""
    try:
        # Python 3.9+ importlib.resources API
        ref = importlib.resources.files("survey_dashboard").joinpath("dashboard_template.html")
        return ref.read_text(encoding="utf-8")
    except Exception:
        # Fallback: look next to this file
        here = Path(__file__).parent
        return (here / "dashboard_template.html").read_text(encoding="utf-8")


def build_html(records: list[dict]) -> str:
    """
    Return a self-contained HTML string with ``records`` embedded as inline JS.

    The template's network-fetch boot block is replaced with a synchronous
    assignment so the page loads from ``file://`` without CORS errors.
    """
    template = _get_template_html()

    json_data = json.dumps(records, ensure_ascii=False)
    inline_block = _INLINE_BLOCK_TEMPLATE.format(json_data=json_data)

    if _FETCH_BLOCK in template:
        html = template.replace(_FETCH_BLOCK, inline_block)
    else:
        # Fallback: inject after the ALL_DATA declaration
        html = template.replace(
            "let ALL_DATA = [];",
            f"let ALL_DATA = [];\n{inline_block}",
            1,
        )

    return html
