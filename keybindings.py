from pathlib import Path

from libqtile import extension
from libqtile.config import Key
from libqtile.lazy import lazy

from display import toggle_display, toggle_other_displays
from float_fs_toggle import toggle_floating, toggle_fullscreen
from globals_config import (
    ALT,
    CTRL,
    SHIFT,
    SUPER,
    Color,
    browser,
    display_ports,
    dmenu_font,
    email_client,
    file_manager,
    move_floating,
    move_to_next_screen,
    resize_floating,
    terminal,
    terminal_huge,
)
from screenshot import screenshot
from wacom import wacom_touch_toggle

suspend_script = str(Path(__file__).parent / "suspend.sh")

keys = [  # {{{
    # Windows focus
    Key([SUPER], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([SUPER], "Left", lazy.layout.left(), desc="Move focus to left"),
    Key([SUPER], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([SUPER], "Right", lazy.layout.right(), desc="Move focus to right"),
    Key([SUPER], "j", lazy.layout.down(), desc="Move focus down"),
    Key([SUPER], "Down", lazy.layout.down(), desc="Move focus down"),
    Key([SUPER], "k", lazy.layout.up(), desc="Move focus up"),
    Key([SUPER], "Up", lazy.layout.up(), desc="Move focus up"),
    Key(
        [ALT],
        "Tab",
        lazy.group.focus_back(),
        desc="Focus the window that had focus before the current.",
    ),
    # Move windows between left/right columns or move up/down in
    # current stack.
    Key(
        [SHIFT, SUPER],
        "j",
        lazy.layout.shuffle_down(),
        desc="Move window down",
    ),
    Key([SHIFT, SUPER], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    Key(
        [SHIFT, SUPER],
        "h",
        lazy.layout.swap_column_left(),
        desc="Swap column left",
    ),
    Key(
        [SHIFT, SUPER],
        "l",
        lazy.layout.swap_column_right(),
        desc="Swap column right",
    ),
    # Move floating window
    Key(
        [ALT, SUPER],
        "h",
        move_floating(-50, 0),
        desc="Move window left by 50",
    ),
    Key(
        [ALT, SUPER],
        "l",
        move_floating(50, 0),
        desc="Move window right by 50",
    ),
    Key(
        [ALT, SUPER],
        "j",
        move_floating(0, 50),
        desc="Move window down by 50",
    ),
    Key(
        [ALT, SUPER],
        "k",
        move_floating(0, -50),
        desc="Move window up by 50",
    ),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key(
        [CTRL, SUPER],
        "h",
        lazy.layout.grow_left(),
        desc="Grow window to the left",
    ),
    Key(
        [CTRL, SUPER],
        "Left",
        lazy.layout.grow_left(),
        desc="Grow window to the left",
    ),
    Key(
        [CTRL, SUPER],
        "l",
        lazy.layout.grow_right(),
        desc="Grow window to the right",
    ),
    Key(
        [CTRL, SUPER],
        "Right",
        lazy.layout.grow_right(),
        desc="Grow window to the right",
    ),
    Key(
        [CTRL, SUPER],
        "j",
        lazy.layout.grow_down(),
        desc="Grow window down",
    ),
    Key([CTRL, SUPER], "k", lazy.layout.grow_up(), desc="Grow window up"),
    # Resize floating
    Key(
        [ALT, SHIFT],
        "h",
        resize_floating(-50, 0),
        desc="Shrink floating window horizontally",
    ),
    Key(
        [ALT, SHIFT],
        "l",
        resize_floating(50, 0),
        desc="Grow floating window horizontally",
    ),
    Key(
        [ALT, SHIFT],
        "j",
        resize_floating(0, 50),
        desc="Grow floating window vertically",
    ),
    Key(
        [ALT, SHIFT],
        "k",
        resize_floating(0, -50),
        desc="Shrink floating window vertically",
    ),
    Key(
        [SUPER],
        "n",
        lazy.layout.reset(),
        desc="Resets column widths, respecting 'initial_ratio' value",
    ),
    Key(
        [SHIFT, SUPER],
        "n",
        lazy.layout.normalize(),
        desc="Reset all window sizes",
    ),
    # Toggle between different layouts as defined below
    Key([SUPER], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    # Switch screen
    Key(
        [ALT, SUPER],
        "Space",
        lazy.next_screen(),
        desc="Move to the next screen",
    ),
    Key([SUPER], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [SUPER],
        "f",
        toggle_floating(),
        desc="Toggle floating on the focused window",
    ),
    Key(
        [],
        "F11",
        toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
]  # }}}

_launch = [  # {{{
    Key(
        [SUPER],
        "a",
        lazy.run_extension(
            extension.J4DmenuDesktop(
                dmenu_font=dmenu_font,
                dmenu_ignorecase=True,
                dmenu_prompt=" ",
                j4dmenu_generic=False,
                j4dmenu_terminal=terminal,
                background=Color.BLACK_GRAY,
                foreground=Color.GREEN,
                selected_background=Color.DARK_GRAY,
                selected_foreground=Color.PINK,
            )
        ),
        desc="Open application menu in top bar",
    ),
    Key(
        [CTRL, SUPER],
        "r",
        lazy.reload_config(),
        desc="Reload the config",
    ),
    Key(
        [SHIFT, SUPER],
        "r",
        lazy.restart(),
        desc="Restart Qtile",
    ),
    Key([SUPER], "z", lazy.spawn(suspend_script), desc="Suspend"),
    Key([CTRL, SUPER], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([SUPER], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key(
        [ALT, SUPER],
        "Return",
        lazy.spawn(terminal_huge),
        desc="Launch huge terminal",
    ),
    Key([SUPER], "b", lazy.spawn(browser), desc="Open web browser"),
    Key([SUPER], "e", lazy.spawn(email_client), desc="Open email client"),
    Key(
        [SUPER],
        "s",
        lazy.spawn(file_manager),
        desc="Open file manager",
    ),
    Key(
        [],
        "Print",
        screenshot(),
        desc="Take a screenshot",
    ),
]  # }}}

_audio = [  # {{{
    Key(
        [],
        "XF86AudioRaiseVolume",
        # lazy.spawn("amixer -q sset Master 1%+ unmute"),
        lazy.spawn("wpctl set-volume @DEFAULT_SINK@ 1%+"),
        desc="Raise volume by 1%",
    ),
    Key(
        [],
        "XF86AudioLowerVolume",
        # lazy.spawn("amixer -q sset Master 1%- unmute"),
        lazy.spawn("wpctl set-volume @DEFAULT_SINK@ 1%-"),
        desc="Lower volume by 1%",
    ),
    Key(
        [],
        "XF86AudioPlay",
        lazy.spawn("playerctl play-pause"),
        desc="Toggle play/pause",
    ),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next"), desc="Next track"),
    Key([CTRL, SUPER], "m", lazy.spawn("playerctl next"), desc="Next track"),
    Key(
        [],
        "XF86AudioPrev",
        lazy.spawn("playerctl previous"),
        desc="Previous track",
    ),
    Key(
        [CTRL, SUPER],
        "n",
        lazy.spawn("playerctl previous"),
        desc="Previous track",
    ),
]  # }}}

_monitor = [  # {{{
    # Turn monitors on/off
    Key(
        [ALT, CTRL],
        "1",
        toggle_display(display_ports[0]),
        desc="Toggle left display",
    ),
    Key(
        [ALT, CTRL],
        "2",
        toggle_display(display_ports[1]),
        desc="Toggle right display",
    ),
    Key([SUPER], "d", toggle_other_displays(), desc="Toggle other display"),
    # Move focus and/or windows between screens
    Key(
        [ALT, CTRL],
        "Tab",
        lazy.next_screen(),
        desc="Switch to the next screen.",
    ),
    Key(
        [ALT, SHIFT],
        "Tab",
        move_to_next_screen(),
        desc="Move window and focus to next screen.",
    ),
    Key(
        [ALT, SUPER],
        "1",
        lazy.to_screen(0),
        desc="Focus primary screen.",
    ),
    Key(
        [ALT, SUPER],
        "2",
        lazy.to_screen(-1),
        desc="Focus other screen.",
    ),
]  # }}}

_scratchpad = [  # {{{
    Key(
        [SUPER],
        "m",
        lazy.group["0"].dropdown_toggle("music"),
        desc="Open music player in a dropdown",
    ),
    Key(
        [CTRL, SUPER],
        "Return",
        lazy.group["0"].dropdown_toggle("kitty"),
        desc="Open dropdown terminal (small)",
    ),
    Key(
        [SHIFT, SUPER],
        "t",
        lazy.group["0"].dropdown_toggle("big_kitty"),
        desc="Open dropdown terminal (tall)",
    ),
    Key(
        [SUPER],
        "F1",
        lazy.group["0"].dropdown_toggle("key_bindings"),
        desc="List key bindings",
    ),
]  # }}}

_mouse = [  # {{{
    Key(
        [SHIFT, SUPER],
        "F1",
        lazy.spawn("ydotool mousemove -- -250 0"),
        desc="Move pointer left",
    ),
    Key(
        [SHIFT, SUPER],
        "F2",
        lazy.spawn("ydotool mousemove -- 250 0"),
        desc="Move pointer right",
    ),
    Key(
        [SHIFT, SUPER],
        "F3",
        lazy.spawn("ydotool mousemove -- 0 150"),
        desc="Move pointer up",
    ),
    Key(
        [SHIFT, SUPER],
        "F4",
        lazy.spawn("ydotool mousemove -- 0 -150"),
        desc="Move pointer down",
    ),
    Key(
        [ALT, SHIFT, SUPER],
        "F1",
        lazy.spawn("ydotool mousemove -- -25 0"),
        desc="Move pointer left",
    ),
    Key(
        [ALT, SHIFT, SUPER],
        "F2",
        lazy.spawn("ydotool mousemove -- 25 0"),
        desc="Move pointer right",
    ),
    Key(
        [ALT, SHIFT, SUPER],
        "F3",
        lazy.spawn("ydotool mousemove -- 0 25"),
        desc="Move pointer up",
    ),
    Key(
        [ALT, SHIFT, SUPER],
        "F4",
        lazy.spawn("ydotool mousemove -- 0 -25"),
        desc="Move pointer down",
    ),
    # Wacom
    Key(
        [SUPER],
        "c",
        wacom_touch_toggle(),
        desc="Toggle wacom touch",
    ),
]  # }}}

keys.extend(_launch)
keys.extend(_audio)
keys.extend(_monitor)
keys.extend(_scratchpad)
keys.extend(_mouse)

# vim: foldmethod=marker
