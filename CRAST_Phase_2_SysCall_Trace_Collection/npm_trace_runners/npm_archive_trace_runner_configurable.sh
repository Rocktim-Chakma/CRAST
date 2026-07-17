#!/usr/bin/env bash
# CRAST NPM archive tracing runner for .tgz package archives.

set -u

INPUT_DIR="${INPUT_DIR:-/data/malicious_tgz}"
WORK_DIR="${WORK_DIR:-/data/workspace}"
TRACE_DIR="${TRACE_DIR:-/data/traces}"
LOG_DIR="${LOG_DIR:-/data/logs}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-120}"
FAILED_LIST="$LOG_DIR/failed_packages.txt"
DONE_LIST="$LOG_DIR/completed_packages.txt"

mkdir -p "$WORK_DIR" "$TRACE_DIR" "$LOG_DIR"
touch "$FAILED_LIST" "$DONE_LIST"

if [ "$(id -u)" -eq 0 ]; then
  echo "ERROR: Do not run tracing scripts as root." | tee -a "$FAILED_LIST"
  exit 1
fi

shopt -s nullglob
for tgz in "$INPUT_DIR"/*.tgz; do
  filename="$(basename "$tgz")"
  base="${filename%.tgz}"
  safe_base="$(echo "$base" | sed 's#[/@: ]#_#g')"
  pkg_work="$WORK_DIR/$safe_base"
  pkg_out="$TRACE_DIR/$safe_base"
  rm -rf "$pkg_work"
  mkdir -p "$pkg_work" "$pkg_out"
  tar -xzf "$tgz" -C "$pkg_work" > "$pkg_out/extract.stdout.log" 2> "$pkg_out/extract.stderr.log"
  if [ $? -ne 0 ]; then
    echo "$filename | extract_failed" >> "$FAILED_LIST"
    continue
  fi

  export HOME="$pkg_work/home"
  export npm_config_cache="$pkg_work/.npm-cache"
  export TMPDIR="$pkg_work/tmp"
  mkdir -p "$HOME" "$npm_config_cache" "$TMPDIR"

  pkg_dir="$pkg_work/package"
  [ -d "$pkg_dir" ] || pkg_dir="$pkg_work"
  cd "$pkg_dir" || { echo "$filename | cd_failed" >> "$FAILED_LIST"; continue; }

  timeout "${TIMEOUT_SECONDS}s" strace -ff -tt -T -s 256 -o "$pkg_out/trace" \
    -e trace=%file,%process,%network,%desc \
    npm install --ignore-scripts=false \
    > "$pkg_out/run.stdout.log" \
    2> "$pkg_out/run.stderr.log"
  rc=$?
  if [ $rc -eq 0 ]; then
    echo "$filename" >> "$DONE_LIST"
  elif [ $rc -eq 124 ]; then
    echo "$filename | timeout | rc=$rc" >> "$FAILED_LIST"
  else
    echo "$filename | run_failed | rc=$rc" >> "$FAILED_LIST"
  fi
done
