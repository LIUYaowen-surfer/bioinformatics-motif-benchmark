"""Install Python dependencies pinned in eval_config.yaml; --check only verifies them."""
import argparse
from importlib.metadata import version
import json
from pathlib import Path
import re
import subprocess
import sys


def dependencies():
    config = Path(__file__).resolve().parents[1] / 'eval_config.yaml'
    # Read only the documented JSON-compatible flow list, not arbitrary YAML.
    matches = re.findall(r'^  pip_dependencies: (\[.*\])$', config.read_text(encoding='utf-8'), re.M)
    if len(matches) != 1:
        raise ValueError('Expected one pip_dependencies flow list in eval_config.yaml')
    packages = json.loads(matches[0])
    if not packages or any(not isinstance(p, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+==[0-9]+(?:\.[0-9]+)+', p) for p in packages):
        raise ValueError('Each Python dependency must have an exact numeric version')
    return packages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    packages = dependencies()
    if not args.check:
        subprocess.run([sys.executable, '-m', 'pip', 'install', *packages], check=True)
    for package in packages:
        name, expected = package.split('==')
        actual = version(name)
        if actual != expected:
            raise ValueError(f'{name}: expected {expected}, installed {actual}')
        print(f'{name}=={actual}: OK')


if __name__ == '__main__':
    main()
