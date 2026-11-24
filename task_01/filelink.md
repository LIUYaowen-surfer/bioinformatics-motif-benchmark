# task_01 source files

Preparation/evaluation only. Preserve the relative download paths below. The checked-in `sources.json` pins the reviewed SHA-256 values.

| Local path under downloads/ | Source | SHA-256 |
|---|---|---|
| `hydra/elife-60562-supp3-v2.xlsx` | [Download/source](https://cdn.elifesciences.org/articles/60562/elife-60562-supp3-v2.xlsx) | `6cad74e027fc0c7bb9239dc4ea64567267bb92991ff86b9d1749dbb2d63ece71` |
| `hydra/elife-60562-supp1-v2.xlsx` | [Download/source](https://cdn.elifesciences.org/articles/60562/elife-60562-supp1-v2.xlsx) | `516c738ec517f187bba819966a7bdcd950358df354d2dbd068cf19d235d47015` |
| `hydra/GSE152994_untreated_consensus_diffbind_labels.bed.gz` | [Download/source](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE152nnn/GSE152994/suppl/GSE152994_untreated_consensus_diffbind_labels.bed.gz) | `699643015032596a47d685357dd2739c405a4e8f3cc2fbd6aa6704524a948c7e` |
| `hydra/BSgenome.Hymag.NIH.Hymag2_2.0.tar.gz` | [Download/source](https://datadryad.org/dataset/doi:10.25338/B8S612) | `72ca05d3055e9d24ac667b3c22cc056e7cd271487e7811e84ff201fa3d96e992` |

The BSgenome link is a dataset landing page. In the 2021 Dryad `fullRepo.zip` archive, obtain `fullRepo/local/resources/BSgenome.Hymag.NIH.Hymag2_2.0.tar.gz`. The repository does not automatically download the 3.8-GB archive. An already reviewed tarball can be reused; do not substitute a newer Hydra assembly.

Input rebuilding needs supp1, the BED gzip and BSgenome tarball. Reference extraction needs supp3. The full motif library is already included separately.
