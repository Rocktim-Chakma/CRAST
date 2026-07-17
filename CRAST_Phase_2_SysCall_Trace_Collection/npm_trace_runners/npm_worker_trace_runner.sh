#!/usr/bin/env bash

LIST="$HOME/crast/worker4_list.txt"
PKG_DIR="$HOME/crast/packages/worker4"
BASE="$HOME/crast"

TMP_BASE="$BASE/tmp_runs/worker4"
LOG_BASE="$BASE/logs_safe/worker4"
RESULT_BASE="$BASE/results/worker4"

SUCCESS_LIST="$RESULT_BASE/success.txt"
FAILED_LIST="$RESULT_BASE/failed.txt"

mkdir -p "$TMP_BASE" "$LOG_BASE" "$RESULT_BASE"
touch "$SUCCESS_LIST" "$FAILED_LIST"

export NVM_DIR="$HOME/.nvm"
source "$NVM_DIR/nvm.sh"

while read -r pkg; do
  [ -z "$pkg" ] && continue

  echo "========================================"
  echo "Running package: $pkg"
  echo "========================================"

  PKG_SUCCESS=0

  for v in 14 16 18; do
    echo "Trying Node $v for $pkg"

    nvm use "$v" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
      echo "Node $v not available"
      continue
    fi

    RUN_DIR="$TMP_BASE/${pkg}_node${v}"
    rm -rf "$RUN_DIR"
    mkdir -p "$RUN_DIR"

    export HOME="$RUN_DIR/home"
    export npm_config_cache="$RUN_DIR/.npm-cache"
    mkdir -p "$HOME" "$npm_config_cache"

    cd "$RUN_DIR" || continue

    OUT_FILE="$LOG_BASE/${pkg}_node${v}.out"
    ERR_FILE="$LOG_BASE/${pkg}_node${v}.err"
    TRACE_PREFIX="$LOG_BASE/${pkg}_node${v}.trace"

    timeout 60s strace -ff -ttt -T -o "$TRACE_PREFIX" \
      npm install "$PKG_DIR/$pkg" \
      > "$OUT_FILE" 2> "$ERR_FILE"

    RC=$?

    if [ $RC -eq 0 ]; then
      echo "$pkg" >> "$SUCCESS_LIST"
      echo "SUCCESS: $pkg"
      PKG_SUCCESS=1
      break
    else
      echo "FAILED on Node $v: $pkg"
    fi
  done

  if [ $PKG_SUCCESS -eq 0 ]; then
    echo "$pkg" >> "$FAILED_LIST"
    echo "ALL VERSIONS FAILED: $pkg"
  fi

done < "$LIST"

echo "========================================"
echo "Done."
echo "Success list: $SUCCESS_LIST"
echo "Failed list : $FAILED_LIST"
echo "Logs folder : $LOG_BASE"
echo "========================================"
