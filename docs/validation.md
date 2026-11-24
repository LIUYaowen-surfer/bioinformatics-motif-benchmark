# Validation recorded 2026-11-24

- 12 unit/regression tests passed: common 0–10 scorer, exact/partial/no overlap, order invariance, case sensitivity, malformed/duplicate JSON, cardinality, no input mutation, FASTA anonymization, source-hash rejection, output-directory protection, missing-resource failure and workspace allowlist.
- Both `top10.json` files and both complete `author_results.json` files regenerated from pinned author XLSX sources and matched the committed files byte-for-byte. Reference serialization uses LF on Windows and Linux.
- Rebuilt 2,183 Hydra target, 33,214 Hydra background and 10,013 Arabidopsis target sequences from the downloaded author sources. All rebuilt FASTA hashes matched the reviewed values.
- Exported a real Hydra workspace and compared all DNA sequences with the prepared inputs: no sequence/order changes. Its exact file allowlist was checked; no author reference, table, BED coordinate or source manifest was exported.
- Validated the sanitized full 332-matrix Hydra motif library, Top-10 selection provenance, local documentation links and the prior numerical background audit.
- Prepared the real 309-motif Cis-BP 1.02 RSAT mirror from the pinned downloaded TRANSFAC source. Source and converted SHA-256 checks passed; the converted MEME file exactly matched the resource prepared in the original local directory. Exported a real Task 02 workspace with all 10,013 sequences unchanged and the identical motif file. The synthetic fixture test remains a separate regression check. No biological Task 02 baseline was run.
- No HOMER enrichment run, CentriMo run, Agent benchmark run, raw-read processing or genome alignment was performed. Reference self-scores are software checks, not empirical benchmark results.

Repeat the utility tests with `python -m unittest discover -s tests -v` and repository checks with `python scripts/validate_repository.py`. Source-data integration checks require the external downloads listed in the task documentation.
