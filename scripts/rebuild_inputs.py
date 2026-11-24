"""Rebuild sequence inputs from pinned author tables/BED/BSgenome; no motif analysis."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import tarfile
import tempfile
import openpyxl

ROOT = Path(__file__).resolve().parents[1]


def check(downloads, name):
    spec = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))['files'][name]
    path = downloads / name
    with path.open('rb') as stream:
        value = hashlib.file_digest(stream, 'sha256').hexdigest()
    if value != spec['sha256']:
        raise ValueError(f'Unreviewed source hash: {name}')
    return path


class TwoBit:
    def __init__(self, archive):
        with tarfile.open(archive, 'r:gz') as stream:
            members = [m for m in stream.getmembers() if m.name.endswith('/single_sequences.2bit')]
            if len(members) != 1:
                raise ValueError('Expected one genome 2bit member')
            self.data = stream.extractfile(members[0]).read()
        self.endian = '>' if struct.unpack_from('>I', self.data)[0] == 0x1A412743 else '<'
        signature, version, count, reserved = self.ints(0, 4)
        if signature != 0x1A412743 or version != 0:
            raise ValueError('Unsupported 2bit format')
        pos, index = 16, {}
        for _ in range(count):
            length = self.data[pos]
            name = self.data[pos + 1:pos + 1 + length].decode('ascii')
            pos += length + 1
            index[name] = self.ints(pos)[0]
            pos += 4
        self.contigs = {}
        for name, off in index.items():
            length, ncount = self.ints(off, 2)
            pos = off + 8
            starts = self.ints(pos, ncount)
            pos += ncount * 4
            sizes = self.ints(pos, ncount)
            pos += ncount * 4
            masks = self.ints(pos)[0]
            pos += 4 + masks * 8 + 4
            self.contigs[name] = length, list(zip(starts, sizes)), pos
        self.lookup = [''.join('TCAG'[(value >> shift) & 3] for shift in [6, 4, 2, 0]) for value in range(256)]

    def ints(self, pos, count=1):
        return struct.unpack_from(self.endian + str(count) + 'I', self.data, pos) if count else ()

    def sequence(self, chromosome, start, end):
        length, blocks, offset = self.contigs[chromosome]
        if not 0 <= start < end <= length:
            raise ValueError('Out-of-bounds BED interval')
        text = ''.join(self.lookup[b] for b in self.data[offset + start // 4:offset + (end + 3) // 4])
        seq = list(text[start % 4:start % 4 + end - start])
        for a, size in blocks:
            left, right = max(a, start), min(a + size, end)
            if left < right:
                seq[left - start:right - start] = 'N' * (right - left)
        return ''.join(seq)


def write_record(out, header, seq):
    if not seq or set(seq) - set('ACGTN'):
        raise ValueError('Invalid author sequence')
    out.write('>' + header + '\n' + '\n'.join(seq[i:i + 60] for i in range(0, len(seq), 60)) + '\n')


def hydra(downloads, output):
    table = check(downloads, 'hydra/elife-60562-supp1-v2.xlsx')
    peaks = check(downloads, 'hydra/GSE152994_untreated_consensus_diffbind_labels.bed.gz')
    archive = check(downloads, 'hydra/BSgenome.Hymag.NIH.Hymag2_2.0.tar.gz')
    wb = openpyxl.load_workbook(table, read_only=True, data_only=True)
    up, ordered = set(), []
    for sheet in ['H3H0', 'F3F0']:
        rows = wb[sheet].iter_rows(values_only=True)
        header = list(next(rows))
        indexes = [header.index(c) for c in ['Peak ID', 'log2FC', 'False Discovery Rate']]
        for row in rows:
            pid, fc, fdr = [row[i] for i in indexes]
            if pid is None:
                continue
            if sheet == 'H3H0':
                ordered.append(int(pid))
            if fdr is not None and fc is not None and float(fdr) <= 1e-4 and float(fc) > 0:
                up.add(int(pid))
    wb.close()
    coords = {}
    with gzip.open(peaks, 'rt') as stream:
        for line in stream:
            cells = line.rstrip().split('\t')
            try:
                pid = int(cells[3])
            except (IndexError, ValueError):
                continue
            if pid in coords:
                raise ValueError('Duplicate author peak ID')
            coords[pid] = cells[0], int(cells[1]), int(cells[2])
    genome = TwoBit(archive)
    for role, selected in [('target', True), ('background', False)]:
        with (output / f'{role}_peaks.bed').open('w', encoding='ascii', newline='\n') as bed, (output / f'{role}_sequences.fasta').open('w', encoding='ascii', newline='\n') as fasta:
            for pid in ordered:
                if (pid in up) != selected:
                    continue
                chromosome, start, end = coords[pid]
                bed.write(f'{chromosome}\t{start}\t{end}\t{pid}\t0\t.\n')
                write_record(fasta, f'{pid} {chromosome}:{start}-{end}', genome.sequence(chromosome, start, end))


def arabidopsis(downloads, output):
    wb = openpyxl.load_workbook(check(downloads, 'arabidopsis/NIHMS1584062-supplement-Table_S4.xlsx'), read_only=True, data_only=True)
    values = [str(row[1]).strip() for row in wb['Sequences'].iter_rows(min_row=2, values_only=True) if row[1] is not None and str(row[1]).strip()]
    wb.close()
    if len(values) % 2:
        raise ValueError('Unpaired header/sequence cell')
    with (output / 'target_sequences.fasta').open('w', encoding='ascii', newline='\n') as out:
        for header, seq in zip(values[::2], values[1::2]):
            if not header.startswith('>'):
                raise ValueError('Missing author FASTA header')
            write_record(out, header[1:], seq)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--task', choices=['all', 'task_01', 'task_02'], default='all')
    args = parser.parse_args()
    output, source = args.output_dir.resolve(), args.downloads.resolve()
    try:
        if output.exists() or output == source or source.is_relative_to(output) or output.is_relative_to(source):
            raise ValueError('Use a new output outside the source directory')
        expected = json.loads((ROOT / 'inputs.json').read_text(encoding='utf-8'))
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output.parent) as temp:
            stage = Path(temp) / 'prepared'
            for task, builder in [('task_01', hydra), ('task_02', arabidopsis)]:
                if args.task not in ['all', task]:
                    continue
                folder = stage / task / 'input'
                folder.mkdir(parents=True)
                builder(source, folder)
                for role, spec in expected[task].items():
                    f = folder / f'{role}_sequences.fasta'
                    if hashlib.sha256(f.read_bytes()).hexdigest() not in spec['accepted_sha256']:
                        raise ValueError(f'Rebuilt sequence differs from reviewed input: {task}/{role}')
            stage.rename(output)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'Rebuild failed: {error}\n')
    print(f'Verified inputs rebuilt in {output}')


if __name__ == '__main__':
    main()
