#!/usr/bin/env python3
"""Configure a local Metabase demo for the contact-center BI case."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
RUNTIME_PATH = ARTIFACTS_DIR / "metabase_runtime.json"
METABASE_URL = "http://localhost:3000"
ADMIN_EMAIL = "sber-workshop@example.local"
ADMIN_PASSWORD = "SberWorkshop2026!"
ADMIN_FIRST = "Sber"
ADMIN_LAST = "Workshop"
DB_NAME = "Речевая аналитика контакт-центра"


CARD_SPECS = [
    {
        "name": "Выручка по неделям",
        "display": "line",
        "description": "Как меняется выручка по мере внедрения обучения на основе речевой аналитики.",
        "query": """
SELECT
  week_start,
  SUM(sales_revenue_rub) AS "Выручка, руб."
FROM contact_center_training
GROUP BY 1
ORDER BY 1
""".strip(),
        "row": 0,
        "col": 0,
        "sizeX": 12,
        "sizeY": 6,
    },
    {
        "name": "Ошибки ИИ и отклонения супервайзера",
        "display": "line",
        "description": "Кривая обучения модели: со временем супервайзер отклоняет меньшую долю находок ИИ.",
        "query": """
SELECT
  week_start,
  SUM(ai_errors_detected) AS "Найдено ИИ",
  SUM(supervisor_rejected_errors) AS "Отклонено супервайзером"
FROM contact_center_training
GROUP BY 1
ORDER BY 1
""".strip(),
        "row": 0,
        "col": 12,
        "sizeX": 12,
        "sizeY": 6,
    },
    {
        "name": "Командный срез для коучинга",
        "display": "table",
        "description": "Актуальный срез по командам для коучинговых обсуждений.",
        "query": """
SELECT
  team AS "Команда",
  ROUND(AVG(adherence_score) * 100, 1) AS "Следование рекомендациям, %",
  ROUND(AVG(qa_score), 1) AS "Средний QA score",
  ROUND(SUM(sales_revenue_rub), 0) AS "Выручка, руб.",
  ROUND(SUM(supervisor_rejected_errors)::numeric / NULLIF(SUM(ai_errors_detected), 0) * 100, 1) AS "Отклонено, %"
FROM contact_center_training
WHERE week_start = (SELECT MAX(week_start) FROM contact_center_training)
GROUP BY 1
ORDER BY "Выручка, руб." DESC
""".strip(),
        "row": 6,
        "col": 0,
        "sizeX": 12,
        "sizeY": 5,
    },
    {
        "name": "Эффект обучения на выручку",
        "display": "line",
        "description": "По неделям видно, как вместе растут применение рекомендаций в работе и выручка команды.",
        "query": """
WITH weekly AS (
  SELECT
    week_start,
    AVG(adherence_score) * 100 AS adherence_pct,
    AVG(sales_revenue_rub) AS revenue_rub
  FROM contact_center_training
  GROUP BY 1
),
baseline AS (
  SELECT
    MIN(week_start) AS first_week
  FROM weekly
),
base_values AS (
  SELECT
    w.adherence_pct AS base_adherence_pct,
    w.revenue_rub AS base_revenue_rub
  FROM weekly w
  CROSS JOIN baseline b
  WHERE w.week_start = b.first_week
)
SELECT
  w.week_start,
  ROUND(w.adherence_pct, 1) AS "Следование рекомендациям, %",
  ROUND(w.revenue_rub, 0) AS "Средняя выручка, руб.",
  ROUND(w.adherence_pct / NULLIF(b.base_adherence_pct, 0) * 100, 1) AS "Индекс следования, неделя 1 = 100",
  ROUND(w.revenue_rub / NULLIF(b.base_revenue_rub, 0) * 100, 1) AS "Индекс выручки, неделя 1 = 100"
FROM weekly w
CROSS JOIN base_values b
ORDER BY 1
""".strip(),
        "row": 6,
        "col": 12,
        "sizeX": 12,
        "sizeY": 4,
    },
    {
        "name": "Корреляция следования и выручки",
        "display": "scalar",
        "description": "Коэффициент корреляции Пирсона между недельным уровнем следования рекомендациям и средней выручкой.",
        "query": """
WITH weekly AS (
  SELECT
    week_start,
    AVG(adherence_score) AS adherence_score_avg,
    AVG(sales_revenue_rub) AS revenue_rub_avg
  FROM contact_center_training
  GROUP BY 1
)
SELECT
  ROUND(CORR(adherence_score_avg, revenue_rub_avg)::numeric, 3) AS "Коэффициент корреляции"
FROM weekly
""".strip(),
        "row": 10,
        "col": 12,
        "sizeX": 12,
        "sizeY": 1,
    },
]


def database_details() -> dict:
    return {
        "host": "db",
        "port": 5432,
        "dbname": "bank_training",
        "user": "bank_user",
        "password": "bank_pass",
        "ssl": False,
        "tunnel-enabled": False,
    }


def api_request(path: str, method: str = "GET", payload: dict | None = None, session_id: str | None = None):
    headers = {"Content-Type": "application/json"}
    if session_id:
        headers["X-Metabase-Session"] = session_id
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(f"{METABASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def wait_for_metabase() -> None:
    deadline = time.time() + 420
    while time.time() < deadline:
        try:
            api_request("/api/health")
            return
        except Exception:
            time.sleep(5)
    raise TimeoutError("Metabase did not start within 7 minutes.")


def maybe_run_initial_setup() -> None:
    props = api_request("/api/session/properties")
    setup_token = props.get("setup-token")
    is_setup = props.get("is-setup")
    if is_setup or not setup_token:
        return
    payload = {
        "token": setup_token,
        "prefs": {"allow_tracking": False, "site_name": "Sber BI Workshop"},
        "user": {
            "first_name": ADMIN_FIRST,
            "last_name": ADMIN_LAST,
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "site_name": "Sber BI Workshop",
        },
        "database": {
            "engine": "postgres",
            "name": DB_NAME,
            "is_full_sync": True,
            "auto_run_queries": True,
            "details": database_details(),
        },
    }
    try:
        api_request("/api/setup", method="POST", payload=payload)
    except RuntimeError as exc:
        if "The /api/setup route can only be used to create the first user" not in str(exc):
            raise
    time.sleep(5)


def login() -> str:
    response = api_request(
        "/api/session",
        method="POST",
        payload={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    return response["id"]


def ensure_database_id(session_id: str) -> int:
    databases = api_request("/api/database", session_id=session_id)
    items = databases if isinstance(databases, list) else databases.get("data", [])
    for db in items:
        if db.get("name") == DB_NAME:
            return db["id"]
    payload = {
        "engine": "postgres",
        "name": DB_NAME,
        "is_full_sync": True,
        "auto_run_queries": True,
        "details": database_details(),
    }
    created = api_request("/api/database", method="POST", payload=payload, session_id=session_id)
    return created["id"]


def get_existing_collection_item(path: str, session_id: str, name: str):
    payload = api_request(path, session_id=session_id)
    if isinstance(payload, list):
        items = payload
    else:
        items = payload.get("data", payload)
    for item in items:
        if item.get("name") == name:
            return item
    return None


def ensure_card(session_id: str, database_id: int, spec: dict) -> int:
    existing = get_existing_collection_item("/api/card", session_id, spec["name"])
    payload = {
        "name": spec["name"],
        "description": spec["description"],
        "display": spec["display"],
        "visualization_settings": {},
        "dataset_query": {
            "database": database_id,
            "type": "native",
            "native": {"query": spec["query"], "template-tags": {}},
        },
    }
    if existing:
        api_request(f"/api/card/{existing['id']}", method="PUT", payload=payload, session_id=session_id)
        return existing["id"]
    created = api_request("/api/card", method="POST", payload=payload, session_id=session_id)
    return created["id"]


def ensure_dashboard(session_id: str) -> int:
    name = "Дашборд обучения по речевой аналитике"
    existing = get_existing_collection_item("/api/dashboard", session_id, name)
    payload = {
        "name": name,
        "description": "Демо-дашборд Metabase для учебного кейса по BI.",
        "parameters": [],
    }
    if existing:
        api_request(f"/api/dashboard/{existing['id']}", method="PUT", payload=payload, session_id=session_id)
        return existing["id"]
    created = api_request("/api/dashboard", method="POST", payload=payload, session_id=session_id)
    return created["id"]


def attach_cards(session_id: str, dashboard_id: int, card_ids: list[int]) -> None:
    dashboard = api_request(f"/api/dashboard/{dashboard_id}", session_id=session_id)
    existing_cards = dashboard.get("dashcards", dashboard.get("ordered_cards", []))
    spec_by_card_id = {card_id: spec for spec, card_id in zip(CARD_SPECS, card_ids)}
    dashcards = []
    changed = False
    next_temp_id = -1

    for item in existing_cards:
        current = dict(item)
        current_card_id = current.get("card_id") or current.get("card", {}).get("id")
        spec = spec_by_card_id.get(current_card_id)
        if spec:
            if (
                current.get("row") != spec["row"]
                or current.get("col") != spec["col"]
                or current.get("size_x") != spec["sizeX"]
                or current.get("size_y") != spec["sizeY"]
            ):
                current["row"] = spec["row"]
                current["col"] = spec["col"]
                current["size_x"] = spec["sizeX"]
                current["size_y"] = spec["sizeY"]
                changed = True
        dashcards.append(current)

    existing_ids = {
        item.get("card_id") or item.get("card", {}).get("id")
        for item in dashcards
        if item.get("card_id") or item.get("card")
    }

    for spec, card_id in zip(CARD_SPECS, card_ids):
        if card_id in existing_ids:
            continue
        dashcards.append(
            {
                "id": next_temp_id,
                "card_id": card_id,
                "row": spec["row"],
                "col": spec["col"],
                "size_x": spec["sizeX"],
                "size_y": spec["sizeY"],
                "parameter_mappings": [],
                "visualization_settings": {},
            }
        )
        next_temp_id -= 1
        changed = True
    if changed:
        api_request(
            f"/api/dashboard/{dashboard_id}/cards",
            method="PUT",
            payload={"cards": dashcards},
            session_id=session_id,
        )


def ensure_public_link(session_id: str, dashboard_id: int) -> str:
    dashboard = api_request(f"/api/dashboard/{dashboard_id}", session_id=session_id)
    public_uuid = dashboard.get("public_uuid")
    if not public_uuid:
        created = api_request(f"/api/dashboard/{dashboard_id}/public_link", method="POST", payload={}, session_id=session_id)
        public_uuid = created.get("uuid") or created.get("id") or created.get("public_uuid")
    if not public_uuid:
        raise RuntimeError("Unable to create Metabase public dashboard link.")
    return str(public_uuid)


def capture_dashboard(url: str, screenshot_path: Path) -> None:
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--virtual-time-budget=15000",
            "--window-size=1440,1024",
            f"--screenshot={screenshot_path}",
            url,
        ],
        check=True,
    )


def main() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    wait_for_metabase()
    maybe_run_initial_setup()
    session_id = login()
    database_id = ensure_database_id(session_id)
    card_ids = [ensure_card(session_id, database_id, spec) for spec in CARD_SPECS]
    dashboard_id = ensure_dashboard(session_id)
    attach_cards(session_id, dashboard_id, card_ids)
    public_uuid = ensure_public_link(session_id, dashboard_id)
    public_url = f"{METABASE_URL}/public/dashboard/{public_uuid}"
    admin_url = f"{METABASE_URL}/dashboard/{dashboard_id}"
    screenshot_path = ARTIFACTS_DIR / "metabase_dashboard_actual.png"
    time.sleep(8)
    capture_dashboard(public_url, screenshot_path)
    runtime = {
        "tool": "Metabase",
        "metabase_url": METABASE_URL,
        "admin_url": admin_url,
        "public_url": public_url,
        "dashboard_id": dashboard_id,
        "database_id": database_id,
        "database_name": DB_NAME,
        "admin_email": ADMIN_EMAIL,
        "admin_password": ADMIN_PASSWORD,
        "screenshot": str(screenshot_path),
    }
    RUNTIME_PATH.write_text(json.dumps(runtime, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(runtime, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
