# Task 3 verification evidence

## Successful remote push

- [Open successful run](https://github.com/haseeb9876/progree-devops-internship/actions/runs/36829758268)
- Commit: `dd36bc884d8e66c7e803f96a4be21cd5972f14c7`
- Event: `push`
- Result: **success**
- Backend unit tests: **28 passed**.
- Frontend unit/component tests: **12 passed**.
- Application startup and revision verification: **30.16 seconds**.
- Live application checks: **7 passed**.
- Cleanup: **success**.

The build job produced the images consumed by a separate deployment job. Image
IDs, revision labels, and the API health endpoint were checked against the
triggering commit. The test environment was removed after verification.

## Deliberate failure demonstration

- [Open failed run](https://github.com/haseeb9876/progree-devops-internship/actions/runs/36830344712)
- Commit: `d1ee9f1216608ef06913ec9aedb407b089fafe8b`
- Event: `push`
- Result: **expected failure**.
- Backend tests: **28 passed, 1 deliberately failed**.
- Frontend checks: **passed**.
- Build: **skipped**.
- Deployment: **skipped**.

The demonstration branch was eligible for deployment under the same push trigger;
its downstream stages were blocked by the failed quality job. The deliberately
incorrect test was reverted afterward and was never merged into main.

## Verified recovery

After reverting the deliberate failure, [run 36830587646](https://github.com/haseeb9876/progree-devops-internship/actions/runs/36830587646)
passed linting, all tests, image build, deployment verification, and cleanup.

## Saved files

- `successful-run.json` and `failed-run.json`: GitHub run/job/step metadata.
- `backend-tests.json`, `frontend-tests.json`: actual test counts and selected-module coverage.
- `failure-test-summary.json`: the intentional test failure.
- `deployment/`: real deployment metadata, image IDs, smoke-test output, service status, and redacted logs.

GitHub artifacts have retention limits. These saved records preserve the evidence
in the repository; the linked GitHub runs remain the source for the execution
history. This is a temporary runner deployment, not an always-on hosted website.
