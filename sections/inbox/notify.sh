#!/bin/zsh
# notify.sh "title" "text": a Mac notification on the Air (from the server: through ssh air) and on the MacBook Pro the captain works on.
T="${1//\"/\'}"; M="${2//\"/\'}"
if [ -x /usr/bin/osascript ]; then
  /usr/bin/osascript -e "display notification \"$M\" with title \"$T\" sound name \"Glass\"" 2>/dev/null
else  # on the Ubuntu server: show it on the Air through its reverse tunnel
  ssh -o ConnectTimeout=5 -o BatchMode=yes air "/usr/bin/osascript -e 'display notification \"$M\" with title \"$T\" sound name \"Glass\"'" 2>/dev/null
fi
ssh -o ConnectTimeout=5 -o BatchMode=yes pro "/usr/bin/osascript -e 'display notification \"$M\" with title \"$T\" sound name \"Glass\"'" 2>/dev/null
exit 0
