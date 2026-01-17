# GitHub Actions Workflows

This directory contains GitHub Actions workflows for continuous integration.

## Workflows

### `ci.yml` - Main CI Checks
Runs on every push and pull request to `main`, `master`, or `develop` branches.

**What it does:**
- Runs `make check` which executes:
  - `make lint` - Runs `ruff check .` and `pylint app`
  - `make typecheck` - Runs `mypy app`
  - `make test` - Runs `pytest`

**Python versions tested:** 3.10, 3.11, 3.12

### `format-check.yml` - Code Formatting Check
Runs on every push and pull request to check code formatting.

**What it does:**
- Checks if code is properly formatted using `ruff format --check .`

**Note:** To format code locally, run `make format`

## Local Development

Before pushing, you can run the same checks locally:

```bash
# Run all checks (lint, typecheck, test)
make check

# Run individual checks
make lint      # Linting
make typecheck # Type checking
make test      # Tests
make format    # Format code
```

## Workflow Status

You can view the status of these workflows in the "Actions" tab of your GitHub repository.
