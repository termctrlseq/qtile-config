import contextlib
import json
import os
from enum import StrEnum
from pathlib import Path
from subprocess import CalledProcessError, run

import cairocffi
from libqtile import pangocffi, qtile
from libqtile.lazy import lazy
from libqtile.log_utils import logger


def get_xd_ports(default=None):
    if default is None:
        default = ["DP-1", "HDMI-1"]
    try:
        result = run(
            ["/bin/sh", "-c", "xrandr | awk '/ connected/ {print $1}'"],
            capture_output=True,
            check=True,
            encoding="utf-8",
        )

    except CalledProcessError as e:
        logger.error(f"{e}")
        return default

    if result.returncode == 0:
        return sorted(result.stdout.splitlines())
    else:
        logger.error(f"xrandr return code: {result.returncode}")
        logger.error(f"xrandr error: {result.returncode}")
        return default


port_to_screen = {}
IS_WAYLAND = qtile.core.name == "wayland"
wldisplay_ports = ["DP-1", "HDMI-A-1"]
display_ports = wldisplay_ports if IS_WAYLAND else get_xd_ports()
display_modes = ["2560x1440", "1680x1050"]
display_rates = [100, 60]
display_widths = [2560, 1680]
display_v_offsets = [0, 0]

# Modifiers
ALT = "mod1"
CTRL = "control"
SHIFT = "shift"
SUPER = "mod4"

# Default programs
terminal = "alacritty"
terminal_huge = "kitty -o font_size=24"
browser = "firefox"
email_client = "evolution"
file_manager = "pcmanfm"

# Font
font_main = "JetbrainsMono Nerd Font Bold"
font_main_size = 16


def get_char_width():
    surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, 1, 1)
    ctx = cairocffi.Context(surface)
    layout = pangocffi.create_layout(ctx)  # type: ignore
    layout.set_font_description(
        pangocffi.FontDescription.from_string(
            f"{font_main} {font_main_size}px"
        )
    )
    layout.set_text(" ")
    return layout.get_pixel_size()[0]


font_other_size = 14
dmenu_font = "JetbrainsMono Nerd Font:bold:size=14"

# Window sizes
LAYOUT_MARGIN = 2
LAYOUT_BORDER_WIDTH = 2


# Colors
class Color(StrEnum):
    YELLOW = "#e0af68"
    MUTED_YELLOW = "#b49a72"
    MUTED_AMBER = "#9b8063"
    PINK = "#ad8ee6"
    SOFT_LAVENDER = "#9a83bf"
    GREEN = "#527a73"
    MUTED_TEAL = "#718f88"
    BLUE = "#7079db"
    SLATE_BLUE = "#727a91"
    MUTED_BLUE = "#7883a8"
    SOFT_BLUE = "#4a5083"
    PURPLE = "#8880a0"
    LIGHT_VIOLET = "#7478a1"
    GRAY_VIOLET = "#77758e"
    MUTED_VIOLET_GRAY = "#666b8e"
    DARK_VIOLET_GRAY = "#5d6284"
    DARK_VIOLET = "#515478"
    LIGHT_GRAY = "#a1a1a1"
    LIGHT_MID_GRAY = "#88888a"
    MID_GRAY = "#444455"
    DARK_GRAY = "#212146"
    DARK_BLUE_GRAY = "#25253b"
    BLACK_GRAY = "#12121b"
    BLACK = "#010614"
    BLACK_BLUE = "#0c0c0f"
    PURE_BLACK = "#000000"


displays = {  # goes into widget_widths
    f"disp{i}": round(font_main_size * 1.786)
    for i, _ in enumerate(display_ports, start=1)
}

widget_widths = dict(
    groupbox=font_main_size * 18.625,
    clock=font_main_size * 10.6875,
    sep=5,
    tray=round(font_main_size * 1.786),
    vol_icon=round(font_main_size * 2.5),
    vol_perc=round(font_main_size * 2.143),
    audio_out=round(font_main_size * 1.786),
    thermal=round(font_main_size * 4.286),
    cpu=round(font_main_size * 4.643),
    mem_icon=round(font_main_size * 1.43),
    mem_g=round(font_main_size * 3.57),
    net_down=round(font_main_size * 4.286),
    net_up=round(font_main_size * 4.643),
    **displays,
    quick_exit=round(font_main_size * 1.43),
)

saved_pos_dict: dict[str, dict[str, int]] = {}
data_dir = (
    Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    / "qtile"
)
data_dir.mkdir(parents=True, exist_ok=True)
saved_pos_json = data_dir / "saved_pos.json"


def save_pos(client) -> None:
    """Save window position and size to dict."""
    pos_x, pos_y = client.get_position()
    width, height = client.get_size()
    # global saved_pos_dict
    if client.name != "scratchpad":
        saved_pos_dict[client.info()["wm_class"][0]] = {
            "x": pos_x,
            "y": pos_y,
            "width": width,
            "height": height,
        }


def restore_pos(client) -> None:
    """Restore saved position."""
    wm_class = client.info()["wm_class"][0]
    if saved_pos := get_pos(wm_class):
        client.set_position_floating(
            saved_pos["x"],
            saved_pos["y"],
        )
        client.set_size_floating(
            saved_pos["width"],
            saved_pos["height"],
        )


def dump_pos(
    saved_pos_dict: dict[str, dict[str, int]] = saved_pos_dict,
    saved_pos_json: Path = saved_pos_json,
) -> None:
    """Write saved positions dict to json file."""
    load_pos()
    with saved_pos_json.open("w", encoding="utf-8") as f:
        json.dump(saved_pos_dict, f, indent=2)


def load_pos(saved_pos_json: Path = saved_pos_json) -> None:
    """Load saved position dict from json file."""
    # global saved_pos_dict
    with (
        contextlib.suppress(ValueError, FileNotFoundError),
        saved_pos_json.open() as f,
    ):
        json_dict = json.load(f)
        for key in json_dict:
            saved_pos_dict.setdefault(key, json_dict[key])


def get_pos(wm_class: str) -> dict[str, int] | None:
    """Return saved position dict for wm_class."""
    saved_pos = saved_pos_dict.get(wm_class)
    if wm_class and saved_pos is None:
        load_pos()

    return saved_pos_dict.get(wm_class)


@lazy.function
def move_floating(qtile, dx, dy):
    cur_win = qtile.current_window
    if cur_win:
        cur_win.move_floating(dx, dy)
        save_pos(cur_win)


@lazy.function
def resize_floating(qtile, dx, dy):
    cur_win = qtile.current_window
    if cur_win:
        cur_win.resize_floating(dx, dy)
        save_pos(cur_win)


@lazy.function
def default_app(qtile):
    group_label = qtile.current_group.label
    match group_label:
        case "browser":
            qtile.spawn(browser)
        case "email":
            qtile.spawn(email_client)
        case "media":
            qtile.spawn(file_manager)
        case "term":
            qtile.spawn(terminal)
        case "":
            qtile.spawn("firefox --private-window")


@lazy.function
def move_to_next_screen(qtile):
    cur_win = qtile.current_window
    if (num_scr := len(qtile.get_screens())) > 1:
        if (idx := cur_win.group.screen.info()["index"]) == num_scr - 1:
            idx = 0
        else:
            idx += 1
        cur_win.toscreen(idx)
        qtile.to_screen(idx)


@lazy.function
def move_to_prev_screen(qtile):
    cur_win = qtile.current_window
    if (num_scr := len(qtile.get_screens())) > 1:
        if (idx := cur_win.group.screen.info()["index"]) == 0:
            idx = num_scr - 1
        else:
            idx -= 1
        cur_win.toscreen(idx)
        qtile.to_screen(idx)


@lazy.function
def close_window(qtile) -> None:
    cur_win = qtile.current_window
    if cur_win.name == "scratchpad":
        qtile.spawn("ydotool key 16:1 16:0")
    else:
        cur_win.kill()
