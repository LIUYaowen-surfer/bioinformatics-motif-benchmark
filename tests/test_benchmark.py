import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from score_motif import score, load_json
import prepare_inputs
from validate_repository import validate


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.ref = {'ids': [f'M{i:04d}_1.02' for i in range(10)]}

    def test_exact_reversed_and_partial_overlap(self):
        self.assertEqual(score(self.ref, self.ref), 10)
        self.assertEqual(score({'ids': self.ref['ids'][::-1]}, self.ref), 10)
        self.assertEqual(score({'ids': self.ref['ids'][:8] + ['x', 'y']}, self.ref), 8)

    def test_no_matches_and_case_sensitive(self):
        self.assertEqual(score({'ids': [x.lower() for x in self.ref['ids']]}, self.ref), 0)

    def test_reject_bad_cardinality_duplicates_and_types(self):
        for bad in [[], ['x'] * 10, list(range(10)), [' x'] + self.ref['ids'][1:], self.ref['ids'] + ['extra']]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                score({'ids': bad}, self.ref)
        with self.assertRaises(ValueError):
            score({'ids': self.ref['ids'], 'score': 10}, self.ref)

    def test_reject_duplicate_json_keys_and_nan(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'answer.json'
            for bad in ['{"ids": [], "ids": []}', '{"ids": [NaN]}']:
                path.write_text(bad)
                with self.assertRaises(ValueError):
                    load_json(path)

    def test_cli_prints_only_integer_and_does_not_modify_inputs(self):
        reference = ROOT / 'task_02/reference/top10.json'
        before = reference.read_bytes()
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/score_motif.py'), str(reference), str(reference)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '10')
        self.assertEqual(reference.read_bytes(), before)

    def test_cli_invalid_input_has_no_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / 'bad.json'
            bad.write_text('{"ids":[]}')
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/score_motif.py'), str(bad), str(ROOT / 'task_01/reference/top10.json')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')

    def test_committed_author_selections_and_resources(self):
        validate()


class PreparationTests(unittest.TestCase):
    def test_task02_export_allowlist_and_anonymization_with_fixture_resources(self):
        # Synthetic fixture exercises plumbing only; it is not a biological baseline.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_repo, source, resources = root / 'repo', root / 'source', root / 'resources'
            fake_repo.mkdir()
            inputs = source / 'task_02/input'
            inputs.mkdir(parents=True)
            resources.mkdir()
            seq = inputs / 'target_sequences.fasta'
            seq.write_text('>source_coordinates\nACGT\n')
            (fake_repo / 'inputs.json').write_text(json.dumps({'task_02': {'target': {'accepted_sha256': [hashlib.sha256(seq.read_bytes()).hexdigest()], 'sequences': 1, 'length': 4}}}))
            (fake_repo / 'agent_prompt.md').write_text('Neutral instruction')
            database = resources / 'motifs.meme'
            database.write_text('MEME version 4\nALPHABET= ACGT\n' + ''.join(f'MOTIF M{i:04d}_1.02\nletter-probability matrix: alength= 4 w= 1\n0.25 0.25 0.25 0.25\n' for i in range(11)))
            (resources / 'resource_manifest.json').write_text(json.dumps({'database_release': 'synthetic test fixture', 'source_url': 'fixture', 'files': {'motifs.meme': {'sha256': hashlib.sha256(database.read_bytes()).hexdigest()}}}))
            (resources / 'reference.json').write_text('DO NOT EXPORT')
            output = root / 'agent'
            with patch.object(prepare_inputs, 'ROOT', fake_repo):
                prepare_inputs.prepare('task_02', source, output, resources)
            self.assertEqual({p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}, {'prompt.md', 'input/task.json', 'input/target.fasta', 'input/resources/motifs.meme'})
            self.assertEqual(list(prepare_inputs.fasta(output / 'input/target.fasta')), [('target_000001', 'ACGT')])
            self.assertEqual(json.loads((output / 'input/task.json').read_text())['output_count'], 10)

    def test_anonymization_preserves_bases(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / 'source.fa', Path(tmp) / 'target.fa'
            src.write_bytes(b'>paper_id chr1:12-20\nACGTNN\n>other\nCCAA\n')
            spec = {'accepted_sha256': [hashlib.sha256(src.read_bytes()).hexdigest()], 'sequences': 2}
            self.assertEqual(prepare_inputs.copy_anonymous(src, dst, 'target', spec), 2)
            records = list(prepare_inputs.fasta(dst))
            self.assertEqual(records, [('target_000001', 'ACGTNN'), ('target_000002', 'CCAA')])

    def test_changed_source_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / 'source.fa', Path(tmp) / 'target.fa'
            src.write_text('>x\nACGT\n')
            with self.assertRaises(ValueError):
                prepare_inputs.copy_anonymous(src, dst, 'target', {'accepted_sha256': ['0' * 64], 'sequences': 1})
            self.assertFalse(dst.exists())

    def test_task02_missing_resources_fails_without_partial_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'workspace'
            with self.assertRaisesRegex(ValueError, 'requires --resources-dir'):
                prepare_inputs.prepare('task_02', Path(tmp) / 'source', output)
            self.assertFalse(output.exists())

    def test_existing_workspace_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'workspace'
            output.mkdir()
            sentinel = output / 'keep.txt'
            sentinel.write_text('unchanged')
            with self.assertRaises(ValueError):
                prepare_inputs.prepare('task_01', Path(tmp) / 'source', output)
            self.assertEqual(sentinel.read_text(), 'unchanged')


if __name__ == '__main__':
    unittest.main()
