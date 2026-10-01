#!/usr/bin/env python3
"""Write GitHub summaries and persist a small, credential-free evidence bundle."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
out = root / '.ci-artifacts'
out.mkdir(exist_ok=True)

def emit(markdown):
    print(markdown)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as handle:
            handle.write(markdown + '\n')

def read_json(path, fallback):
    return json.loads(path.read_text()) if path.is_file() else fallback

mode = sys.argv[1]
if mode == 'tests':
    component = os.environ['COMPONENT']
    result = read_json(root / component / 'reports/unit-tests.json', {})
    coverage = read_json(root / component / 'reports/coverage/coverage-summary.json', {}).get('total', {})
    rows = [f'## {component}: unit/component tests', '', '| Metric | Result |', '| --- | --- |',
            f"| Passed | {result.get('numPassedTests', 'not run')} |",
            f"| Failed | {result.get('numFailedTests', 'not run')} |",
            f"| Skipped | {result.get('numPendingTests', 'not run')} |",
            f"| Successful | {result.get('success', False)} |"]
    seconds = sum(max(0, t.get('endTime', 0) - t.get('startTime', 0)) for t in result.get('testResults', [])) / 1000
    rows.append(f'| Test execution seconds | {seconds:.2f} |')
    for metric in ('lines', 'branches', 'functions', 'statements'):
        rows.append(f"| {metric} coverage (selected modules) | {coverage.get(metric, {}).get('pct', 'not available')}% |")
    emit('\n'.join(rows))
elif mode == 'collect':
    for filename, command in [
        ('service-status.json', ['docker', 'compose', 'ps', '--all', '--format', 'json']),
        ('service-logs.txt', ['docker', 'compose', 'logs', '--no-color', '--tail', '100']),
    ]:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        text = result.stdout + result.stderr
        secrets = root / '.secrets'
        if secrets.is_dir():
            for path in secrets.iterdir():
                if path.is_file():
                    value = path.read_text().strip()
                    if value:
                        text = text.replace(value, '[REDACTED]')
        (out / filename).write_text(text)
elif mode == 'deployment':
    record = read_json(out / 'deployment.json', {})
    record.update({'commit': os.environ.get('APP_REVISION'),
                   'rollout': os.environ.get('ROLLOUT_RESULT', 'unknown'),
                   'smoke_tests': os.environ.get('SMOKE_RESULT', 'unknown'),
                   'cleanup': os.environ.get('CLEANUP_RESULT', 'unknown')})
    record['result'] = 'success' if all(record[k] == 'success' for k in ('rollout', 'smoke_tests', 'cleanup')) else 'failure'
    record['run_url'] = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
    record['reported_utc'] = datetime.now(timezone.utc).isoformat()
    (out / 'deployment.json').write_text(json.dumps(record, indent=2) + '\n')
    smoke = (out / 'smoke-tests.txt').read_text() if (out / 'smoke-tests.txt').is_file() else ''
    count = sum(line.startswith('PASS:') for line in smoke.splitlines())
    markdown = '\n'.join([
        '## Deployment status', '', '| Metric | Result |', '| --- | --- |',
        f"| Overall | {record['result']} |", f"| Commit | `{record['commit']}` |",
        f"| Rollout | {record['rollout']} |", f"| API verification | {record['smoke_tests']} |",
        f"| Passed API checks | {count} |", f"| Startup seconds | {record.get('startup_seconds', 'not reached')} |",
        f"| Health | {record.get('health', {}).get('status', 'not reached')} |",
        f"| Cleanup | {record['cleanup']} |", '',
        'The application was deployed on this runner. The environment is removed after verification; this is not a persistent public website.',
    ])
    (out / 'deployment-summary.md').write_text(markdown + '\n')
    emit(markdown)
elif mode == 'workflow':
    needs = json.loads(os.environ['NEEDS_JSON'])
    rows = ['## Task 3 pipeline status', '', '| Stage | Outcome |', '| --- | --- |']
    rows.extend(f"| {name} | {value['result']} |" for name, value in needs.items())
    rows += ['', 'Build requires successful lint/tests. Deployment requires successful quality and build jobs.',
             'Pushes and manual runs deploy a temporary test stack. Pull requests run quality and build checks.']
    emit('\n'.join(rows))
else:
    raise SystemExit('Usage: report.py tests|collect|deployment|workflow')
