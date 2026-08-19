#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
need git
need python3
failed=0
python3 - "$PROJECT_ROOT/config/sources.json" <<'PYVERIFY' | while IFS=$'\t' read -r id sha dir editable; do
import json, sys
cfg=json.load(open(sys.argv[1]))
for r in cfg['repositories']:
    print('\t'.join([r['id'], r['sha'], r['directory'], str(r['editable']).lower()]))
PYVERIFY
  target="$PROJECT_ROOT/sources/$dir"
  if [[ ! -d "$target/.git" ]]; then echo "MISSING $id: $target" >&2; exit 2; fi
  head=$(git -C "$target" rev-parse HEAD)
  if [[ "$editable" == "true" ]]; then
    git -C "$target" merge-base --is-ancestor "$sha" HEAD || { echo "FAIL $id HEAD $head is not based on $sha" >&2; exit 3; }
    echo "OK $id base=$sha head=$head"
  else
    [[ "$head" == "$sha" ]] || { echo "FAIL $id expected=$sha got=$head" >&2; exit 4; }
    echo "OK $id $head"
  fi
done
