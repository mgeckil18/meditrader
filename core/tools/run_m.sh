#!/usr/bin/env bash
# Runs one M-series configuration: 3 warm-start snapshots, then 6 seeds x 10 years.
# Usage (repo root, after `cargo build --release` in core/):
#   bash core/tools/run_m.sh NAME     # experiments/configs/m/NAME.json -> experiments/out/m2/NAME_{0..5}.json
# Intermediate files (snapshots, per-seed configs, logs) go to $MEDI_TMP (default: experiments/out/tmp).
set -e
cd "$(dirname "$0")/../.."
B=core/target/release/medi
S=${MEDI_TMP:-experiments/out/tmp}
mkdir -p "$S" experiments/out/m2
N=$1; C=experiments/configs/m/$N.json
for k in 0 1 2; do $B snapshot $C $k $S/${N}_snap$k.json > $S/${N}_s$k.log 2>&1 & done; wait
for s in 0 1 2 3 4 5; do python3 -c "import json,sys;c=json.load(open('$C'));c['seed']=$s;json.dump(c,open('$S/${N}_c$s.json','w'))"; done
for s in 0 1 2 3; do $B run $S/${N}_c$s.json $N experiments/out/m2/${N}_$s.json $S/${N}_snap$((s%3)).json > $S/${N}_r$s.log 2>&1 & done; wait
for s in 4 5; do $B run $S/${N}_c$s.json $N experiments/out/m2/${N}_$s.json $S/${N}_snap$((s%3)).json > $S/${N}_r$s.log 2>&1 & done; wait
echo "$N done"
