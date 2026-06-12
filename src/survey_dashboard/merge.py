"""Merge structured + free-text survey CSVs into a list of record dicts."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Column maps — structured CSV header  →  JSON key
# Adjust if your real CSV headers differ from these defaults.
# ---------------------------------------------------------------------------

STRUCTURED_COL_MAP: dict[str, str] = {
    "org_type":                    "org_type",
    "role":                        "role",
    "aware_paymentworks":          "aware_paymentworks",
    "paymentworks_actions":        "paymentworks_actions",
    "paymentworks_difficulties":   "paymentworks_difficulties",
    "paymentworks_support_source": "paymentworks_support_source",
    "aware_transcepta":            "aware_transcepta",
    "invoice_submission_method":   "invoice_submission_method",
    "transcepta_interactions":     "transcepta_interactions",
    "transcepta_difficulties":     "transcepta_difficulties",
    "transcepta_support_source":   "transcepta_support_source",
    "ipps_resources_aware":        "ipps_resources_aware",
    "ipps_difficulties":           "ipps_difficulties",
    "po_clarity_rating":           "po_clarity_rating",
    "aware_po_nonpayment":         "aware_po_nonpayment",
}

FREETEXT_COL_MAP: dict[str, str] = {
    "org_type_other":                 "org_type_other",
    "role_other":                     "role_other",
    "paymentworks_actions_text":      "paymentworks_actions_text",
    "paymentworks_difficulties_text": "paymentworks_difficulties_text",
    "paymentworks_support_other":     "paymentworks_support_other",
    "paymentworks_issues_open":       "paymentworks_issues_open",
    "invoice_submission_other":       "invoice_submission_other",
    "transcepta_interactions_text":   "transcepta_interactions_text",
    "transcepta_difficulties_text":   "transcepta_difficulties_text",
    "transcepta_support_other":       "transcepta_support_other",
    "transcepta_issues_open":         "transcepta_issues_open",
    "ipps_resources_other":           "ipps_resources_other",
    "ipps_difficulties_other":        "ipps_difficulties_other",
    "po_clarity_text":                "po_clarity_text",
    "suggestions_open":               "suggestions_open",
}


def _read_csv(path: str | Path) -> list[dict]:
    """Read a CSV file, stripping UTF-8 BOM if present."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _remap_row(row: dict, col_map: dict[str, str]) -> dict[str, str]:
    """Map one CSV row to JSON keys, case-insensitively."""
    out: dict[str, str] = {}
    # Build a lowercase-keyed lookup of the raw row
    lower_row = {k.strip().lower(): v for k, v in row.items()}
    for csv_col, json_key in col_map.items():
        out[json_key] = lower_row.get(csv_col.lower(), "").strip()
    return out


def merge(structured_path: str | Path, freetext_path: str | Path) -> list[dict]:
    """
    Merge structured and free-text CSV files row-by-row.

    Returns a list of combined record dicts ready to be serialised as JSON.
    If the two files have different row counts a warning is printed to stderr
    and the shorter length is used.
    """
    structured_rows = _read_csv(structured_path)
    freetext_rows   = _read_csv(freetext_path)

    if len(structured_rows) != len(freetext_rows):
        print(
            f"[WARNING] Row count mismatch: "
            f"structured={len(structured_rows)}, freetext={len(freetext_rows)}. "
            f"Using min({len(structured_rows)}, {len(freetext_rows)}) rows.",
            file=sys.stderr,
        )

    records: list[dict] = []
    for i, s_row in enumerate(structured_rows):
        record = _remap_row(s_row, STRUCTURED_COL_MAP)
        if i < len(freetext_rows):
            record.update(_remap_row(freetext_rows[i], FREETEXT_COL_MAP))
        records.append(record)

    return records
