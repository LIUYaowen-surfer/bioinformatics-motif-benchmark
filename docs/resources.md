# Offline motif resources

## Hydra

`resources/hydra/motifs.homer` retains all 332 matrices in the author's full generic chromVar/HOMER library, in original order. Keep consensus, full motif name and scoring threshold; prior enrichment statistics after header field 3 are removed. Matrix rows are unchanged. Source URL, original hash and sanitized hash are in `resource_manifest.json`.

This is the full candidate motif universe, not a Top-10 subset. Original discovery-study labels inside motif names belong to the HOMER ID namespace and remain necessary for exact matching.

## Arabidopsis / Cis-BP

Supply a separate directory with `motifs.meme` (the complete relevant Cis-BP library, retaining the `M####_1.02` namespace) and `resource_manifest.json`:

```json
{
  "database_release": "actual complete Cis-BP release used",
  "source_url": "database download URL",
  "files": {"motifs.meme": {"sha256": "actual SHA-256"}}
}
```

The exporter verifies the recorded hash, requires unique MOTIF IDs and copies only `motifs.meme`. It cannot prove completeness or historical identity from a self-recorded hash. Review and freeze the database before comparing Agents. Do not use a Top-10-only database, a database filtered by author positive results, or a motif library reconstructed from the 291 AGI list. This repository has not yet recovered a frozen historical Cis-BP library. No DAP-seq library or motif-to-AGI mapping is needed for this Top-10 Cis-BP protocol.

No TAIR10 genome is required to consume the author's supplied masked sequences. Their 100-bp versus 300-bp Methods discrepancy remains unresolved; changing the input windows would define a new benchmark version.
