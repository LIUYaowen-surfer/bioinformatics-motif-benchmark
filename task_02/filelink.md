# task_02 source files

Preparation/evaluation only. Preserve the relative download paths below. The checked-in `sources.json` pins the reviewed SHA-256 values.

| Local path under downloads/ | Source | SHA-256 |
|---|---|---|
| `arabidopsis/NIHMS1584062-supplement-Table_S1.xlsx` | [Download/source](https://pmc.ncbi.nlm.nih.gov/articles/instance/7219318/bin/NIHMS1584062-supplement-Table_S1.xlsx) | `dea4e0c9f46259f8d89e80c962d7692b3b69bbd50623df0098334404ade3ef05` |
| `arabidopsis/NIHMS1584062-supplement-Table_S2.xlsx` | [Download/source](https://pmc.ncbi.nlm.nih.gov/articles/instance/7219318/bin/NIHMS1584062-supplement-Table_S2.xlsx) | `7b768bd03c11f54680fb9bc5eb07c6d1eed8064b598cd70d28ef28be48e589fa` |
| `arabidopsis/NIHMS1584062-supplement-Table_S4.xlsx` | [Download/source](https://pmc.ncbi.nlm.nih.gov/articles/instance/7219318/bin/NIHMS1584062-supplement-Table_S4.xlsx) | `09f494899c1750c07395d1705e60c82f49e840043bd3015f77ddfe9d1e8a82e0` |

S4 alone is required for sequence and reference rebuilding. S1/S2 support region auditing. The PMC source may require a browser download; preserve the actual XLSX bytes and validate the pinned hash. No TAIR10 genome or explicit background FASTA is required for the supplied-sequence route.

The motif database is prepared separately: [Cis-BP 1.02 Arabidopsis TRANSFAC mirror (309 motifs)](https://rsat.eead.csic.es/plants/motif_databases/cisBP/CisBp_A_thaliana.tf). Source SHA-256: `7fd2ecab4d39ec7e6838a8ad772f0c6b487c091479a2f8ed30678c3bccdf4497`. See the [resource manifest](../resources/cisbp/resource_manifest.json) and [preparation instructions](../docs/resources.md).
