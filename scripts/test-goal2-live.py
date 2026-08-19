#!/usr/bin/env python3
"""Run the semantic Goal 2 Recorder Draft contract against a live Maxun service."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("MAXUN_BASE_URL", "http://127.0.0.1:8080/api").rstrip("/")
KEY = os.environ.get("MAXUN_API_KEY")
URL = os.environ.get("GOAL2_FIXTURE_URL", os.environ.get("FIXTURE_URL", "http://127.0.0.1:4173/page1.html"))
if not KEY:
    raise SystemExit("MAXUN_API_KEY is required")


def call(path: str, body: object | None = None) -> dict:
    request = urllib.request.Request(
        BASE + path,
        headers={"x-api-key": KEY, "content-type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    if body is not None:
        request.data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        payload = json.load(error)
        raise AssertionError(f"{path} returned HTTP {error.code}: {payload.get('code', payload.get('error', 'unknown'))}")
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} returned a non-object")
    return payload


def data(payload: dict) -> dict:
    value = payload.get("data")
    if not isinstance(value, dict):
        raise AssertionError("Maxun operation returned no data")
    return value


def expect_error(path: str, body: object, status: int, code: str) -> dict:
    request = urllib.request.Request(
        BASE + path,
        headers={"x-api-key": KEY, "content-type": "application/json"},
        method="POST",
        data=json.dumps(body).encode(),
    )
    try:
        urllib.request.urlopen(request, timeout=300)
    except urllib.error.HTTPError as error:
        payload = json.load(error)
        assert error.code == status, (error.code, payload)
        assert payload.get("code") == code, payload
        return payload
    raise AssertionError(f"{path} unexpectedly succeeded")


def field_kind(field: dict) -> str:
    samples = [str(value).lower() for value in field.get("samples", [])]
    attribute = field.get("attribute")
    if attribute == "src":
        return "image_url"
    if attribute == "href":
        return "product_url"
    if any("review" in value for value in samples):
        return "review_count"
    if any(value.startswith("$") for value in samples):
        return "price"
    if samples and all(value.replace(".", "", 1).isdigit() for value in samples):
        return "rating"
    return "product_name"


created = data(call("/sdk/recorder/drafts", {
    "url": URL,
    "name": f"Goal 2 Live Draft {int(time.time())}",
    "description": "Product name, price, rating, image URL, product URL, and review count",
}))
assert len(created.get("lists", [])) >= 1
assert "selector" not in json.dumps(created)
list_candidate = max(created["lists"], key=lambda candidate: len(candidate.get("fields", [])))
assert len(list_candidate["fields"]) >= 6
selected = data(call(f"/sdk/recorder/drafts/{created['id']}/select-list", {
    "listCandidateId": list_candidate["id"],
    "limit": 5,
}))
assert selected.get("selectedListId") == list_candidate["id"]
probe_field_id = list_candidate["fields"][0]["id"]
assert "selector" not in json.dumps(data(call(f"/sdk/recorder/drafts/{created['id']}/fields", {
    "fieldId": probe_field_id, "action": "exclude",
})))
assert "selector" not in json.dumps(data(call(f"/sdk/recorder/drafts/{created['id']}/fields", {
    "fieldId": probe_field_id, "action": "include",
})))

for field in list_candidate["fields"]:
    name = field_kind(field)
    update = data(call(f"/sdk/recorder/drafts/{created['id']}/fields", {
        "fieldId": field["id"],
        "action": "rename",
        "name": name,
    }))
    assert "selector" not in json.dumps(update)

preview = data(call(f"/sdk/recorder/drafts/{created['id']}/preview", {"followPagination": True, "limit": 5}))
assert len(preview.get("rows", [])) == 5
assert preview.get("pagesVisited", 0) >= 2
assert preview.get("diagnostics") == []
refreshed = data(call(f"/sdk/recorder/drafts/{created['id']}"))
selected_after_preview = next(item for item in refreshed.get("lists", []) if item.get("selected"))
assert selected_after_preview.get("pagination", {}).get("tested") is True
assert "selector" not in json.dumps(refreshed)
field_ids = {field["id"] for field in selected_after_preview.get("fields", [])}

validation = data(call(f"/sdk/recorder/drafts/{created['id']}/validate", {"scope": "multi-page"}))
assert validation.get("valid") is True
assert validation.get("pagesVisited", 0) >= 2
coverage = validation.get("coverage", {})
assert set(coverage) == field_ids and len(coverage) == 6 and all(value == 1 for value in coverage.values())
assert not any(item.get("severity") == "error" for item in validation.get("diagnostics", []))

conflict = None
if os.environ.get("GOAL2_CONFLICT_NAME"):
    conflict = expect_error(
        f"/sdk/recorder/drafts/{created['id']}/compile",
        {"robotName": os.environ["GOAL2_CONFLICT_NAME"]},
        409,
        "robot_name_conflict",
    )

compiled = data(call(f"/sdk/recorder/drafts/{created['id']}/compile", {
    "robotName": f"Goal 2 Live Robot {int(time.time())}",
}))
assert compiled.get("robotId")
assert compiled.get("limit") == 5
assert compiled.get("pagination", {}).get("type") == "clickNext"
assert "selector" not in json.dumps(compiled)
robot = data(call(f"/sdk/robots/{compiled['robotId']}"))
workflow = robot.get("recording", {}).get("workflow", [])
actions = [action.get("action") for pair in workflow for action in pair.get("what", [])]
assert "goto" in actions and "scrapeList" in actions

run = data(call(f"/sdk/robots/{compiled['robotId']}/execute", {}))
rows = run.get("data", {}).get("listData", [])
assert run.get("status") == "success"
assert len(rows) == 5
assert [row.get("product_name") for row in rows] == [
    "Aurora Headphones", "Meridian Keyboard", "Atlas Webcam", "Nova USB-C Hub", "Orbit Desk Lamp"
]

artifact = {
    "fixtureUrl": URL,
    "draftId": created["id"],
    "listCandidates": len(created["lists"]),
    "selectedFields": [field_kind(field) for field in list_candidate["fields"]],
    "fieldOperations": ["exclude", "include", "rename"],
    "preview": {"rows": len(preview["rows"]), "pagesVisited": preview["pagesVisited"], "diagnostics": preview["diagnostics"]},
    "paginationTestedAfterPreview": selected_after_preview["pagination"]["tested"],
    "validation": {"valid": validation["valid"], "pagesVisited": validation["pagesVisited"], "coverage": validation["coverage"], "diagnostics": validation["diagnostics"]},
    "compiledRobotId": compiled["robotId"],
    "nameConflict": {"status": 409, "code": conflict["code"]} if conflict else None,
    "run": {"status": run["status"], "runId": run.get("runId"), "rows": rows},
}
out = ROOT / ".local" / "evidence" / "goal2-live.json"
out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
print(f"Goal 2 live contract passed: draft {created['id']}, robot {compiled['robotId']}, {len(rows)} rows across {preview['pagesVisited']} pages.")
