#!/usr/bin/env python3
"""Verify credential-free Goal 2 semantic Recorder Draft evidence."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".local" / "evidence"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


expected = load(EVIDENCE / "goal2-verification.json")
live = load(EVIDENCE / "goal2-live.json")
auth = load(EVIDENCE / "goal2-auth-contract.json")
compat = load(EVIDENCE / "goal2-recorder-compatibility.json")
assert auth == {"draftMissingKeyStatus": 401}
assert compat["firstCreateStatus"] == 201 and compat["repeatCreateStatus"] == 200 and compat["repeatExisting"] is True
assert expected["provider"] == "opencode-go"
assert expected["model"] == "deepseek-v4-flash"
assert expected["tools"] == [
    "maxun_create_recorder_draft",
    "maxun_select_list_candidate",
    "maxun_update_draft_field",
    "maxun_preview_recorder_draft",
    "maxun_validate_recorder_draft",
    "maxun_compile_recorder_draft",
    "maxun_run_robot",
]
assert expected["listCandidatesInspected"] == live["listCandidates"] >= 1
assert expected["draftId"] == live["draftId"]
assert expected["compiled"]["robotId"] == live["compiledRobotId"]
assert live["paginationTestedAfterPreview"] is True
assert live["nameConflict"] == {"status": 409, "code": "robot_name_conflict"}

def contains_selector_key(value):
    if isinstance(value, dict):
        return any(key == "selector" or contains_selector_key(child) for key, child in value.items())
    if isinstance(value, list):
        return any(contains_selector_key(child) for child in value)
    return False

assert not contains_selector_key(live)
assert expected["renamedFields"] == ["image_url", "product_url", "product_name", "price", "rating", "review_count"]
assert expected["fieldOperations"] == ["exclude", "include", "rename"]
assert live["fieldOperations"] == expected["fieldOperations"]
assert expected["preview"] == {"rows": 5, "pagesVisited": 3, "diagnostics": []}
assert expected["paginationTestedAfterPreview"] is True
assert expected["validation"]["valid"] is True
coverage = expected["validation"]["coverage"]
assert isinstance(coverage, dict) and len(coverage) == 6 and all(value == 1 for value in coverage.values())
assert expected["compiled"]["robotId"]
assert expected["compiled"]["nativeAction"] == "scrapeList"
assert expected["compiled"]["pagination"] == "clickNext"
assert expected["compiled"]["limit"] == 5
assert expected["compiled"]["selectorExposed"] is False
assert expected["nameConflict"] == {"status": 409, "code": "robot_name_conflict"}
assert (ROOT / expected["transcriptArtifact"]).is_file()
assert expected["run"]["status"] == "success"
assert len(expected["run"]["rows"]) == 5
assert [row["product_name"] for row in expected["run"]["rows"]] == [
    "Aurora Headphones", "Meridian Keyboard", "Atlas Webcam", "Nova USB-C Hub", "Orbit Desk Lamp"
]

api_key = os.environ.get("MAXUN_API_KEY")
if api_key:
    for path in EVIDENCE.rglob("*"):
        if path.is_file() and api_key.encode() in path.read_bytes():
            raise AssertionError(f"API key found in evidence: {path}")

print("Goal 2 evidence verified: semantic draft sequence, pagination, validation, native compile, and five rows.")
