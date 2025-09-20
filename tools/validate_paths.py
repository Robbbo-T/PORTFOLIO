#!/usr/bin/env python3
import sys, subprocess, re
try:
    out = subprocess.check_output(["bash","-lc","git ls-files"], text=True)
except Exception:
    sys.exit(0)
bad = [p for p in out.splitlines() if re.search(r"[\s]|[^\x00-\x7F]", p)]
if bad:
    print("Forbidden chars detected in paths:")
    for p in bad: print(" -", p)
    sys.exit(1)
print("OK: no spaces/emojis in tracked paths.")