"""Compare requirements.txt between two git commits, whatever the file encoding.

Usage: python scripts/compare_requirements.py OLD_COMMIT NEW_COMMIT
"""
import subprocess
import sys


def read(commit):
    raw = subprocess.check_output(["git", "show", f"{commit}:requirements.txt"])
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):      # UTF-16 (written with ">" in PowerShell 5)
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig")
    return {line.strip() for line in text.splitlines() if line.strip()}


old, new = read(sys.argv[1]), read(sys.argv[2])
print("Removed or changed (old):")
for line in sorted(old - new):
    print("   -", line)
print("Added or changed (new):")
for line in sorted(new - old):
    print("   +", line)