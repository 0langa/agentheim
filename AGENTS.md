Repository agent rule:

Before finishing any work, update files in `devtest/` so local test runner and command list reflect current repository test structure and recommended execution paths.

AI live connectivity test rule:

Agents may run `devtest/ai_test.ps1` at most 2 times in a row for the same validation attempt.
If run #2 fails, stop retrying and report failure.

Timeout policy:

Each `devtest/ai_test.ps1` run must use a hard timeout of 2 minutes (120 seconds).
If timeout is hit, treat as failed attempt.
