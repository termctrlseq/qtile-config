#!/bin/bash

i3lock --nofork --image="$HOME/Pictures/background/Neon_red.png"
status=$?

if ((status == 0)); then
    # Run after successful unlock
    qtile cmd-obj -o root -f fire_user_hook -a run_on_unlock
fi

