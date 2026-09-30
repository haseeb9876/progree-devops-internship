#!/usr/bin/env python3
"""Capture only non-secret operational evidence from the running local stack."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
out = root / 'docs/task-2/evidence'
out.mkdir(parents=True, exist_ok=True)
def run(*args):
    return subprocess.check_output(args, cwd=root, text=True).strip()

services = []
for identifier in run('docker', 'compose', 'ps', '-q').splitlines():
    info = json.loads(run('docker', 'inspect', identifier))[0]
    service = info['Config']['Labels']['com.docker.compose.service']
    assert info['State']['Health']['Status'] == 'healthy', service
    ports = info['HostConfig'].get('PortBindings') or {}
    if service != 'frontend':
        assert not ports, f'{service} unexpectedly publishes a host port'
    else:
        assert all(p['HostIp'] == '127.0.0.1' for bindings in ports.values() for p in bindings)
    if service in ('frontend', 'backend', 'redis'):
        assert info['Config']['User'] not in ('', 'root', '0')
        assert info['HostConfig']['ReadonlyRootfs']
    assert all(not m['RW'] for m in info['Mounts'] if m['Destination'].startswith('/run/secrets/'))
    services.append({'service': service, 'health': info['State']['Health']['Status'],
                     'runtime_user': info['Config']['User'], 'published_ports': ports,
                     'read_only_rootfs': info['HostConfig']['ReadonlyRootfs'],
                     'networks': sorted(info['NetworkSettings']['Networks']),
                     'image_id': info['Image']})
assert len(services) == 4
network_name = next(n for s in services if s['service'] == 'mongodb' for n in s['networks'])
assert json.loads(run('docker', 'network', 'inspect', network_name))[0]['Internal']
run('docker', 'compose', 'exec', '-T', 'backend', 'sh', '-c',
    'test ! -e /run/secrets/mongo_root_password')
redis_response = run('docker', 'compose', 'exec', '-T', 'redis', 'redis-cli', 'ping')
assert 'NOAUTH' in redis_response
run('docker', 'compose', 'exec', '-T', 'mongodb', 'mongosh', '--quiet', '--eval',
    "try {db.getSiblingDB('wanderlust').posts.findOne(); quit(1)} catch(e) {quit(e.code === 13 ? 0 : 1)}")

secret_values = [p.read_bytes().strip() for p in (root / '.secrets').iterdir() if p.is_file()]
paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=root).split(b'\0')
for raw in paths:
    if raw:
        path = root / raw.decode()
        if path.is_file():
            data = path.read_bytes()
            assert not any(value in data for value in secret_values), f'Credential found in {path.name}'
for tag in ('progree-wanderlust-backend:task2', 'progree-wanderlust-frontend:task2'):
    data = run('docker', 'image', 'inspect', tag).encode()
    data += run('docker', 'history', '--no-trunc', tag).encode()
    assert not any(value in data for value in secret_values)

rows = []
for tag in ('progree-wanderlust-backend:baseline', 'progree-wanderlust-backend:task2',
            'progree-wanderlust-frontend:build-stage', 'progree-wanderlust-frontend:task2'):
    info = json.loads(run('docker', 'image', 'inspect', tag))[0]
    rows.append({'image': tag, 'size_bytes': info['Size'], 'id': info['Id']})
(out / 'image-sizes.json').write_text(json.dumps(rows, indent=2) + '\n')
(out / 'container-status.json').write_text(json.dumps({'captured_utc': datetime.now(timezone.utc).isoformat(), 'services': services}, indent=2) + '\n')
checks = [
    'All four services are healthy.',
    'Only the frontend publishes a host port, bound to 127.0.0.1.',
    'The database/cache network is internal.',
    'Frontend, backend, and Redis use non-root users and read-only root filesystems.',
    'Secret mounts are read-only; the backend cannot read the MongoDB root password.',
    'MongoDB rejects unauthenticated data queries; Redis rejects unauthenticated PING.',
    'Generated secrets are absent from Git-eligible files and runtime image configuration/history.',
]
text = '\n'.join('PASS: ' + check for check in checks) + '\n'
(out / 'configuration-checks.txt').write_text(text)
print(text, end='')
