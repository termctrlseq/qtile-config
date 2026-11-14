#!/bin/sh

# autostart.sh

xrandr \
    --output DP-1 --mode 2560x1440 --rate 100 --pos 0x0 --primary \
    --output HDMI-1 --mode 1680x1050 --rate 60 --pos 2560x0

picom &
xset dpms 0 0 7200 s off r rate 600

if xsetwacom list devices | grep -q Wacom; then
    finger_touch="$(xsetwacom list devices | awk '/Finger touch/{print $8}')"
    pad="$(xsetwacom list devices | awk '/Pad pad/{print $8}')"

    # effectively disables zoom gesture
    if [ -n "${finger_touch}" ]; then
        xsetwacom set "${finger_touch}" ZoomDistance 10000
        xsetwacom set "${finger_touch}" ScrollDistance 200
    fi

    # switch left and right click
    if [ -n "${pad}" ]; then
        xsetwacom set "${pad}" "Button" "1" "button +3 "
        xsetwacom set "${pad}" "Button" "3" "button +1 "

    fi
fi

xss-lock --transfer-sleep-lock -- "$HOME/.config/qtile/i3lock_wrapper.sh"

