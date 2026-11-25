# Task 02 — Arabidopsis mesophyll motif-associated TFs

Evaluator documentation; do not supply it to the Agent.

- Paper: Sijacic et al. (2018), *Chromatin accessibility changes between Arabidopsis stem cells and mesophyll cells illuminate cell type-specific transcription factor networks*. [DOI](https://doi.org/10.1111/tpj.13882), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7219318/).
- [GEO GSE101940](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE101940).
- [Source links](filelink.md), [scoring answer](reference/top10.json), [complete author evidence](reference/author_results.json).

The target FASTA contains all 10,013 100-bp masked sequences from S4 `Sequences`, column B (`RBC-Enriched-THSs`), unchanged apart from anonymized headers in exported workspaces. RBC denotes mesophyll. No explicit negative FASTA is published. Record the statistical background model for each MEME-ChIP component and its software version.

The complete audit evidence includes the unranked union of **291 TF AGIs** in the author's RBC organized lists: 175 Cis-BP rows / 173 AGIs and 173 DAP-seq rows / 171 AGIs, including row 2. These lists provide gene-level audit evidence. Full evidence retains 638 Tomtom matches (181+46 Cis-BP DREME/MEME; 326+85 DAP-seq) and 570 CentriMo rows (234 Cis-BP, 336 DAP-seq).

Tomtom statistics describe motif similarity. The source DREME/MEME blocks do not report the original discovery enrichment p-values. Both query ID and actual query consensus are preserved. E <= 0.05 selects 154 raw Tomtom matches and 438 CentriMo rows; E < 0.05 selects 437 CentriMo rows. The Methods/Overview differ at equality; both flags are retained, and the primary author-organized set is not reconstructed by that cutoff.

## Scored Top 10

The scoring reference uses the Cis-BP CentriMo block only: `# db = 3`, ascending `E-value`, source row as tie-breaker, first 10 rows (234–243). The IDs are Cis-BP motif IDs. All selected 10 are significant. The 291-AGI collection provides supplementary audit evidence.

Both tasks score exact Top-10 ID overlap from 0 to 10.

## Limits that remain

- Methods describe 300-bp windows and S1 lists 5,895 enriched THSs, whereas supplied S4 sequences are 10,013 × 100 bp. All sequence coordinates overlap enriched S1 regions, covering 5,885 of 5,895; five sequences cross two regions. Exact generation of these inputs remains unresolved. CentriMo positional statistics may reflect a different window representation. Scores measure correspondence to author labels, not a proven exact rerun from these 100-bp sequences.
- The 309-motif Cis-BP 1.02 RSAT mirror is frozen by source/output hashes and can be prepared as [offline resources](../docs/resources.md). Its identity with the paper's original matrix file remains unproven; mirror rounding may affect results.
- TAIR10 is the reported assembly; a complete genome is unnecessary for consuming author sequences and is not included.
- Local source hashes were verified, but manual PMC downloads were not independently matched to a remote official checksum.

Task 02 is suitable as a transparent exploratory benchmark with these limitations. Do not present it as an exact historically reproducible MEME-ChIP run.
