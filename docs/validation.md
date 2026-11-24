# Validation recorded 2026-11-24

- 12 unit/regression tests passed: common 0–10 scorer, exact/partial/no overlap, order invariance, case sensitivity, malformed/duplicate JSON, cardinality, no input mutation, FASTA anonymization, source-hash rejection, output-directory protection, missing-resource failure and workspace allowlist.
- Both `top10.json` files and both complete `author_results.json` files regenerated from pinned author XLSX sources and matched the committed files byte-for-byte. Reference serialization uses LF on Windows and Linux.
- Rebuilt 2,183 Hydra target, 33,214 Hydra background and 10,013 Arabidopsis target sequences from the downloaded author sources. All rebuilt FASTA hashes matched the reviewed values.
- Exported a real Hydra workspace and compared all DNA sequences with the prepared inputs: no sequence/order changes. Its exact file allowlist was checked; no author reference, table, BED coordinate or source manifest was exported.
- Validated the sanitized full 332-matrix Hydra motif library, Top-10 selection provenance, local documentation links and the prior numerical background audit.
- Task 02 workspace export was tested with a clearly synthetic database fixture only. A real complete, versioned Cis-BP library has not yet been staged; no biological Task 02 baseline was run.
- No HOMER enrichment run, CentriMo run, Agent benchmark run, raw-read processing or genome alignment was performed. Reference self-scores are software checks, not empirical benchmark results.

Repeat the utility tests with `python -m unittest discover -s tests -v` and repository checks with `python scripts/validate_repository.py`. Source-data integration checks require the external downloads listed in the task documentation.
