#!/usr/bin/env python3
"""Verify the non-secret Goal 4 implementation handoff."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence_path = ROOT / ".local" / "evidence" / "goal4-readiness.json"
evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
assert evidence["status"] == "complete"
assert evidence["goal1"] == evidence["goal2"] == evidence["goal3"] == "complete"
assert evidence["goal4"] == "complete"
assert evidence["goal5"] == "deferred"
assert evidence["existingMaxunRrwebEvent"]
assert evidence["existingMaxunDomReplayer"]
assert evidence["existingHarnessSessionUiSlots"]
assert evidence["existingHarnessDetailsShell"]
assert evidence["rrwebLicense"] == evidence["rrwebSnapshotLicense"] == "MIT"
remote_browser = (ROOT / "sources/maxun/server/src/browser-management/classes/RemoteBrowser.ts").read_text(encoding="utf-8")
assert "maskAllInputs: true" in remote_browser
assert "maskTextSelector," in remote_browser
assert "blockSelector: 'iframe'" in remote_browser
assert "recordCanvas: false" in remote_browser
masking = json.loads((ROOT / ".local" / "evidence" / "goal4-rrweb-masking.json").read_text(encoding="utf-8"))
assert masking["sensitiveValuesLeaked"] is False
assert masking["publicTextPreserved"] is True
assert masking["covered"]["contenteditable"] is True
assert masking["covered"]["iframe"]["blocked"] is True
assert masking["covered"]["canvas"]["recordingDisabled"] is True
live = json.loads((ROOT / ".local" / "evidence" / "goal4-live.json").read_text(encoding="utf-8"))
assert live["capability"]["issued"] is True
assert live["capability"]["claimBound"] is True
assert live["stream"]["unauthorizedRejected"] is True
assert live["stream"]["reconnectFullSnapshot"] is True
assert live["screenshot"]["available"] is True
assert live["telemetry"]["rrwebEventsPersisted"] is False
web = json.loads((ROOT / ".local" / "evidence" / "goal4-web-acceptance.json").read_text(encoding="utf-8"))
assert web["passed"] is True
assert web["assertions"]["reloadReconnect"] is True
assert web["assertions"]["telemetryAbsentFromSessionHistory"] is True
assert web["assertions"]["apiKeyAbsentFromBrowserResources"] is True
licensing = json.loads((ROOT / ".local" / "evidence" / "goal4-licensing.json").read_text(encoding="utf-8"))
assert all(item["license"] == "MIT" for item in licensing["packages"])
assert "rrweb-event" in (
    ROOT / "sources/maxun/server/src/browser-management/classes/RemoteBrowser.ts"
).read_text(encoding="utf-8")
assert "DOMBrowserRenderer" in (
    ROOT / "sources/maxun/src/components/recorder/DOMBrowserRenderer.tsx"
).read_text(encoding="utf-8")
assert "details" in (
    ROOT / "sources/deepseek-harness/packages/client/ui-conversation/README.md"
).read_text(encoding="utf-8")
criteria = (ROOT / "goals/04-browser-ui.md").read_text(encoding="utf-8")
assert criteria.count("- [ ]") == 0
assert criteria.count("- [x]") == 7
for path in (ROOT / "docs/GOAL4_READINESS.md", ROOT / "docs/SECURITY.md"):
    text = path.read_text(encoding="utf-8")
    assert "MAXUN_API_KEY" in text
    assert "Session.append()" in text or "session log" in text
for path in (evidence_path,):
    text = path.read_text(encoding="utf-8")
    assert "MAXUN_API_KEY=" not in text
    assert "sk-" not in text
print("Goal 4 acceptance verified: stream auth, masking, replay UI, screenshot fallback, reload reconnect, telemetry exclusion, licensing, and regressions recorded.")
