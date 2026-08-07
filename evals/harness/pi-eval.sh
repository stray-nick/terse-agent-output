#!/usr/bin/env python3
"""Eval-runner shim for pi: cap each invocation (timeout, DEVNULL stdin)."""
import subprocess, sys
try:
    completed = subprocess.run(
        ["pi", *sys.argv[1:]],
        timeout=600,
        stdin=subprocess.DEVNULL,
        check=False,
    )
    sys.exit(completed.returncode)
except subprocess.TimeoutExpired:
    sys.exit(124)
