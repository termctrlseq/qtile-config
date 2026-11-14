import re
import time
from pathlib import Path
from subprocess import Popen

from libqtile import hook, layout, qtile
from libqtile.backend.wayland.inputs import InputConfig
from libqtile.config import (
    Click,
    Drag,
    Key,
    Match,
)
from libqtile.lazy import lazy
from libqtile.log_utils import logger

from display import update_displays  # noqa: F401
from globals_config import (
    ALT,
    CTRL,
    IS_WAYLAND,
    LAYOUT_BORDER_WIDTH,
    LAYOUT_MARGIN,
    SHIFT,
    SUPER,
    Color,
    dump_pos,
    font_main,
    font_main_size,
    restore_pos,
    save_pos,
)
from groups import groups
from imv import (  # type: ignore  # noqa: F401
    imv,
    imv_startup,
)
from keybindings import keys
from screens_config import generate_screens  # noqa: F401


@hook.subscribe.startup_once
def autostart():
    auto_start_sh = "autostart.sh"
    if IS_WAYLAND:
        # do not block when calling wlr-randr on wayland (no subprocess.run())
        auto_start_sh = "autostart_wayland.sh"

    Popen([str(Path(__file__).with_name(auto_start_sh))])


@hook.subscribe.startup
def startup():
    qtile.screens[0].set_wallpaper(
        str(Path("~/Pictures/background/Neon.png").expanduser())
    )


@hook.subscribe.resume
def resume():
    qtile.screens[0].set_wallpaper(
        str(Path("~/Pictures/background/Neon_green.png").expanduser())
    )


@hook.subscribe.user("run_on_unlock")  # type: ignore
def run_on_unlock():
    screen = qtile.screens[0]

    logger.warning(f"Initial wallpaper: {time.time()}")
    screen.set_wallpaper(
        str(Path("~/Pictures/background/Neon_green.png").expanduser())
    )

    def change_wallpaper():
        logger.warning(f"Delayed wallpaper: {time.time()}")
        screen.set_wallpaper(
            str(Path("~/Pictures/background/Neon.png").expanduser())
        )

    qtile.call_later(1, change_wallpaper)


@hook.subscribe.client_new
def client_new(client):
    if client.match(Match(wm_class="imv")):
        imv_startup()
    elif client.name == "scratchpad":
        client.keep_above(True)


@hook.subscribe.client_focus
def client_focus(client):
    if client.info()["floating"]:
        client.move_to_top()


@hook.subscribe.client_killed
def client_killed(client):
    client_info = client.info()
    if client_info["floating"] and not client_info["fullscreen"]:
        save_pos(client)
        dump_pos()


@hook.subscribe.float_change
def float_change():
    cur_win = qtile.current_window
    cur_win_info = cur_win.info()
    if (
        cur_win
        and cur_win_info["floating"]
        and not cur_win_info["fullscreen"]
    ):
        restore_pos(cur_win)


# Keys append/extend {{{
# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is
# loaded before qtile is started
# We therefore defer the check until the key binding is run
# by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            [ALT, CTRL],
            f"f{vt}",
            lazy.core.change_vt(vt).when(
                func=lambda: qtile.core.name == "wayland"
            ),
            desc=f"Switch to VT{vt}",
        )
    )


for i in groups:
    keys.extend(
        [
            # SUPER + group number = switch to group
            Key(
                [SUPER],
                i.name,
                lazy.group[i.name].toscreen(),
                desc=f"Switch to group {i.name}",
            ),
            # SUPER + shift + group number = switch to & move focused
            # window to group
            Key(
                [SUPER, SHIFT],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc=f"Switch to & move focused window to group {i.name}",
            ),
            # Or, use below if you prefer not to switch to that group.
            # # SUPER + control + group number = move focused window to group
            Key(
                [SUPER, CTRL],
                i.name,
                lazy.window.togroup(i.name),
                desc=f"move focused window to group {i.name}",
            ),
        ]
    )  # }}}

# Layouts {{{
layouts = [
    layout.Columns(
        border_focus=Color.BLUE,
        border_normal=Color.MID_GRAY,
        border_on_single=True,
        border_width=LAYOUT_BORDER_WIDTH,
        grow_amount=5,
        initial_ratio=1.7,
        insert_position=1,
        margin=LAYOUT_MARGIN,
        margin_on_single=LAYOUT_MARGIN,
        single_border_width=LAYOUT_BORDER_WIDTH,
        wrap_focus_columns=False,
    ),
    layout.Max(),
]
floating_layout = layout.Floating(
    border_focus=Color.BLUE,
    border_normal=Color.MID_GRAY,
    border_width=LAYOUT_BORDER_WIDTH,
    float_rules=[
        # Run `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(title=re.compile(r"^Task.*")),
        Match(wm_class="org.gnome.Nautilus"),
        Match(title="Virtual Machine Manager"),
        Match(wm_class="virt-viewer"),
        Match(wm_class="imv"),
        Match(wm_class="pcmanfm"),
        Match(wm_class="feh"),
        Match(role=re.compile(r"EMailBrowser.*")),
        Match(wm_class="solaar"),
        Match(wm_class=re.compile("^Chromium$")),
    ],
)  # }}}

# Screens/widgets
widget_defaults = {
    "font": font_main,
    "fontsize": font_main_size,
    "padding": 3,
    "foreground": Color.LIGHT_GRAY,
}
extension_defaults = widget_defaults.copy()


# Mouse: Drag floating layouts. {{{


mouse = [
    Drag(
        [SUPER],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [SUPER],
        "Button3",
        lazy.window.set_size_floating(),
        start=lazy.window.get_size(),
    ),
    Click([SUPER], "Button2", lazy.window.bring_to_front()),
    Click(
        [SUPER],
        "Button5",
        lazy.spawn("playerctl position 5+"),
    ),
    Click(
        [SUPER],
        "Button4",
        lazy.spawn("playerctl position 5-"),
    ),
    # Click([CTRL], "Button1", mouse_click()),
]  # }}}

auto_fullscreen = True
auto_minimize = False
bring_front_click = True
cursor_warp = False
dgroups_app_rules = []  # type: list
dgroups_key_binder = None
floats_kept_above = False
focus_on_window_activation = "smart"
focus_previous_on_window_remove = True
follow_mouse_focus = "click_or_drag_only"
reconfigure_screens = True
wl_input_rules = {
    "type:touchpad": InputConfig(natural_scroll=True, pointer_accel=0.3),
    "type:pointer": InputConfig(natural_scroll=False),
}

wmname = "LG3D"
# vim:foldmethod=marker
