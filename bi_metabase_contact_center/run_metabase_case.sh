#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || true)}"
if [ -z "$PYTHON_BIN" ]; then
  echo "python3 не найден. Установите Python 3 и повторите запуск." >&2
  exit 1
fi

chmod +x postgres/init/02_load.sh

if ! "$PYTHON_BIN" - <<'PY'
import subprocess, sys
try:
    subprocess.run(['docker', 'ps'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=True)
except Exception:
    sys.exit(1)
PY
then
  open -a Docker || true
  echo "Waiting for Docker Desktop..."
  "$PYTHON_BIN" - <<'PY'
import subprocess
import sys
import time

for _ in range(60):
    try:
        subprocess.run(['docker', 'ps'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=True)
        print('Docker is ready')
        raise SystemExit(0)
    except Exception:
        time.sleep(5)

print('Docker daemon is still unavailable after waiting.', file=sys.stderr)
raise SystemExit(1)
PY
fi

docker compose up -d
"$PYTHON_BIN" setup_metabase_case.py

RUNTIME_VALUES="$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path

runtime = json.loads(Path("artifacts/metabase_runtime.json").read_text(encoding="utf-8"))
print("\t".join([
    runtime["admin_url"],
    runtime["public_url"],
    runtime["admin_email"],
    runtime["admin_password"],
]))
PY
)"
IFS=$'\t' read -r ADMIN_URL PUBLIC_URL ADMIN_EMAIL ADMIN_PASSWORD <<<"$RUNTIME_VALUES"

echo "Metabase готов."
echo "Конструктор дашборда: $ADMIN_URL"
echo "Публичный просмотр: $PUBLIC_URL"
echo "Логин: $ADMIN_EMAIL"
echo "Пароль: $ADMIN_PASSWORD"
open "$ADMIN_URL"
