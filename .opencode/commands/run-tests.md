---
description: Run pytest for this project and report results. Optionally filter by test file or test name.
---

Run the tests for this project.

$ARGUMENTS

Steps:
1. Run `cd src && uv run pytest tests/ -v $ARGUMENTS` and capture the output
2. Report how many tests passed, failed, or errored
3. For any failures, show the full error and suggest a fix
