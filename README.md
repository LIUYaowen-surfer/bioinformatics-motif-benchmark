# Bioinformatics Motif Benchmark

Identify the **top 10 motifs** from DNA sequences and compare them with author-published results. Both tasks use the same scoring rule: exact Top-10 ID overlap, **0–10**, with no F1 score or rank weighting. The layout follows [Bioinformatics DEG Benchmark](https://github.com/LIUYaowen-surfer/bioinformatics-deg-benchmark).

| Task | Input | Author Top-10 selection | Reference |
|---|---|---|---|
| [task_01](task_01/README.md) | Hydra 0–3 h opening regions; 2,183 target / 33,214 explicit background sequences | HOMER known motifs, ascending enrichment p-value | [Top 10](task_01/reference/top10.json) |
| [task_02](task_02/README.md) | Arabidopsis mesophyll; 10,013 author-supplied masked sequences | Cis-BP database motifs in CentriMo, ascending positional-enrichment E-value | [Top 10](task_02/reference/top10.json) |

These are sequence-level tasks, not raw ATAC-seq analysis tasks. Task 02 intentionally selects the Cis-BP CentriMo sub-analysis; the unranked 291-AGI author list and Tomtom match p-values are not used to invent a Top 10. The original 100-bp input versus 300-bp Methods discrepancy remains documented.

## Prepare the workspace

Source links and pinned hashes are included. Large genomes, spreadsheets and sequence inputs are not committed. If you already have the reviewed `motif-data-preparation` directory, use it directly as `--source-dir` below. Otherwise download the sources linked from each task's `filelink.md`, preserving their `hydra/` and `arabidopsis/` subfolders, then rebuild:

```sh
python scripts/install_dependencies.py
python scripts/rebuild_inputs.py --downloads downloads --output-dir data
```

Hydra sequences are extracted from the author's BSgenome 2bit genome using BED zero-based half-open intervals, without installing R or substituting a newer assembly. Arabidopsis sequences are copied from author S4 cells. Rebuilt FASTA hashes must match the reviewed inputs. No motif analysis runs during this step.

Create a fresh Agent workspace outside the repository:

```sh
python scripts/prepare_inputs.py --task task_01 --source-dir data --output-dir ../motif_agent_01
python scripts/prepare_cisbp.py --output-dir data/cisbp_resources
python scripts/prepare_inputs.py --task task_02 --source-dir data --resources-dir data/cisbp_resources --output-dir ../motif_agent_02
```

Task 01 includes the full 332-matrix motif library with previous enrichment statistics removed from headers. Task 02 preparation downloads and verifies the **309-motif Arabidopsis Cis-BP 1.02 RSAT mirror**, then converts it to MEME format using pinned source/output hashes; see [resource requirements](docs/resources.md). All candidate motifs are retained. This mirror is now frozen for preparation, but identity with the paper's original database and exact historical analysis remains unproven.

The exporter verifies hashes and writes only anonymous target/background FASTA, the common `prompt.md`, neutral task instructions and allowlisted motif resources. It does not export author tables, genomic coordinates, references, paper links, evaluator scripts or repository history. Existing output directories are refused.

## Run and score

The benchmark selects **HOMER 5.1** and **MEME Suite 5.5.7** for new evaluation runs. These are benchmark choices, not recovered author versions. [eval_config.yaml](eval_config.yaml) records those exact versions, the tested Python version, database manifests and validation status. Analysis-tool installation and enrichment runs have not yet been tested; this is not a solved dependency or container lock.

All Python preparation/audit dependencies are pinned directly in `eval_config.yaml` under `utility_environment.pip_dependencies`. There is no separate requirements file. `python scripts/install_dependencies.py` reads that list and installs it with the current Python interpreter; `python scripts/install_dependencies.py --check` verifies installed versions without installing anything. The installer uses only the Python standard library and expects the documented JSON-compatible YAML flow-list syntax. HOMER and MEME remain separate analysis applications installed through the command below.

On Linux/WSL2 with Conda available, the selected analysis versions can be requested with the following command (installation not yet validated here):

```sh
conda create -n motif-analysis --override-channels -c conda-forge -c bioconda --strict-channel-priority homer=5.1 meme=5.5.7
```

Before official evaluation, verify installed versions and archive resolved package builds or a container digest, command lines and resource limits. Give all Agents identical software, database releases and resource limits, and run offline with only the exported workspace mounted.

The Agent writes `result.json` with `{"ids": [...]}` containing exactly 10 unique IDs. Outside its environment, score against the selected task:

```sh
python scripts/score_motif.py ../motif_agent_01/result.json task_01/reference/top10.json
python scripts/score_motif.py ../motif_agent_02/result.json task_02/reference/top10.json
```

Both commands print one integer from 0 to 10. List order is not scored; IDs must match exactly. See [scoring.md](scoring.md). Keep `methods.md` and logs alongside the score; ID overlap alone does not verify scientific validity.

## Reproduce references and validate

```sh
python scripts/extract_reference.py --input-dir downloads --output-dir ../motif_regenerated
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

The extractor verifies source SHA-256 values and writes `task_XX/reference/top10.json` plus complete `author_results.json`. Use `--task task_01` or `--task task_02` to limit extraction. Existing output paths are never overwritten. Full evidence retains the corrected Task 02 AGI lists, Tomtom and CentriMo records, separately from the simple scoring answer.

The [Hydra background audit](docs/hydra_background.md) explains why 33,214 raw regions produce an effective background weight near 32,333.52; no input records were deleted to force agreement with the published table heading.

## Structure and limitations

```text
agent_prompt.md / eval_config.yaml / scoring.md
inputs.json / sources.json
scripts/                  preparation, extraction, scoring, validation
task_01/ and task_02/      evaluator notes, source links, Top-10 and full evidence
resources/hydra/          full motif universe, sanitized headers
resources/cisbp/          frozen source/output hashes and provenance
docs/                     resource requirements and background audit
tests/                    meaningful format/scoring/preparation regressions
```

Keep this public evaluator repository, its history and source papers outside the Agent environment. Anonymization and offline mounting reduce direct answer access but cannot guarantee absence of study recognition or training-data contamination. Author results are reproducibility targets, not unique biological ground truth. Task 02's input/method mismatch and incomplete historical resource provenance may affect attainable overlap even for a valid workflow. Third-party data and motif resources retain their original terms; no blanket license is assigned to them.
