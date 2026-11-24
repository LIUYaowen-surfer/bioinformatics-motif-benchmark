"""Create a fresh anonymous offline workspace from verified prepared FASTA files."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def fasta(path):
    name, chunks = None, []
    seen = set()
    with path.open(encoding='ascii') as stream:
        for raw in stream:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('>'):
                if name is not None:
                    if not chunks:
                        raise ValueError('Empty FASTA record')
                    yield name, ''.join(chunks)
                name, chunks = line[1:], []
                if not name or name in seen:
                    raise ValueError('Empty or duplicate FASTA header')
                seen.add(name)
            else:
                if name is None or set(line) - set('ACGTN'):
                    raise ValueError('Expected uppercase A/C/G/T/N FASTA with headers')
                chunks.append(line)
    if name is None or not chunks:
        raise ValueError('Empty FASTA or final record')
    yield name, ''.join(chunks)


def copy_anonymous(source, dest, role, spec):
    if digest(source) not in spec['accepted_sha256']:
        raise ValueError(f'Unreviewed input hash: {source.name}')
    with dest.open('w', encoding='ascii', newline='\n') as out:
        count = 0
        for count, (_, seq) in enumerate(fasta(source), 1):
            if spec.get('length') is not None and len(seq) != spec['length']:
                raise ValueError('Unexpected sequence length')
            out.write(f'>{role}_{count:06d}\n')
            out.write('\n'.join(seq[i:i + 60] for i in range(0, len(seq), 60)) + '\n')
    if count != spec['sequences']:
        raise ValueError(f'Wrong {role} count: {count}')
    return count


def stage_resources(task, source, dest):
    expected_names = ['motifs.homer'] if task == 'task_01' else ['motifs.meme']
    if source is None and task == 'task_01':
        source = ROOT / 'resources/hydra'
    if source is None:
        raise ValueError('Task 02 requires --resources-dir with the complete Cis-BP motif database; see docs/resources.md')
    manifest = json.loads((source / 'resource_manifest.json').read_text(encoding='utf-8'))
    if set(manifest['files']) != set(expected_names):
        raise ValueError(f'Resource manifest must list exactly {expected_names}')
    for name in expected_names:
        if (source / name).is_symlink() or digest(source / name) != manifest['files'][name]['sha256']:
            raise ValueError(f'Resource hash mismatch or symlink: {name}')
    if task == 'task_01':
        reviewed = json.loads((ROOT / 'resources/hydra/resource_manifest.json').read_text(encoding='utf-8'))
        if manifest['files'] != reviewed['files']:
            raise ValueError('Use the frozen full Hydra motif library for this protocol')
    else:
        import re
        motif_ids = set()
        database_text = (source / 'motifs.meme').read_text(encoding='utf-8')
        if not database_text.lstrip().startswith('MEME version'):
            raise ValueError('Expected a MEME-format motif database')
        for line in database_text.splitlines():
            if line.startswith('MOTIF '):
                identifier = line.split()[1]
                if not re.fullmatch(r'M\d+_1\.02', identifier):
                    raise ValueError('Use the original Cis-BP M####_1.02 motif-ID namespace')
                if identifier in motif_ids:
                    raise ValueError('Duplicate database motif ID')
                motif_ids.add(identifier)
        if len(motif_ids) <= 10:
            raise ValueError('Provide the complete candidate database, not a Top-10 subset')
        if database_text.count('letter-probability matrix:') != len(motif_ids):
            raise ValueError('Each motif must have a letter-probability matrix')
        if not manifest.get('database_release') or not manifest.get('source_url'):
            raise ValueError('Record database_release and source_url for Task 02')
    dest.mkdir()
    for name in expected_names:
        shutil.copyfile(source / name, dest / name)
    # Only identity/checksum information enters the neutral workspace.
    return {name: digest(dest / name) for name in expected_names}


def prepare(task, source, output, resource_dir=None):
    output, source = output.resolve(), source.resolve()
    if output.exists() or output.is_relative_to(ROOT) or ROOT.is_relative_to(output) or output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('Choose a new output path outside the repository and source directory')
    manifests = json.loads((ROOT / 'inputs.json').read_text(encoding='utf-8'))
    spec = manifests[task]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        workspace = Path(temp) / 'workspace'
        inputs = workspace / 'input'
        inputs.mkdir(parents=True)
        hashes = stage_resources(task, resource_dir, inputs / 'resources')
        counts = {}
        for role in ['target', 'background']:
            if role not in spec:
                continue
            original = source / task / 'input' / f'{role}_sequences.fasta'
            counts[role] = copy_anonymous(original, inputs / f'{role}.fasta', role, spec[role])
        contract = {
            'input': 'input/target.fasta', 'sequence_counts': counts,
            'background': 'input/background.fasta' if task == 'task_01' else None,
            'background_policy': 'Use the supplied explicit background with composition correction' if task == 'task_01' else 'No explicit negative FASTA was supplied. Use and document a justified sequence background model; do not treat another cell type as the author background.',
            'objective': 'Rank known motifs by enrichment p-value; return the top 10 distinct full HOMER motif names, with no added significance threshold. Break ties by database order.' if task == 'task_01' else 'Rank Cis-BP database motifs by CentriMo positional-enrichment E-value and return the top 10 distinct motif IDs. Exclude de novo query motifs and other databases. Do not rank by Tomtom similarity statistics or by AGI gene name.',
            'id_namespace': 'HOMER full motif name' if task == 'task_01' else 'Cis-BP motif ID (M####_1.02 namespace)',
            'output_count': 10,
            'resource_sha256': hashes,
        }
        (inputs / 'task.json').write_text(json.dumps(contract, indent=2) + '\n', encoding='utf-8')
        shutil.copyfile(ROOT / 'agent_prompt.md', workspace / 'prompt.md')
        workspace.rename(output)
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', choices=['task_01', 'task_02'], required=True)
    parser.add_argument('--source-dir', type=Path, required=True, help='Prepared root containing task_XX/input/')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--resources-dir', type=Path)
    args = parser.parse_args()
    try:
        counts = prepare(args.task, args.source_dir, args.output_dir, args.resources_dir)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'Preparation failed: {error}\n')
    print(f'Prepared {counts} in {args.output_dir}')


if __name__ == '__main__':
    main()
