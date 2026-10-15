#!/bin/zsh
# notify.sh "title" "text": a Mac notification on the Air and on the MacBook Pro the captain works on.
T="${1//\"/\'}"; M="${2//\"/\'}"
/usr/bin/osascript -e "display notification \"$M\" with title \"$T\" sound name \"Glass\"" 2>/dev/null
ssh -o ConnectTimeout=5 -o BatchMode=yes pro "/usr/bin/osascript -e 'display notification \"$M\" with title \"$T\" sound name \"Glass\"'" 2>/dev/null
exit 0
