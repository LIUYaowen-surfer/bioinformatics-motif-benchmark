"""Validate committed Top-10 references, audit evidence, and motif-resource integrity."""
import hashlib
import json
from pathlib import Path
from score_motif import load_json, score

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    for task in ['task_01', 'task_02']:
        answer = load_json(root / task / 'reference/top10.json')
        full = load_json(root / task / 'reference/author_results.json')
        if score(answer, answer) != 10:
            raise ValueError('Self-score must be 10')
        if task == 'task_01':
            expected = [m['motif_id'] for m in full['motifs'][:10]]
            assert full['motif_count'] == len(full['motifs']) == 332
            assert [m['p_value'] for m in full['motifs']] == sorted(m['p_value'] for m in full['motifs'])
        else:
            selected = sorted((r for r in full['centrimo_results'] if r['source_worksheet'] == 'RBC-Enriched-THSs-CisBP' and r['author_values']['# db'] == 3), key=lambda r: (r['centrimo_e_value'], r['source_row']))[:10]
            expected = [r['motif_id'] for r in selected]
            assert [r['source_row'] for r in selected] == list(range(234, 244))
            assert all(r['centrimo_e_value'] <= .05 for r in selected)
            assert full['motif_count'] == 291 and len(full['tomtom_matches']) == 638 and len(full['centrimo_results']) == 570
            assert full['ranking_metric'] is None  # Full AGI audit set remains unranked.
            assert full['tomtom_matches'][0]['query_id'] != full['tomtom_matches'][0]['query_consensus']
            assert all(v['entries'][0]['source_row'] == 2 for v in full['author_organized_list'].values())
        assert answer['ids'] == expected
        sources = load_json(root / 'sources.json')['files']
        assert full['source']['sha256'] == sources[full['source']['file']]['sha256']
    library = root / 'resources/hydra/motifs.homer'
    manifest = load_json(root / 'resources/hydra/resource_manifest.json')
    assert hashlib.sha256(library.read_bytes()).hexdigest() == manifest['files']['motifs.homer']['sha256']
    headers = [line.split('\t') for line in library.read_text(encoding='utf-8').splitlines() if line.startswith('>')]
    assert len(headers) == 332 and all(len(row) == 3 for row in headers)
    assert set(load_json(root / 'task_01/reference/top10.json')['ids']) <= {h[1] for h in headers}
    audit = load_json(root / 'docs/hydra_background_audit.json')
    assert audit['raw_background_sequences'] == 33214
    assert audit['retained_background_sequences'] == 33212
    assert audit['author_table_denominator_check']['replayed_weight_sum_in_interval']
    assert abs(audit['group_file_6_decimal_weight_sum'] - 32333.520313) < .001
    print('PASS: both Top-10 references, corrected full evidence, sanitized 332-matrix library and background audit')


if __name__ == '__main__':
    validate()
