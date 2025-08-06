#!/bin/bash

URL="$1"
CLEAN_URL="${URL#papergrab:}"
cd "$(dirname "$0")" || exit 1

# Activate virtualenv
if [ -f env/bin/activate ]; then
  source env/bin/activate
else
  echo "❌ Virtual environment not found."
  exit 1
fi

LOG="/tmp/papergrab_$(date +%s).log"
python3 papergrab.py "$CLEAN_URL" > "$LOG" 2>&1
STATUS=$?

if [ $STATUS -ne 0 ]; then
  (command -v gnome-terminal && gnome-terminal -- bash -c "cat $LOG; echo; read") \
  || (command -v xterm && xterm -e "cat $LOG; echo; read") \
  || (cat "$LOG"; echo; read)
else
  rm -f "$LOG"
fi

