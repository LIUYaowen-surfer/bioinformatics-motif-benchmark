"""Rebuild the pinned 309-motif RSAT Cis-BP mirror; no enrichment analysis."""
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def convert(data):
    records = []
    with localcontext() as context:
        context.prec = 28
        for block in data.decode('utf-8').split('//'):
            if not block.strip():
                continue
            ids = re.findall(r'^AC\s+(M\d+_1\.02)\s*$', block, re.M)
            if len(ids) != 1 or not re.search(r'^P0\s+A\s+C\s+G\s+T\s*$', block, re.M):
                raise ValueError('Invalid accession or alphabet')
            rows = []
            for line in block.splitlines():
                fields = line.split()
                if fields and fields[0].isdigit():
                    if len(fields) != 5 or int(fields[0]) != len(rows) + 1:
                        raise ValueError('Invalid matrix row')
                    nums = [Decimal(x) for x in fields[1:]]
                    if any(not x.is_finite() or x < 0 for x in nums) or sum(nums) <= 0:
                        raise ValueError('Invalid matrix values')
                    rows.append([x / sum(nums) for x in nums])
            if not rows:
                raise ValueError('Empty matrix')
            records.append((ids[0], rows))
    if len(records) != 309 or len({r[0] for r in records}) != 309:
        raise ValueError('Expected 309 unique motifs')
    lines = ['MEME version 4', '', 'ALPHABET= ACGT', '', 'strands: + -', '']
    for name, rows in records:
        lines += ['MOTIF ' + name, 'letter-probability matrix: alength= 4 w= ' + str(len(rows))]
        lines += [' '.join(format(x, '.12f') for x in row) for row in rows]
        lines += ['']
    return ('\n'.join(lines) + '\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-file', type=Path, help='Use an existing pinned TRANSFAC file instead of downloading')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('Output directory already exists; choose a new directory')
    manifest_bytes = (ROOT / 'resources/cisbp/resource_manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    if args.source_file:
        data = args.source_file.read_bytes()
    else:
        with urllib.request.urlopen(manifest['source_url'], timeout=60) as response:
            data = response.read()
    if hashlib.sha256(data).hexdigest() != manifest['source_file']['sha256']:
        raise ValueError('Source hash mismatch; do not silently substitute a newer database')
    meme = convert(data)
    if hashlib.sha256(meme).hexdigest() != manifest['files']['motifs.meme']['sha256']:
        raise ValueError('Converted database hash mismatch')
    args.output_dir.mkdir(parents=True)
    (args.output_dir / 'motifs.meme').write_bytes(meme)
    (args.output_dir / 'resource_manifest.json').write_bytes(manifest_bytes)
    print('Prepared 309 motifs; source and converted SHA-256 verified.')


if __name__ == '__main__':
    main()
