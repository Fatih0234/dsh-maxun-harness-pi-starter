# GitHub review coordinates

This integration workspace is reviewed across the root project and its two source pull requests:

- Root integration workspace: [Fatih0234/dsh-maxun-harness-pi-starter](https://github.com/Fatih0234/dsh-maxun-harness-pi-starter), current `main`.
- Maxun service: [getmaxun/maxun#1194](https://github.com/getmaxun/maxun/pull/1194), fork head `Fatih0234/maxun:pi/maxun-harness-integration`, head `7d027053a732519bacb28eebd77dde77077c2ed8`, base `6ef14c7c89fac18b5ba771a1228ee064e1d7810f`.
- DeepSeek Harness: [Fatih0234/deepseek-harness#1](https://github.com/Fatih0234/deepseek-harness/pull/1), fork head `Fatih0234/deepseek-harness:pi/maxun-harness-integration`, head `4b68869cbb9b9ddf1c48d6d7d27d1a37e467494e`, base `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`.

The source pins and the root integration contract are recorded in `config/sources.json`, `docs/GOAL4_READINESS.md`, and `docs/GOAL5_READINESS.md`. Sanitized acceptance artifacts are in `review-evidence/`. The root repository intentionally does not vendor the source checkouts; the source PRs above contain the implementation changes.
