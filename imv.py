"""
User hook for imv.
Applies orientation from exif tag and resizes imv window.

Requires:
    pillow

Example usage from imv config:
    <Right> = next; exec DISPLAY=${DISPLAY%.*} qtile cmd-obj -o cmd -f fire_user_hook -a imv $imv_pid "$imv_current_file"
"""

import os
from subprocess import Popen, SubprocessError, run

from libqtile import hook, qtile
from libqtile.config import Match

from globals_config import (
    LAYOUT_BORDER_WIDTH,
    LAYOUT_MARGIN,
    get_pos,
)


def get_screen_rect(margin: int | list, border: int) -> tuple[int, ...]:
    """Return min/max x/y."""
    if isinstance(margin, int):
        margin_top = margin_right = margin_bottom = margin_left = margin
    else:
        margin_top, margin_right, margin_bottom, margin_left = margin

    cur_scr = qtile.current_screen
    bars = {pos: 0 for pos in ["top", "bottom", "left", "right"]}
    for pos in cur_scr.items("bar")[1]:
        bar = getattr(cur_scr, pos)
        bars[pos] = bar.info()["fullsize"]

    min_x = bars["left"] + margin_left
    min_y = bars["top"] + margin_top
    max_x = (
        cur_scr.info()["width"] - bars["right"] - margin_right - border * 2
    )
    max_y = (
        cur_scr.info()["height"] - bars["bottom"] - margin_bottom - border * 2
    )
    max_width = max_x - min_x - border * 2
    max_height = max_y - min_y - border * 2

    return min_x, min_y, max_x, max_y, max_width, max_height


@hook.subscribe.user("imv")  # type: ignore
def imv(pid: str, file: str) -> None:
    if not pid or not file:
        return

    min_x, min_y, max_x, max_y, max_width, max_height = get_screen_rect(
        LAYOUT_MARGIN, LAYOUT_BORDER_WIDTH
    )

    try:
        from PIL import Image

        with Image.open(file) as img:
            img_width, img_height = img.size
            img_orientation = img.getexif().get(274, 1)

    except (
        ImportError,
        OSError,
    ):
        img_width = max_width * 3 // 4
        img_height = max_height
        img_orientation = 1

    # Orientation: 1 -> 0°, 6 -> 90°, 3 -> 180°, 8 -> 270°
    rotate_dict = {6: 90, 3: 180, 8: 270}
    zoom_amount: float = 0
    xy_swapped = False
    rotate_cmd: list[str] | None = None

    # Find orientation
    if img_orientation in rotate_dict:
        rotate_cmd = [
            "imv-msg",
            pid,
            f"rotate to {rotate_dict[img_orientation]}",
        ]
        # 90° and 270° swap horizontal and vertical
        if img_orientation % 2 == 0:
            img_height, img_width = img_width, img_height
            xy_swapped = True

    # Fit image in the available screen area
    if (
        img_width > max_width
        and (img_height * max_width / img_width) <= max_height
    ):
        width = max_width
        height = img_height * max_width / img_width
        zoom_amount = height * 100 / img_height
    elif (
        img_height > max_height
        and (img_width * max_height / img_height) <= max_width
    ):
        height = max_height
        width = img_width * max_height / img_height
        zoom_amount = width * 100 / img_width
    else:
        width = img_width
        height = img_height

    # Reduce size of landscapes except for panorama
    if height > max_height * 0.75 and height < width < 2.5 * height:
        width *= 0.75
        height *= 0.75
        zoom_amount *= 0.75

    # Find new position
    pos_x = min_x + (max_width - width) / 2
    pos_y = min_y + (max_height - height) / 2

    if saved_pos := get_pos("imv"):
        saved_center_x = saved_pos["x"] + saved_pos["width"] / 2
        saved_center_y = saved_pos["y"] + saved_pos["height"] / 2
        center_x = pos_x + width / 2
        center_y = pos_y + height / 2
        if (
            abs(center_x - saved_center_x) > 50
            or abs(center_y - saved_center_y) > 50
        ):
            pos_x += saved_center_x - center_x
            pos_y += saved_center_y - center_y

            if pos_x + width > max_x:
                pos_x -= (pos_x + width) - max_x
            if pos_y + height > max_y:
                pos_y -= (pos_y + height) - max_y

            pos_x = max(pos_x, min_x)
            pos_y = max(pos_y, min_y)

    # Move/resize current window
    cur_win = qtile.current_window
    if (
        cur_win.match(Match(wm_class="imv"))
        and cur_win.info()["floating"]
        and not cur_win.info()["fullscreen"]
    ):
        cur_win.set_size_floating(int(width), int(height))
        cur_win.set_position_floating(int(pos_x), int(pos_y))

        if rotate_cmd:
            Popen(rotate_cmd)
        if not xy_swapped:
            Popen(["imv-msg", pid, "scaling full"])
        # scaling doesn't work when x/y are switched,
        # so set zoom with delay
        elif zoom_amount:

            def imv_zoom():
                Popen(["imv-msg", pid, "zoom actual"])
                Popen(["imv-msg", pid, f"zoom {int(zoom_amount) + 1}%"])

            qtile.call_later(0.2, imv_zoom)


# runs when imv window is created (called from client_new hook)
def imv_startup(cmd: str | None = None) -> None:
    try:
        result = run(
            ["pgrep", "--newest", "^imv"],
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
    except SubprocessError:
        return

    cmd = f"{cmd}; " if cmd else ""
    display = os.environ.get("DISPLAY", ":0")
    if result.stdout:
        pid = result.stdout.strip()
        Popen(
            [
                "imv-msg",
                pid,
                (
                    f"{cmd}exec DISPLAY={display} qtile cmd-obj"
                    " -o root"
                    " -f fire_user_hook"
                    " -a imv $imv_pid $imv_current_file"
                ),
            ]
        )
