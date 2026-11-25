# Task 01 — Hydra 0–3 h HOMER results

Evaluator documentation; do not supply it to the Agent.

- Paper: Cazet, Cho and Juliano (2021), *Generic injuries are sufficient to induce ectopic Wnt organizers in Hydra*. [DOI](https://doi.org/10.7554/eLife.60562).
- [GEO GSE152994](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE152994); [author code](https://github.com/cejuliano/jcazet_regeneration_patterning).
- [Source links](filelink.md), [scoring answer](reference/top10.json), [complete author results](reference/author_results.json).

Targets are the union of head/foot 3 h versus 0 h accessibility increases with FDR <= 1e-4 and log2FC > 0, restricted to H3H0 table IDs (2,183). Background is the other H3H0 IDs (33,214), following author Up.3/Up.3.c definitions. Coordinates come from the untreated DiffBind-labelled consensus BED. Extract from Hydra 2.0.

The complete 332-row reference comes from Supplementary file 3, `3hpa HOMER Enrichment`, preserving motif names, consensus, p/q statistics and row provenance. The scored answer is the first 10 rows in author order. These 10 names are unique; one duplicate name remains outside the selected top 10. Selection uses the first 10 rows directly.

All 35,397 source sequences were checked base-by-base against the author's BSgenome 2bit genome. The preparation script anonymizes FASTA headers while preserving bases and order. BED and source coordinates remain evaluator-only. The full known-motif database is provided with prior result statistics removed from headers.

HOMER's weighted background is approximately 32,333.52, rather than the raw 33,214 records. See the [background audit](../docs/hydra_background.md). The original installed HOMER version remains unknown; exact p-value reproduction is not a scoring requirement.
