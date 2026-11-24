"""Lightweight HOMER GC/1-3-mer background-weight replay; no motif search.

Port of the rules in HOMER freq2group.pl, assignGeneWeights.pl and
Motif2.cpp SequenceArray::normalizeSequence[Iteration]. Source hashes are
recorded in the accompanying audit. Source code is inspected, not executed.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import argparse
import bisect
import collections
import hashlib
import json
from pathlib import Path
import numpy as np


def read_fasta(path):
    records = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('>'):
            records.append([line[1:].split()[0], ''])
        else:
            records[-1][1] += line.strip().upper()
    return records


def run(root, gc_mode='acgt'):
    paths = [root / 'task_01/input' / f'{side}_sequences.fasta' for side in ['target', 'background']]
    records = [read_fasta(path) for path in paths]
    boundaries = [.2, .25, .3, .35, .4, .45, .5, .6, .7, .8]
    bins = []
    poor = []
    for side in records:
        bb = []
        for name, seq in side:
            if len(seq) < 5 or len(seq) > 100000 or seq.count('N') / len(seq) > .7:
                poor.append(name)
            denominator = len(seq) - seq.count('N') if gc_mode == 'acgt' else len(seq)
            # homerTools writes GC frequencies to a text file; rounding is
            # reproduced below after checking the format in SeqTag.cpp.
            gc = float(f'{(seq.count("G") + seq.count("C")) / denominator:.6f}')
            bb.append(bisect.bisect_right(boundaries, gc))
        bins.append(bb)
    counts = [collections.Counter(b) for b in bins]
    if poor:
        raise ValueError('This scoped replay expects the audited inputs with no poor-sequence exclusions')
    active = sorted(b for b in set(bins[0]) | set(bins[1]) if counts[0][b] >= 1 and counts[1][b] >= 1)
    nt = sum(counts[0][b] for b in active)
    nb = sum(counts[1][b] for b in active)
    excluded = [name for (name, seq), b in zip(records[1], bins[1]) if b not in active]
    selected = [[(name, seq, b) for (name, seq), b in zip(side, bside) if b in active] for side, bside in zip(records, bins)]
    weights = np.array([float(f'{(counts[0][b] / nt * nb / counts[1][b]):.5f}') for name, seq, b in selected[1]])
    initial_sum = float(weights.sum())
    lookup = np.full(256, -1, dtype=np.int32)
    lookup[[65, 67, 71, 84]] = [0, 1, 2, 3]
    matrices = []
    for k in [1, 2, 3]:
        mats = []
        for side in selected:
            matrix = np.zeros((len(side), 4 ** k), dtype=np.float64)
            for i, (name, seq, b) in enumerate(side):
                digits = lookup[np.frombuffer(seq.encode('ascii'), dtype=np.uint8)]
                # Preserve the upstream j < length-curLen boundary exactly.
                size = len(seq) - k
                codes = np.zeros(size, dtype=np.int32)
                valid = np.ones(size, dtype=bool)
                for j in range(k):
                    part = digits[j:j + size]
                    valid &= part >= 0
                    codes += part * (4 ** j)
                counts_k = np.bincount(codes[valid], minlength=4 ** k)
                assert counts_k.sum() > 0
                matrix[i] = counts_k / counts_k.sum()
            mats.append(matrix)
        reverse = []
        for code in range(4 ** k):
            digits = [(code // 4 ** j) % 4 for j in range(k)]
            reverse.append(sum((3 - d) * 4 ** j for j, d in enumerate(reversed(digits))))
        matrices.append((mats[0].sum(axis=0), mats[1], np.array(reverse)))
    print('Prepared small k-mer frequency matrices', flush=True)

    def iteration(w):
        error = 0.
        for target, background, rev in matrices:
            back = w @ background
            total_t, total_b = target.sum(), back.sum()
            t = np.maximum((target + target[rev]) / 2, .5 / total_t)
            b = np.maximum((back + back[rev]) / 2, .5 / total_b)
            factors = total_b * t / total_t / b
            error += float(np.mean((factors - 1) ** 2))
            new = np.clip(w * (background @ factors), .001, 1000.)
            penalty = np.maximum(new, 1 / new) ** 2
            delta = new - w
            damp = ((delta > 0) & (new > 1)) | ((delta < 0) & (new < 1))
            w = w + np.where(damp, delta / penalty, delta)
        return w, error

    last = 1e100
    history = []
    for i in range(160):
        weights, err = iteration(weights)
        history.append({'iteration': i + 1, 'error': err, 'background_weight_sum': float(weights.sum())})
        if err >= last:
            break
        last = err
    weights, err = iteration(weights)  # Upstream performs a final reporting iteration.
    rounded = np.array([float(f'{w:.6f}') for w in weights])
    table = json.loads((Path(__file__).resolve().parents[1] / 'task_01/reference/author_results.json').read_text(encoding='utf-8'))
    lower, upper, usable_rows = 0., float('inf'), 0
    for motif in table['motifs']:
        hits = motif['background_sequences_with_motif']
        fraction = motif['pct_background_sequences_with_motif']
        if fraction > .00005:
            lower = max(lower, (hits - .05) / (fraction + .00005))
            upper = min(upper, (hits + .05) / (fraction - .00005))
            usable_rows += 1
    return {
        'method': 'Source-rule replay of HOMER GC weighting and 1-3-mer normalization only',
        'gc_denominator': gc_mode,
        'input_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'raw_target_sequences': len(records[0]), 'raw_background_sequences': len(records[1]),
        'poor_sequence_filter_ids': poor,
        'gc_bins': [{'bin': b, 'target': counts[0][b], 'background': counts[1][b], 'retained': b in active} for b in range(11)],
        'unsupported_gc_bin_background_ids': excluded,
        'retained_target_sequences': nt, 'retained_background_sequences': nb,
        'initial_gc_background_weight_sum': initial_sum,
        'normalization_iterations': len(history),
        'final_background_weight_sum': float(weights.sum()),
        'group_file_6_decimal_weight_sum': float(rounded.sum()),
        'iteration_history': history,
        'author_table_denominator_check': {
            'usable_rows': usable_rows, 'lower_bound': lower, 'upper_bound': upper,
            'replayed_weight_sum_in_interval': lower <= float(rounded.sum()) <= upper,
        },
        'scope': 'No motif scanning, discovery, or p-value analysis was run. No BED/FASTA was changed.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--gc-mode', choices=['acgt', 'total'], default='acgt')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run(args.root, args.gc_mode)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'iteration_history'}, indent=2))
