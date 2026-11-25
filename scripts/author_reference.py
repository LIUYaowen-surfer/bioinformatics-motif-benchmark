#!/usr/bin/env python3
"""Rebuild task_01/reference.json and task_02/reference.json from author files.

Only published author results are read.  No motif analysis is re-run.

Internal audited extraction helpers. Use scripts/extract_reference.py in this repository.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = ROOT / "downloads"
MANIFEST = DOWNLOADS / "manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_info(rel: str, path: Path) -> dict:
    info = {"file": rel, "sha256": sha256(path), "size": path.stat().st_size}
    if MANIFEST.exists():
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            rec = manifest.get(rel, {})
            if "url" in rec:
                info["url"] = rec["url"]
        except json.JSONDecodeError:
            pass
    return info


def number(value):
    """Convert author spreadsheet numbers to JSON numbers; keep None as None."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip().lstrip("<")
    try:
        return float(text)
    except ValueError:
        return None


def build_hydra_reference() -> dict:
    rel = "hydra/elife-60562-supp3-v2.xlsx"
    path = DOWNLOADS / rel
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet_name = "3hpa HOMER Enrichment"
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Expected worksheet missing: {sheet_name}; got {wb.sheetnames}")
    ws = wb[sheet_name]
    rows = ws.iter_rows(values_only=True)
    header = list(next(rows))
    expected = [
        "Motif Name", "Consensus", "P-value", "Log P-value",
        "q-value (Benjamini)",
    ]
    for col in expected:
        if col not in header:
            raise ValueError(f"Missing expected column {col!r} in {sheet_name}: {header}")

    idx = {name: i for i, name in enumerate(header)}
    motifs = []
    for row_no, row in enumerate(rows, start=2):
        if not row or row[idx["Motif Name"]] in (None, ""):
            continue
        name = str(row[idx["Motif Name"]]).strip()
        motifs.append(
            {
                "rank": len(motifs) + 1,
                "motif_id": name,
                "motif_name": name,
                "consensus": row[idx["Consensus"]],
                "p_value": number(row[idx["P-value"]]),
                "log_p_value": number(row[idx["Log P-value"]]),
                "q_value": number(row[idx["q-value (Benjamini)"]]),
                "target_sequences_with_motif": number(
                    row[idx["# of Target Sequences with Motif(of 2183)"]]
                ),
                "pct_target_sequences_with_motif": number(
                    row[idx["% of Target Sequences with Motif"]]
                ),
                "background_sequences_with_motif": number(
                    row[idx["# of Background Sequences with Motif(of 32333)"]]
                ),
                "pct_background_sequences_with_motif": number(
                    row[idx["% of Background Sequences with Motif"]]
                ),
                "source_worksheet": sheet_name,
                "source_row": row_no,
                "source_columns": list(header),
            }
        )
    wb.close()

    p_values = [m["p_value"] for m in motifs]
    if any(p is None for p in p_values):
        raise ValueError("Hydra HOMER sheet contains rows without a P-value")
    if p_values != sorted(p_values):
        raise ValueError("Hydra HOMER rows are not in author P-value order")

    duplicate_names = sorted(
        {m["motif_id"] for m in motifs if sum(x["motif_id"] == m["motif_id"] for x in motifs) > 1}
    )
    return {
        "task_id": "task_01",
        "analysis": "HOMER known-motif enrichment, untreated 3 hpa opening peaks",
        "source": source_info(rel, path),
        "source_worksheet": sheet_name,
        "excluded_worksheets": ["chromVAR Variability Scores"],
        "ranking_metric": "P-value (ascending, author worksheet order)",
        "target_sequence_count_reported_by_author": 2183,
        "background_sequence_count_reported_by_author": 32333,
        "notes": [
            "The worksheet contains two rows with the same motif name but different consensus sequences; both are retained as separate author results.",
            "No separate motif-ID column exists in the author file; the full HOMER motif name is used as motif_id and motif_name.",
            "The worksheet is ordered by ascending P-value; rank is the author row order.",
            "The chromVAR worksheet is excluded because it is a different analysis.",
        ],
        "duplicate_motif_names": duplicate_names,
        "motif_count": len(motifs),
        "motifs": motifs,
    }


# Table S4 has independent author-organized, Tomtom and CentriMo sections.
# Preserve each section independently as complete author evidence.
ARABIDOPSIS_SHEETS = [
    ("RBC-Enriched-THSs-CisBP", "Cis-BP", 6),
    ("RBC-Enriched-THSs-DAP-seq", "DAP-seq", 5),
]


def build_arabidopsis_reference() -> dict:
    import re
    from collections import Counter

    rel = "arabidopsis/NIHMS1584062-supplement-Table_S4.xlsx"
    path = DOWNLOADS / rel
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    organized = {}
    tf_support = {}
    tomtom = []
    centrimo = []
    for sheet_name, database, first_col in ARABIDOPSIS_SHEETS:
        rows = list(wb[sheet_name].iter_rows(values_only=True))
        organized_rows = []
        block = None
        headers = None
        for row_no, row in enumerate(rows, start=1):
            if row_no >= 2 and row[0] not in (None, ""):
                agi = str(row[1]).strip()
                if not re.fullmatch(r"AT[1-5]G\d{5}", agi):
                    raise ValueError(f"Unexpected AGI: {sheet_name}:{row_no}: {agi}")
                record = {
                    "author_identifier": str(row[0]).strip(),
                    "agi": agi,
                    "gene_symbol": str(row[2]).strip() if row[2] is not None else None,
                    "motif_database": database,
                    "source_worksheet": sheet_name,
                    "source_row": row_no,
                    "source_columns": {"author_identifier": "A", "agi": "B", "gene_symbol": "C"},
                }
                organized_rows.append(record)
                tf_support.setdefault(agi, []).append(record)

            cells = list(row[first_col - 1:])
            marker = str(cells[0]).strip() if cells and cells[0] is not None else ""
            if marker.upper() in {"DREME", "MEME", "CENTRIMO"}:
                block = "CentriMo" if marker.upper() == "CENTRIMO" else marker.upper()
                headers = None
                continue
            if not marker:
                continue
            if block is None:
                raise ValueError(f"Data outside a block: {sheet_name}:{row_no}")
            if headers is None:
                headers = [str(v).strip() if v is not None else None for v in cells]
                if block in {"DREME", "MEME"}:
                    expected = ["#Query ID", "Target ID", "Optimal offset", "p-value", "E-value", "q-value", "Overlap", "Query consensus", "Target consensus", "Orientation"]
                    if headers[:10] != expected:
                        raise ValueError(f"Changed Tomtom header: {sheet_name}:{row_no}")
                elif not {"# db", "E-value", "adj_p-value", "p-value"}.issubset(headers):
                    raise ValueError(f"Changed CentriMo header: {sheet_name}:{row_no}")
                continue

            source = {
                "record_id": f"{database}:{block}:{row_no}",
                "motif_database": database,
                "source_worksheet": sheet_name,
                "source_block": block,
                "source_row": row_no,
                "source_columns": {key: first_col + i for i, key in enumerate(headers) if key},
                "author_values": {key: cells[i] for i, key in enumerate(headers) if key},
            }
            values = source["author_values"]
            if block in {"DREME", "MEME"}:
                e_value = number(values["E-value"])
                if e_value is None:
                    raise ValueError(f"Missing Tomtom E-value: {source['record_id']}")
                tomtom.append({
                    **source,
                    "discovery_program": block,
                    "statistic_type": "Tomtom motif-to-motif similarity; not sequence enrichment",
                    "query_id": str(values["#Query ID"]).strip(),
                    "query_consensus": str(values["Query consensus"]).strip(),
                    "target_motif_id": str(values["Target ID"]).strip(),
                    "target_consensus": str(values["Target consensus"]).strip(),
                    "match_p_value": number(values["p-value"]),
                    "match_e_value": e_value,
                    "match_q_value": number(values["q-value"]),
                    "passes_match_e_value_le_0_05": e_value <= 0.05,
                    "passes_match_e_value_lt_0_05": e_value < 0.05,
                })
            else:
                raw_id = str(values["id                         alt"]).strip()
                motif_id, *alt = raw_id.split(maxsplit=1)
                e_value = number(values["E-value"])
                if e_value is None:
                    raise ValueError(f"Missing CentriMo E-value: {source['record_id']}")
                centrimo.append({
                    **source,
                    "statistic_type": "CentriMo positional enrichment",
                    "motif_id": motif_id,
                    "alternate_name": alt[0] if alt else None,
                    "consensus": values.get("consensus"),
                    "centrimo_e_value": e_value,
                    "centrimo_adjusted_p_value": number(values["adj_p-value"]),
                    "centrimo_p_value": number(values["p-value"]),
                    "passes_centrimo_e_value_le_0_05": e_value <= 0.05,
                    "passes_centrimo_e_value_lt_0_05": e_value < 0.05,
                })
        organized[sheet_name] = {
            "rows": len(organized_rows),
            "unique_author_identifiers": len({r['author_identifier'] for r in organized_rows}),
            "unique_agi": len({r['agi'] for r in organized_rows}),
            "entries": organized_rows,
        }
    wb.close()
    motifs = [
        {
            "reference_id": agi,
            "agi": agi,
            "entity_type": "TF gene associated with author-reported motifs",
            "gene_symbols": sorted({r['gene_symbol'] for r in support if r['gene_symbol']}),
            "author_identifiers": sorted({r['author_identifier'] for r in support}),
            "motif_databases": sorted({r['motif_database'] for r in support}),
            "author_support": support,
        }
        for agi, support in sorted(tf_support.items())
    ]
    return {
        "schema_version": "2.0",
        "task_id": "task_02",
        "analysis": "Author-reported TF set associated with mesophyll-enriched THS motifs; all S4 analysis blocks preserved separately",
        "source": source_info(rel, path),
        "cell_type": "mesophyll (author abbreviation RBC)",
        "source_worksheets": [s[0] for s in ARABIDOPSIS_SHEETS],
        "reference_type": "unranked_author_organized_TF_set",
        "evaluation_unit": "AGI gene identifier, not a unique PWM or a Tomtom match row",
        "ranking_metric": None,
        "display_order": "AGI ascending; no biological significance rank",
        "motif_count": len(motifs),
        "motif_count_unit": "unique TF AGIs in author organized lists",
        "motifs": motifs,
        "author_organized_list": organized,
        "tomtom_matches": tomtom,
        "centrimo_results": centrimo,
        "statistics_summary": {
            "tomtom_rows_by_block": dict(Counter(f"{r['motif_database']}:{r['discovery_program']}" for r in tomtom)),
            "centrimo_rows_by_database": dict(Counter(r['motif_database'] for r in centrimo)),
            "tomtom_match_e_value_le_0_05_rows": sum(r['passes_match_e_value_le_0_05'] for r in tomtom),
            "centrimo_e_value_le_0_05_rows": sum(r['passes_centrimo_e_value_le_0_05'] for r in centrimo),
            "exact_e_value_0_05_record_ids": [r['record_id'] for r in centrimo if r['centrimo_e_value'] == 0.05] + [r['record_id'] for r in tomtom if r['match_e_value'] == 0.05],
        },
        "significance_policy": {
            "primary_reference": "Use complete author significant/organized lists verbatim, including worksheet row 2; merge by AGI only.",
            "raw_records": "Preserve all published Tomtom and CentriMo rows, including non-significant rows, as audit evidence only.",
            "threshold_flags": "E <= 0.05 is flagged separately for each statistic. Methods use <= while S4 Overview says <; no row exactly 0.05 should be silently classified without checking.",
            "no_reconstruction_claim": "Do not infer the author organized list solely by filtering Tomtom E-values, or assign a Tomtom p-value to a TF's sequence enrichment.",
        },
        "excluded": ["CLV3 (stem-cell) worksheets"],
        "limitations": [
            "S4 DREME/MEME blocks report Tomtom matches, not the original discovery enrichment p-values.",
            "No author-supported unified enrichment ranking is available across databases/programs.",
            "Organized-list entries and raw-match identifiers are preserved without guessing DAP-seq alias mappings.",
            "The 100-bp supplied FASTA versus 300-bp Methods discrepancy remains outside this reference correction.",
        ],
    }
