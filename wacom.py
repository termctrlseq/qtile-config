"""
wacom_touch() {
    local ft_device ft_state
    ft_device="$(xsetwacom list devices | awk '/type: TOUCH/ {print $8}')"
    ft_state="$(xsetwacom get "$ft_device" Touch)"

    if [[ $ft_state == 'off' ]]; then
        ft_state='on'
    elif [[ $ft_state == 'on' ]]; then
        ft_state='off'
    else
        return 1
    fi

    xsetwacom set "$ft_device" "Touch" "$ft_state"
}
"""

import logging
from subprocess import run

from libqtile.lazy import lazy

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def get_touch_device() -> str | None:
    cmd = ["xsetwacom", "list", "devices"]
    res = run(
        cmd,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )

    if res.returncode != 0:
        logger.warning(f"'{' '.join(cmd)}' exited with: {res.returncode}")
        return None

    lines = res.stdout.splitlines()
    device = None
    for line in lines:
        if "type: TOUCH" in line:
            device = line.split()[7]

    return device


def get_touch_state(device: str) -> str | None:
    cmd = ["xsetwacom", "get", device, "Touch"]
    res = run(
        cmd,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )

    if res.returncode != 0:
        logger.warning(f"'{' '.join(cmd)}' exited with: {res.returncode}")
        return None

    return res.stdout.splitlines()[0] if res.stdout else None


@lazy.function
def wacom_touch_toggle(_qtile) -> None:
    if (device := get_touch_device()) is None:
        logger.warning("Unable to get TOUCH device")
        return

    if (current_state := get_touch_state(device)) is None:
        logger.warning("Unable to find current TOUCH state")
        return

    if current_state == "on":
        new_state = "off"
    elif current_state == "off":
        new_state = "on"
    else:
        logger.warning(f"Unknown state: {current_state}")
        return

    cmd = ["xsetwacom", "set", device, "Touch", new_state]
    res = run(cmd, check=False)

    if res.returncode != 0:
        logger.warning(f"'{' '.join(cmd)}' exited with: {res.returncode}")
