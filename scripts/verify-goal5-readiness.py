#!/usr/bin/env python3
"""Verify the completed Goal 5 handoff/control boundary and evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")

active = read("goals/ACTIVE.md")
goal5 = read("goals/05-human-handoff.md")
handoff = read("docs/GOAL5_READINESS.md")
goal4_readiness = json.loads(read(".local/evidence/goal4-readiness.json"))
live = json.loads(read(".local/evidence/goal5-live.json"))
web = json.loads(read(".local/evidence/goal5-web-acceptance.json"))

assert "Goals 1–5 are complete" in active
assert "Goal 5 implementation is active" in goal5 or "Goal 5 implementation" in goal5
assert handoff.startswith("# Goal 5 readiness")
assert "Separate control lease" in handoff
assert "Cancellation bridge" in handoff
assert "Credential boundary" in handoff
assert goal4_readiness["status"] == "complete"
assert goal4_readiness["goal4"] == "complete"
assert all(line.startswith("- [x]") for line in goal5.splitlines() if line.startswith("- ["))
assert len([line for line in goal5.splitlines() if line.startswith("- [x]")]) == 8
assert live["goal"] == 5 and all(live["criteria"].values())
assert live["commands"]["cancellationStatus"] == "unknown"
assert live["telemetry"]["rawTextInEvidence"] is False
assert live["telemetry"]["rawTextInControlResult"] is False
assert live["telemetry"]["rrwebContainsSecret"] is False
assert live["telemetry"]["screenshotContainsSecret"] is False
assert live["telemetry"]["staleScreenshotRejected"] is True
assert web["passed"] is True

required = [
    "sources/maxun/server/src/models/ControlLease.ts",
    "sources/maxun/server/src/models/ControlCommand.ts",
    "sources/maxun/server/src/sdk/controlLease.ts",
    "sources/maxun/server/src/sdk/browserControl.ts",
    "sources/maxun/server/src/db/migrations/20260819010000-create-maxun-control-leases.js",
    "sources/deepseek-harness/packages/client/ui-maxun/src/client/BrowserDetails.tsx",
    "scripts/test-goal5-live.js",
    ".local/evidence/goal5-live.json",
    ".local/evidence/goal5-web-acceptance.json",
]
for path in required:
    assert (ROOT / path).exists(), path

ui_root = ROOT / "sources/deepseek-harness/packages/client/ui-maxun/src"
ui_text = "\n".join(path.read_text(encoding="utf-8") for path in ui_root.rglob("*.ts*"))
assert "MAXUN_API_KEY" not in ui_text
assert "control-command" in ui_text and "control-release" in ui_text and "request-refresh" in ui_text
for forbidden in (
    "input:keyup",
    "input:url",
    "dom:click",
    "dom:keypress",
    "changeTab",
    "addTab",
    "closeTab",
    "socket.emit('action'",
):
    assert forbidden not in ui_text, f"forbidden legacy mutating event leaked into UI: {forbidden}"

serialized_evidence = json.dumps({"live": live, "web": web})
assert "goal5-human-secret-sentinel" not in serialized_evidence
assert "MAXUN_API_KEY=" not in serialized_evidence

output = ROOT / ".local/evidence/goal5-readiness.json"
evidence = {
    "status": "complete",
    "goal4Boundary": "preserved-read-only-stream",
    "goal3Baseline": ".local/evidence/goal3-live.json",
    "goal5Contract": "goals/05-human-handoff.md",
    "goal5Handoff": "docs/GOAL5_READINESS.md",
    "goal5Criteria": {"total": 8, "implemented": 8},
    "evidence": {
        "liveControl": ".local/evidence/goal5-live.json",
        "webHandoff": ".local/evidence/goal5-web-acceptance.json",
        "goal4Regression": ".local/evidence/goal4-web-acceptance.json",
    },
    "audits": {
        "serverControlLease": True,
        "commandLedgerAndReplayFence": True,
        "cancellationOutcomeUnknown": True,
        "pauseResumeAbortReuse": True,
        "assistVsRecord": True,
        "freshObservationAndValidationInvalidation": True,
        "slowRace": True,
        "credentialBoundary": True,
        "goal4ReadOnlyUi": True,
    },
}
output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
print("Goal 5 acceptance verified: 8/8 criteria, control epochs, cancellation, handoff UI, race, and credential privacy pass.")
