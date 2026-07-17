#!/usr/bin/env bash
# CRAST PyPI tracing runner with per-package Python virtual environments.
# Keep paths configurable through environment variables.

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
PACKAGES=("$INPUT_DIR"/*.tar.gz "$INPUT_DIR"/*.zip "$INPUT_DIR"/*.whl)
shopt -u nullglob

for pkg_archive in "${PACKAGES[@]}"; do
  filename="$(basename "$pkg_archive")"
  base="$filename"
  base="${base%.tar.gz}"; base="${base%.zip}"; base="${base%.whl}"
  safe_base="$(echo "$base" | sed 's#[/@: ]#_#g')"
  pkg_work="$WORK_DIR/$safe_base"
  pkg_out="$TRACE_DIR/$safe_base"
  rm -rf "$pkg_work"
  mkdir -p "$pkg_work" "$pkg_out"
  cp "$pkg_archive" "$pkg_work/"

  export HOME="$pkg_work/home"
  export PIP_CACHE_DIR="$pkg_work/.pip-cache"
  export TMPDIR="$pkg_work/tmp"
  mkdir -p "$HOME" "$PIP_CACHE_DIR" "$TMPDIR"

  python3 -m venv "$pkg_work/venv" > "$pkg_out/venv_create.stdout.log" 2> "$pkg_out/venv_create.stderr.log"
  if [ $? -ne 0 ]; then
    echo "$filename | venv_create_failed" >> "$FAILED_LIST"
    continue
  fi

  VENV_PY="$pkg_work/venv/bin/python"
  VENV_PIP="$pkg_work/venv/bin/pip"
  echo "$pkg_work/venv" > "$pkg_out/venv_path.txt"
  "$VENV_PY" --version > "$pkg_out/python_version.txt" 2>&1
  "$VENV_PIP" --version > "$pkg_out/pip_version.txt" 2>&1
  [ -f "$pkg_work/venv/pyvenv.cfg" ] && cp "$pkg_work/venv/pyvenv.cfg" "$pkg_out/pyvenv.cfg"

  "$VENV_PY" -m pip install --upgrade pip setuptools wheel > "$pkg_out/pip_prepare.stdout.log" 2> "$pkg_out/pip_prepare.stderr.log" || true

  timeout "${TIMEOUT_SECONDS}s" strace -ff -tt -T -s 256 -o "$pkg_out/trace" \
    -e trace=%file,%process,%network,%desc \
    "$VENV_PY" -m pip install --no-input --no-cache-dir "$pkg_work/$filename" \
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
