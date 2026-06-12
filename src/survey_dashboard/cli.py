"""
survey-dashboard CLI
====================

Build and optionally serve an interactive HTML analytics dashboard
from two survey CSV files.

Commands
--------
  build   Merge CSVs and write a self-contained HTML file.
  serve   Merge CSVs, write a temporary HTML file, and open it in the browser.
  json    Merge CSVs and write the combined JSON data file only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import webbrowser
from pathlib import Path

from .merge import merge
from .template import build_html


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_files(*paths: str) -> None:
    for p in paths:
        if not Path(p).exists():
            print(f"[ERROR] File not found: {p}", file=sys.stderr)
            sys.exit(1)


def _write_json(records: list[dict], output: str) -> None:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"[OK] JSON  → {out}  ({len(records)} records)")


def _write_html(records: list[dict], output: str) -> None:
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    html = build_html(records)
    out.write_text(html, encoding="utf-8")
    print(f"[OK] HTML  → {out}  ({len(records)} records embedded)")


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------

def cmd_build(args: argparse.Namespace) -> None:
    """Merge CSVs → self-contained HTML dashboard."""
    _require_files(args.structured, args.freetext)
    records = merge(args.structured, args.freetext)
    _write_html(records, args.output)
    if args.open:
        webbrowser.open(Path(args.output).resolve().as_uri())


def cmd_serve(args: argparse.Namespace) -> None:
    """
    Merge CSVs → temporary HTML file → open in browser.
    No web server required; the page is entirely self-contained.
    """
    _require_files(args.structured, args.freetext)
    records = merge(args.structured, args.freetext)
    html = build_html(records)

    # Write to a temp file that persists until the user closes the terminal
    tmp = tempfile.NamedTemporaryFile(
        suffix=".html", prefix="survey_dashboard_", delete=False, mode="w", encoding="utf-8"
    )
    tmp.write(html)
    tmp.flush()

    uri = Path(tmp.name).resolve().as_uri()
    print(f"[OK] Dashboard written to {tmp.name}")
    print(f"     Opening in browser…")
    webbrowser.open(uri)


def cmd_json(args: argparse.Namespace) -> None:
    """Merge CSVs → survey_data.json (for use with a separate web server)."""
    _require_files(args.structured, args.freetext)
    records = merge(args.structured, args.freetext)
    _write_json(records, args.output)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="survey-dashboard",
        description=(
            "Generate an interactive HTML analytics dashboard from two survey CSV files.\n\n"
            "The dashboard includes bar/donut charts for all 15 survey questions, "
            "cross-tab cohort filtering, sentiment analysis, word clouds, and a comment miner."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="survey-dashboard 0.1.0")

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # --- build ---
    p_build = sub.add_parser(
        "build",
        help="Merge CSVs and write a self-contained HTML dashboard file.",
        description="Merge the two CSV files and write a single HTML file that can be opened directly in any browser with no server required.",
    )
    p_build.add_argument("--structured", "-s", required=True, metavar="PATH",
                         help="Path to the structured responses CSV (one row per respondent, coded answers).")
    p_build.add_argument("--freetext", "-f", required=True, metavar="PATH",
                         help="Path to the free-text responses CSV (same row order, open-ended answers).")
    p_build.add_argument("--output", "-o", default="dashboard.html", metavar="PATH",
                         help="Output HTML file path. Default: dashboard.html")
    p_build.add_argument("--open", action="store_true",
                         help="Open the generated dashboard in the default browser after building.")
    p_build.set_defaults(func=cmd_build)

    # --- serve ---
    p_serve = sub.add_parser(
        "serve",
        help="Merge CSVs and immediately open the dashboard in your browser.",
        description="Merge the two CSV files, write the dashboard to a temporary file, and open it in the default browser. No web server is started.",
    )
    p_serve.add_argument("--structured", "-s", required=True, metavar="PATH",
                         help="Path to the structured responses CSV.")
    p_serve.add_argument("--freetext", "-f", required=True, metavar="PATH",
                         help="Path to the free-text responses CSV.")
    p_serve.set_defaults(func=cmd_serve)

    # --- json ---
    p_json = sub.add_parser(
        "json",
        help="Merge CSVs and write survey_data.json only (for custom deployments).",
        description="Merge the two CSV files and write only the combined JSON data. Useful if you want to host the dashboard HTML yourself and load data via a server.",
    )
    p_json.add_argument("--structured", "-s", required=True, metavar="PATH",
                        help="Path to the structured responses CSV.")
    p_json.add_argument("--freetext", "-f", required=True, metavar="PATH",
                        help="Path to the free-text responses CSV.")
    p_json.add_argument("--output", "-o", default="survey_data.json", metavar="PATH",
                        help="Output JSON file path. Default: survey_data.json")
    p_json.set_defaults(func=cmd_json)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
