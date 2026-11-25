# Top-10 motif overlap

Both tasks use the same prediction format and scoring algorithm. Each task selects its Top 10 using the ranking statistic below.

## Ranking and reference selection

| Task | Ranking statistic | Order | Motif identifier |
|---|---|---|---|
| Task 01: Hydra | HOMER enrichment **P-value** | Ascending (smallest first) | Full HOMER motif name |
| Task 02: Arabidopsis | CentriMo positional-enrichment **E-value** | Ascending (smallest first) | Cis-BP `M####_1.02` motif ID |

- **Task 01:** the reference is the first 10 rows of Supplementary file 3, sheet `3hpa HOMER Enrichment`, ordered by enrichment P-value. Author row order resolves ties. Selection uses the first 10 rows directly.
- **Task 02:** the reference comes from Supplementary Table S4, sheet `RBC-Enriched-THSs-CisBP`, CentriMo block, database `# db = 3`. Sort by E-value, with source row as tie-breaker, and select the first 10 rows (234–243). These rows contain 10 unique Cis-BP motif IDs.

For Agent predictions, use the corresponding statistic in the table and database order to resolve ties. P-values and E-values determine membership in the Top 10; the score counts matching motif IDs. Full author records and source-row provenance are available in each task's `reference/author_results.json`.

## Prediction format

Write `result.json` with exactly one key, `ids`, containing 10 unique, nonempty motif-ID strings. Preserve exact spelling, case and version, with whitespace-free ends. The following illustrates the schema using placeholder IDs:

```json
{"ids": ["motif_01", "motif_02", "motif_03", "motif_04", "motif_05", "motif_06", "motif_07", "motif_08", "motif_09", "motif_10"]}
```

## Score

**Score = |predicted Top 10 ∩ reference Top 10|**, an integer from **0 to 10**. Each exact ID match contributes one point. Eight matching IDs score 8. The score is independent of list order. Report each task separately.

```sh
python scripts/score_motif.py result.json task_01/reference/top10.json
python scripts/score_motif.py result.json task_02/reference/top10.json
```

Use the command for the task being evaluated. Success prints the integer score and exits 0. Invalid input produces exit code 2 and an error message, with empty stdout. Input files are read-only. Scoring self-tests validate the scoring implementation; biological validation requires a separate analysis run.
