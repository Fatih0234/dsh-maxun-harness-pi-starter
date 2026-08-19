#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
need git
need python3
mkdir -p "$PROJECT_ROOT/sources"

python3 - "$PROJECT_ROOT/config/sources.json" <<'PYBOOT' | while IFS=$'\t' read -r id url sha dir editable branch; do
import json, sys
cfg=json.load(open(sys.argv[1]))
for r in cfg['repositories']:
    print('\t'.join([r['id'], r['url'], r['sha'], r['directory'], str(r['editable']).lower(), r.get('branch','')]))
PYBOOT
  target="$PROJECT_ROOT/sources/$dir"
  if [[ -d "$target/.git" ]]; then
    if [[ -n "$(git -C "$target" status --porcelain)" ]]; then
      echo "Refusing to alter dirty checkout: $target" >&2
      exit 1
    fi
  elif [[ -e "$target" ]]; then
    echo "Refusing to overwrite non-git path: $target" >&2
    exit 1
  else
    echo "Initializing $id"
    git init -q "$target"
    git -C "$target" remote add origin "$url"
  fi

  if ! git -C "$target" cat-file -e "$sha^{commit}" 2>/dev/null; then
    echo "Fetching pinned commit for $id"
    git -C "$target" fetch --no-tags --depth=1 origin "$sha"
  fi

  if [[ "$editable" == "true" ]]; then
    if git -C "$target" show-ref --verify --quiet "refs/heads/$branch"; then
      git -C "$target" checkout -q "$branch"
      if ! git -C "$target" merge-base --is-ancestor "$sha" HEAD; then
        echo "$id branch is no longer based on pinned SHA $sha" >&2
        exit 1
      fi
    else
      git -C "$target" checkout -q -b "$branch" "$sha"
    fi
  else
    git -C "$target" checkout -q --detach "$sha"
  fi
  echo "$id: $(git -C "$target" rev-parse --short=12 HEAD)"
done

echo "Source bootstrap complete. Read upstream AGENTS.md files before editing."
