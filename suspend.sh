#!/bin/sh

# prevent double-trigger
if [ -f /tmp/sys_suspend.lock ]; then
    exit 0
fi

touch /tmp/sys_suspend.lock
( sleep 2; rm -f /tmp/sys_suspend.lock ) &

exec systemctl suspend
