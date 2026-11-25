# Offline motif resources

## Hydra

`resources/hydra/motifs.homer` retains all 332 matrices in the author's full generic chromVar/HOMER library, in original order. Keep consensus, full motif name and scoring threshold; prior enrichment statistics after header field 3 are removed. Matrix rows are unchanged. Source URL, original hash and sanitized hash are in `resource_manifest.json`.

This is the full candidate motif universe. Original discovery-study labels inside motif names belong to the HOMER ID namespace and remain necessary for exact matching.

## Arabidopsis / Cis-BP

The frozen preparation source is the [RSAT Arabidopsis Cis-BP 1.02 mirror](https://rsat.eead.csic.es/plants/motif_databases/cisBP/CisBp_A_thaliana.tf): **309 unique motifs**, retaining the `M####_1.02` namespace. The [resource manifest](../resources/cisbp/resource_manifest.json) records the source and converted SHA-256 values, conversion method and limitations. The database is downloaded during preparation, not bundled in this repository. See the mirror's [license notice](https://rsat.eead.csic.es/plants/motif_databases/cisBP/LICENSE.txt); third-party terms continue to apply.

From the repository root, using Python 3.11 or newer (standard library only):

```sh
python scripts/prepare_cisbp.py --output-dir data/cisbp_resources
```

Alternatively, use the downloaded file without network access:

```sh
python scripts/prepare_cisbp.py --source-file /path/to/CisBp_A_thaliana.tf --output-dir data/cisbp_resources
```

Use a new output directory. Both routes verify the frozen source hash before conversion and the output hash afterward. The script keeps all 309 motifs in source order, normalizes each A/C/G/T row by its sum, and writes 12 decimal places. It produces `motifs.meme` and `resource_manifest.json`. No reference answers are read and no enrichment analysis runs.

```sh
python scripts/prepare_inputs.py --task task_02 --source-dir data --resources-dir data/cisbp_resources --output-dir ../motif_agent_02
```

The exporter checks the manifest hash and motif syntax, then copies only `motifs.meme` into the Agent resource directory. Supply the complete frozen library to every Agent.

This freezes a reproducible mirror-based candidate library, **not proof of identity with the paper's original database**. The mirror stores rounded integer matrix values; conversion cannot recover previously lost precision. No background frequencies are embedded: the analysis must specify and record its statistical background model. No biological baseline has been run.

No TAIR10 genome is required to consume the author's supplied masked sequences. Their 100-bp versus 300-bp Methods discrepancy remains unresolved; changing the input windows would define a new benchmark version.
