"""Count exact Top-10 motif-ID overlap; print one integer from 0 to 10."""
import argparse
import json
from pathlib import Path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f'Non-standard JSON number: {value}')


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def ids(value, label):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x or x != x.strip() for x in value):
        raise ValueError(f'{label}: expected an array of nonempty strings without surrounding whitespace')
    if len(set(value)) != len(value):
        raise ValueError(f'{label}: duplicate IDs')
    return set(value)


def score(prediction, reference):
    for label, data in [('Prediction', prediction), ('Reference', reference)]:
        if not isinstance(data, dict) or set(data) != {'ids'}:
            raise ValueError(f'{label} must contain exactly the key "ids"')
    predicted, expected = ids(prediction['ids'], 'Prediction'), ids(reference['ids'], 'Reference')
    if len(predicted) != 10 or len(expected) != 10:
        raise ValueError('Prediction and reference must each contain exactly 10 unique IDs')
    return len(predicted & expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prediction', type=Path)
    parser.add_argument('reference', type=Path)
    args = parser.parse_args()
    try:
        result = score(load_json(args.prediction), load_json(args.reference))
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f'Error: {error}\n')
    print(result)


if __name__ == '__main__':
    main()
