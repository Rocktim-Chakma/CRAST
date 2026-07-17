#!/usr/bin/env bash

INPUT_DIR="/data/malicious_tgz"
WORK_DIR="/data/workspace"
TRACE_DIR="/data/traces"
LOG_DIR="/data/logs"

FAILED_LIST="$LOG_DIR/failed_packages.txt"
DONE_LIST="$LOG_DIR/completed_packages.txt"

mkdir -p "$WORK_DIR" "$TRACE_DIR" "$LOG_DIR"

for tgz in "$INPUT_DIR"/*.tgz; do
  [ -e "$tgz" ] || continue

  base=$(basename "$tgz" .tgz)
  pkg_work="$WORK_DIR/$base"
  pkg_out="$TRACE_DIR/$base"

  rm -rf "$pkg_work"
  mkdir -p "$pkg_work" "$pkg_out"

  echo "Running $base"

  cp "$tgz" "$pkg_work/"
  cd "$pkg_work" || continue

  tar -xzf "$(basename "$tgz")" > "$pkg_out/extract.stdout.log" 2> "$pkg_out/extract.stderr.log"
  if [ $? -ne 0 ]; then
    echo "$base | extract_failed" >> "$FAILED_LIST"
    continue
  fi

  if [ ! -d "$pkg_work/package" ]; then
    echo "$base | package_dir_missing" >> "$FAILED_LIST"
    continue
  fi

  cd "$pkg_work/package" || {
    echo "$base | cd_failed" >> "$FAILED_LIST"
    continue
  }

  [ -f package.json ] && cp package.json "$pkg_out/package.json"

  timeout 120s strace -ff -tt -T -s 256 -o "$pkg_out/trace" \
    -e trace=%file,%process,%network,%desc \
    npm install --ignore-scripts=false \
    > "$pkg_out/run.stdout.log" \
    2> "$pkg_out/run.stderr.log"

  rc=$?

  if [ $rc -ne 0 ]; then
    echo "$base | run_failed | rc=$rc" >> "$FAILED_LIST"
  else
    echo "$base" >> "$DONE_LIST"
  fi
done
