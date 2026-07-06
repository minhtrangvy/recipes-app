import os
import subprocess
import sys
from pathlib import Path


def load_env_file(path: str) -> None:
    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ[key] = value


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: run_with_env.py <env-file> <command> [args...]", file=sys.stderr)
        return 1

    load_env_file(sys.argv[1])
    command = [os.path.expandvars(arg) for arg in sys.argv[2:]]
    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
