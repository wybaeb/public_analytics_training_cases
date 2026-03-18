#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

REPORT_PATH="$SCRIPT_DIR/artifacts/cluster_report.html"
if [ ! -f "$REPORT_PATH" ]; then
  echo "Не найден файл отчета: $REPORT_PATH" >&2
  exit 1
fi

REPORT_URL="file://$REPORT_PATH"
echo "Открываю HTML-отчет: $REPORT_URL"
open "$REPORT_URL"
