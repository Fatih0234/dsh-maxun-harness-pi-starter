# GitHub review coordinates

This integration workspace is reviewed across the root project and its two source pull requests:

- Maxun service: [getmaxun/maxun#1194](https://github.com/getmaxun/maxun/pull/1194), fork head `Fatih0234/maxun:pi/maxun-harness-integration`, head `6e0ec876f5e194598402ea6879df297bf2a23f76`, base `6ef14c7c89fac18b5ba771a1228ee064e1d7810f`.
- DeepSeek Harness: [Fatih0234/deepseek-harness#1](https://github.com/Fatih0234/deepseek-harness/pull/1), fork head `Fatih0234/deepseek-harness:pi/maxun-harness-integration`, head `5f429f9725d2a362ef4e2b1c09449c37e591b304`, base `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`.

The source pins and the root integration contract are recorded in `config/sources.json`, `docs/GOAL4_READINESS.md`, and `docs/GOAL5_READINESS.md`. The root repository intentionally does not vendor the source checkouts; the source PRs above contain the implementation changes.
