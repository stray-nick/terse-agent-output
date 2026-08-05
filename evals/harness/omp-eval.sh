#!/usr/bin/env python3
"""Eval-runner shim: cap each omp invocation so an intermittent hang
(observed in ~10% of -p runs) fails fast and lets the harness retry.
Also close stdin (DEVNULL) so omp uses the positional prompt arg instead
of blocking forever waiting for piped-stdin EOF on some cases."""
import subprocess
import sys

try:
    completed = subprocess.run(
        ["omp", *sys.argv[1:]],
        timeout=600,
        stdin=subprocess.DEVNULL,
        check=False,
    )
    sys.exit(completed.returncode)
except subprocess.TimeoutExpired:
    sys.exit(124)
