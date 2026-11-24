"""Regenerate both compact scoring answers and full author evidence from pinned XLSX files."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import author_reference as author

ROOT = Path(__file__).resolve().parents[1]


def compact(task, full):
    if task == 'task_01':
        selected = [m['motif_id'] for m in full['motifs'][:10]]
    else:
        rows = [r for r in full['centrimo_results']
                if r['motif_database'] == 'Cis-BP' and r['author_values']['# db'] == 3]
        rows.sort(key=lambda r: (r['centrimo_e_value'], r['source_row']))
        selected = [r['motif_id'] for r in rows[:10]]
    if len(selected) != 10 or len(set(selected)) != 10:
        raise ValueError('Ambiguous or insufficient Top-10 names; do not silently deduplicate')
    return {'ids': selected}


def build(downloads, task):
    sources = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
    def checked_info(rel, path):
        spec = sources['files'][rel]
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != spec['sha256']:
            raise ValueError(f'Source hash mismatch: {rel}')
        return {'file': rel, 'sha256': actual, 'size': path.stat().st_size, 'url': spec['url']}
    author.DOWNLOADS = downloads
    author.source_info = checked_info
    # Verify before parsing as well as when generating provenance.
    rel = 'hydra/elife-60562-supp3-v2.xlsx' if task == 'task_01' else 'arabidopsis/NIHMS1584062-supplement-Table_S4.xlsx'
    checked_info(rel, downloads / rel)
    full = author.build_hydra_reference() if task == 'task_01' else author.build_arabidopsis_reference()
    return compact(task, full), full


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', required=True, type=Path, help='Downloaded source root containing hydra/ and arabidopsis/')
    parser.add_argument('--output-dir', required=True, type=Path, help='New output directory outside this repository')
    parser.add_argument('--task', choices=['all', 'task_01', 'task_02'], default='all')
    args = parser.parse_args()
    output, source = args.output_dir.resolve(), args.input_dir.resolve()
    try:
        if output.exists() or output.is_relative_to(ROOT) or ROOT.is_relative_to(output) or output.is_relative_to(source) or source.is_relative_to(output):
            raise ValueError('Choose a new output path outside the repository and source directory')
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output.parent) as temp:
            staging = Path(temp) / 'results'
            for task in ['task_01', 'task_02']:
                if args.task not in ['all', task]:
                    continue
                answer, evidence = build(source, task)
                folder = staging / task / 'reference'
                folder.mkdir(parents=True)
                for name, data in [('top10.json', answer), ('author_results.json', evidence)]:
                    (folder / name).write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
            staging.rename(output)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f'Extraction failed: {error}\n')
    print(f'Extracted references to {output}')


if __name__ == '__main__':
    main()
