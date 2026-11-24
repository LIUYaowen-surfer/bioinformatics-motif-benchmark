# Top-10 motif overlap

Both tasks use exactly the same prediction schema and scoring algorithm, like the DEG benchmark with K changed to 10.

```json
{"ids": ["motif_01", "motif_02", "motif_03", "motif_04", "motif_05", "motif_06", "motif_07", "motif_08", "motif_09", "motif_10"]}
```

These example IDs are placeholders, not valid biological predictions. Each file must contain exactly the key `ids` and exactly 10 different, nonempty strings. No leading/trailing whitespace is accepted. Matching is exact, case- and version-sensitive. There is no synonym/TF-family matching, automatic ID conversion, duplicate removal or partial credit for similar motifs.

**Score = |predicted Top 10 ∩ reference Top 10|**, an integer from **0 to 10**. Eight matching IDs score 8. Order does not affect the score. There is no F1 calculation and no different scoring mode for Task 02.

```sh
python scripts/score_motif.py result.json task_01/reference/top10.json
```

Success prints only the integer and exits 0. Invalid lengths, duplicates, extra/duplicate JSON keys, non-string IDs, nonstandard numbers or unreadable files fail with exit code 2 and no score on stdout. Neither input file is modified.

## How the references are selected

- **Task 01:** first 10 rows of Supplementary file 3 `3hpa HOMER Enrichment`, already ordered by ascending enrichment p-value. Preserve author order for ties. IDs are full HOMER motif names. The selected names are unique; no extra q-value or fold threshold is added.
- **Task 02:** S4 `RBC-Enriched-THSs-CisBP`, CentriMo block, restricted to database `# db = 3`. Rank by ascending CentriMo E-value, then source row; take 10 distinct motif IDs. Source rows are 234–243, and all 10 are already significant. Exclude de novo query motifs and DAP-seq entries. IDs are Cis-BP `M####_1.02` identifiers, not AGI genes. An unexpected duplicate in the selected 10 fails extraction instead of silently changing the selection.

Ranking statistics differ because the authors used different analyses; the **evaluation rule is identical**. The Task 02 Top 10 is a documented sub-analysis, not a fabricated ranking of the 291-gene list or a pooled Tomtom/DREME/MEME rank. Full author records remain in `author_results.json` for audit and do not add positive labels to the Top-10 score.

Report each task separately. A perfect-reference scoring self-test validates the scoring code, not an Agent's scientific analysis or a reproduced bioinformatics baseline.
