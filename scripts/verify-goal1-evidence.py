#!/usr/bin/env python3
"""Verify the credential-free Goal 1 acceptance artifacts."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".local" / "evidence"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


expected = load(ROOT / "tests" / "fixtures" / "catalog" / "expected-first-5.json")
verification = load(EVIDENCE / "goal1-verification.json")
assert verification["rows"] == expected, "normalized rows differ from fixture expectation"
assert verification["rerun_equal"] is True, "independent rerun was not identical"

headless = load(EVIDENCE / "harness-headless-maxun.json")
assert headless["provider"] == "opencode-go"
assert headless["model"] == "deepseek-v4-flash"
assert headless["tools"] == ["maxun_create_list_robot", "maxun_run_robot"]
assert headless["status"] == "success"
assert headless["rows"] == 5
assert headless["limit"] == 5
assert len(headless["fields"]) == 6

contract = load(EVIDENCE / "maxun-auth-contract.json")
assert contract == {"missingKeyStatus": 401, "authenticatedInvalidRequestStatus": 400}

api_key = os.environ.get("MAXUN_API_KEY")
if api_key:
    for path in EVIDENCE.rglob("*"):
        if path.is_file() and api_key.encode() in path.read_bytes():
            raise AssertionError(f"API key found in evidence: {path}")

print("Goal 1 evidence verified: fixture rows, rerun, semantic tools, native flow metadata, and auth boundary.")
