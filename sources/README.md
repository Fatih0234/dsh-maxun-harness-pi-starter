# Source checkouts

Run `../scripts/bootstrap-sources.sh` from the project root.

The script fetches exact commits from `config/sources.json`.

- `maxun` and `deepseek-harness` get local editable integration branches rooted at the research SHAs.
- all other checkouts remain detached reference trees.

Do not vendor these source trees into the starter repository. They are ignored at the top level so each upstream repository keeps its own git history.
