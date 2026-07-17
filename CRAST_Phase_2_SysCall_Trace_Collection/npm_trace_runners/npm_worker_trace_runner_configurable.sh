#!/usr/bin/env bash
# CRAST NPM worker runner for a package list and local package archive directory.

set -u
LIST="${LIST:-$HOME/crast/worker_list.txt}"
PKG_DIR="${PKG_DIR:-$HOME/crast/packages}"
TMP_BASE="${TMP_BASE:-$HOME/crast/tmp_runs}"
LOG_BASE="${LOG_BASE:-$HOME/crast/logs_safe}"
RESULT_BASE="${RESULT_BASE:-$HOME/crast/results}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-60}"
NODE_VERSIONS="${NODE_VERSIONS:-14 16 18}"

mkdir -p "$TMP_BASE" "$LOG_BASE" "$RESULT_BASE"
SUCCESS_LIST="$RESULT_BASE/success.txt"
FAILED_LIST="$RESULT_BASE/failed.txt"
touch "$SUCCESS_LIST" "$FAILED_LIST"

if [ "$(id -u)" -eq 0 ]; then
  echo "ERROR: Do not run tracing scripts as root." | tee -a "$FAILED_LIST"
  exit 1
fi

if [ -s "$HOME/.nvm/nvm.sh" ]; then
  # shellcheck disable=SC1090
  source "$HOME/.nvm/nvm.sh"
fi

while IFS= read -r pkg; do
  [ -z "$pkg" ] && continue
  safe_pkg="$(echo "$pkg" | sed 's#[/@: ]#_#g')"
  for node_ver in $NODE_VERSIONS; do
    if command -v nvm >/dev/null 2>&1; then
      nvm use "$node_ver" >/dev/null 2>&1 || continue
    fi
    RUN_DIR="$TMP_BASE/${safe_pkg}_node${node_ver}"
    OUT_DIR="$LOG_BASE/${safe_pkg}_node${node_ver}"
    rm -rf "$RUN_DIR"
    mkdir -p "$RUN_DIR" "$OUT_DIR"
    export HOME="$RUN_DIR/home"
    export npm_config_cache="$RUN_DIR/.npm-cache"
    export TMPDIR="$RUN_DIR/tmp"
    mkdir -p "$HOME" "$npm_config_cache" "$TMPDIR"

    timeout "${TIMEOUT_SECONDS}s" strace -ff -ttt -T -s 256 -o "$OUT_DIR/trace" \
      npm install "$PKG_DIR/$pkg" \
      > "$OUT_DIR/run.stdout.log" \
      2> "$OUT_DIR/run.stderr.log"
    rc=$?
    if [ $rc -eq 0 ]; then
      echo "$pkg,node$node_ver" >> "$SUCCESS_LIST"
      break
    else
      echo "$pkg,node$node_ver,rc=$rc" >> "$FAILED_LIST"
    fi
  done
done < "$LIST"
