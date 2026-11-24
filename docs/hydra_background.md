# Hydra background count audit

The raw background consists of **33,214** BED/FASTA records. It is not missing 881 records. Replaying the relevant HOMER source rules gives:

| Stage | Background |
|---|---:|
| Original regions | 33,214 |
| After GC bins without target support are excluded | 33,212 |
| Initial GC-weight sum | 33,211.98705 |
| After default 1–3-mer normalization, written with 6 decimals | **32,333.520313** |
| Author table heading | 32,333 |

The two unsupported-bin IDs are 21973 and 92136 (60–70% GC). No sequence fails the default >70% N or length filters. The remaining decrease is a change in weights, not additional deleted BED records. No input is altered by this audit.

Independently, 331 nonzero author background count/proportion pairs constrain the effective denominator to **32,333.491180–32,333.610519**, allowing for displayed rounding. The replayed sum lies inside that interval. The integer header must not be interpreted as a raw region count.

The exact author-installed HOMER executable and original group file were not recovered. The inspected source-code mirror is pinned by SHA-256 in [the numerical audit](hydra_background_audit.json). This is a source-rule replay consistent with the published table, not a full original enrichment rerun or a claim of exact historical software identity.

Optional reproduction, using a prepared data root containing `task_01/input/`:

```sh
python -m pip install -r requirements.txt
python scripts/audit_hydra_background.py --root data
```

Only GC and small k-mer composition/weights are calculated. No motif discovery, motif scanning or enrichment p-value calculation runs.
