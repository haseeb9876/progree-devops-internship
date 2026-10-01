#!/usr/bin/env python3
"""Deploy the actual Compose stack; record startup timing and commit identity."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

root = Path(__file__).resolve().parents[2]
out = root / '.ci-artifacts'
out.mkdir(exist_ok=True)
assert os.environ.get('COMPOSE_PROJECT_NAME', '').startswith('progree-ci-'), 'Use an isolated progree-ci-* project'
revision = os.environ['APP_REVISION']
started = time.monotonic()
record = {'commit': revision, 'started_utc': datetime.now(timezone.utc).isoformat(),
          'environment': 'temporary GitHub-hosted test deployment', 'rollout': 'failure'}
try:
    subprocess.run(['python3', 'scripts/setup-local.py'], cwd=root, check=True)
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        for path in (root / '.secrets').iterdir():
            if path.is_file():
                print('::add-mask::' + path.read_text().strip(), flush=True)
    subprocess.run(['docker', 'compose', 'up', '-d', '--no-build', '--wait', '--wait-timeout', '180'], cwd=root, check=True)
    subprocess.run(['python3', 'scripts/ci/images.py', 'verify'], cwd=root, check=True)
    port = os.environ.get('WEB_PORT', '8080')
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/health/live', timeout=10) as response:
        live = json.load(response)
    assert live['revision'] == revision, 'API is serving a different commit'
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/health/ready', timeout=10) as response:
        record['health'] = json.load(response)
    assert record['health']['status'] == 'ready'
    record['rollout'] = 'success'
    print('PASS: Deployed API serves the exact pushed commit and dependencies are ready.')
finally:
    record['startup_seconds'] = round(time.monotonic() - started, 2)
    record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    (out / 'deployment.json').write_text(json.dumps(record, indent=2) + '\n')
