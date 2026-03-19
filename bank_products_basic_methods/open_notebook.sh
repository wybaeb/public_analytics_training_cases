#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
../.venv/bin/jupyter lab bank_products_basic_methods_walkthrough.ipynb
