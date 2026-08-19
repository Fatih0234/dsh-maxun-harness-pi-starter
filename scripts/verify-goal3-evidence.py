#!/usr/bin/env python3
"""Verify credential-free Goal 3 durable correlation evidence."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / ".local" / "evidence" / "goal3-live.json"
suite = ROOT / ".local" / "evidence" / "goal3-harness-suite.txt"
evidence = json.loads(path.read_text(encoding="utf-8"))
suite_text = suite.read_text(encoding="utf-8")
assert "Test Files  810 passed | 9 skipped (819)" in suite_text
assert "Tests       13512 passed | 110 skipped (13622)" in suite_text

assert evidence["serviceInstanceId"]
assert evidence["draftId"] and evidence["robotId"] and evidence["durableRobotVerified"] is True
assert evidence["firstSessionId"] == evidence["refreshedSessionId"]
assert evidence["browser"]["reconnectClaimExisting"] is True
assert evidence["browser"]["reconnectedStatus"] == "active"
assert evidence["browser"]["goneErrorCode"] == "resource_not_found"
assert evidence["ownership"] == {
    "conflictingSecondSession": True,
    "conflictCode": "claim_conflict",
    "foreignBrowserReleaseBlocked": True,
    "staleEpochBlocked": True,
    "explicitRelease": True,
    "epoch": evidence["ownership"]["epoch"],
    "draftEpoch": evidence["ownership"]["draftEpoch"],
    "reclaimedDraftEpoch": evidence["ownership"]["reclaimedDraftEpoch"],
}
assert evidence["ownership"]["epoch"] >= 1 and evidence["ownership"]["draftEpoch"] >= 1
assert evidence["ownership"]["reclaimedDraftEpoch"] > evidence["ownership"]["draftEpoch"]
assert evidence["projection"] == {
    "coldRestored": True,
    "finalBrowserStatus": "gone",
    "finalLifecycleStatus": "degraded",
    "finalErrorCode": "resource_not_found",
    "durableDraftId": evidence["draftId"],
    "durableRobotId": evidence["robotId"],
    "modelMessages": 0,
    "persistedEventCount": evidence["projection"]["persistedEventCount"],
    "forbiddenTrafficPersisted": False,
    "credentialPersisted": False,
}
assert evidence["projection"]["persistedEventCount"] >= 1

api_key = os.environ.get("MAXUN_API_KEY")
if api_key:
    for candidate in (path, suite):
        if api_key.encode() in candidate.read_bytes():
            raise AssertionError(f"API key found in evidence: {candidate}")

print("Goal 3 evidence verified: cold correlation restore, browser reconnect/gone distinction, ownership conflict, and telemetry exclusion.")
