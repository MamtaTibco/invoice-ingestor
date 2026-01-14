## `alt.Dockerfile` - Workflow Testing

The `alt.Dockerfile` is a lightweight, alternative Dockerfile designed to test
the x35 reusable docker-build workflow for cases that use a custom Dockerfile path,
rather than the default `Dockerfile` provided by `x35-actions`.

The test workflow is in this repository at [`.github/workflows/alt-dockerfile-test.yaml`](../../.github/workflows/alt-dockerfile-test.yaml).

### Triggering a Build

1. From a feature branch, introduce a change to the `ENV TAINT` value in `alt.Dockerfile` to force a rebuild:
```dockerfile
   ENV TAINT="2025-01-27T13:45:00"  # Update to trigger the workflow
```
2. Open a  pull request against `main` to trigger the test workflow.
