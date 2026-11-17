#!/bin/bash

revert() {
    xset dpms 0 0 7200
}
trap revert HUP INT TERM
xset +dpms dpms 30 30 30

i3lock \
    --nofork \
    --image="$HOME/Pictures/background/Neon_Red_v2.png" \
    --color=010614

status=$?
revert

if ((status == 0)); then
    qtile cmd-obj -o root -f fire_user_hook -a run_on_unlock
fi

