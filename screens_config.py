# See: https://docs.qtile.org/en/latest/manual/config/screens.html#dynamic-screen-configuration

import re
from pathlib import Path

from libqtile import bar, widget
from libqtile.config import Screen, ScreenRect
from libqtile.lazy import lazy
from libqtile.log_utils import logger

from audio_sink import audio_output_widget
from display import display_widget
from globals_config import (
    LAYOUT_MARGIN,
    Color,
    close_window,
    default_app,
    font_main_size,
    font_other_size,
    get_char_width,
    port_to_screen,
    widget_widths,
)


def get_main_screen(screen_rect: ScreenRect) -> Screen:
    font_main_char_width = get_char_width()
    widgets_rwidth = sum(list(widget_widths.values())[2:])
    _mpris_width = int(
        screen_rect.width / 2 - widget_widths["clock"] / 2 - widgets_rwidth
    )
    _win_name_max_chars = round(
        (
            screen_rect.width / 2
            - (
                widget_widths["clock"] / 2
                + widget_widths["groupbox"]
                + LAYOUT_MARGIN
            )
        )
        / font_main_char_width
    )

    def remove_markup(text):
        text = re.sub(r"(<.+?>|&.+?;)", "", text.splitlines()[0])
        return f"{text:^{_win_name_max_chars}}"

    return Screen(
        top=bar.Bar(
            [
                widget.GroupBox(
                    active=Color.PURPLE,
                    background=[Color.DARK_GRAY, Color.BLACK],
                    inactive=Color.MID_GRAY,
                    mouse_callbacks={"Button3": default_app()},
                    other_current_screen_border=Color.PURPLE,
                    other_screen_border=Color.MID_GRAY,
                    this_current_screen_border=Color.BLUE,
                    this_screen_border=Color.SOFT_BLUE,
                    urgent_border=Color.PINK,
                ),
                widget.Notify(
                    background=[Color.BLACK, Color.DARK_BLUE_GRAY],
                    background_low=[Color.BLACK, Color.DARK_BLUE_GRAY],
                    default_timeout=None,
                    default_timeout_low=None,
                    default_timeout_urgent=None,
                    fontshadow=Color.BLACK_GRAY,
                    foreground=Color.PINK,
                    foreground_low=Color.PINK,
                    max_chars=_win_name_max_chars,
                    parse_text=remove_markup,
                ),
                widget.WindowName(
                    background=[Color.BLACK, Color.DARK_BLUE_GRAY],
                    fontshadow=Color.BLACK_BLUE,
                    foreground=Color.LIGHT_VIOLET,
                    max_chars=_win_name_max_chars,
                    mouse_callbacks={
                        "Button1": lazy.widget["notify"].display(),
                        "Button3": close_window(),
                        "Button8": lazy.prev_layout(),
                        "Button9": lazy.next_layout(),
                    },
                ),
                widget.Clock(
                    font="sans bold",
                    format=" %a %b %d %I:%M %p ",
                    mouse_callbacks={
                        "Button1": lazy.spawn(
                            "firefox https://calendar.google.com/calendar/u/0/r"
                        ),
                        "Button3": lazy.spawn(
                            "firefox https://keep.google.com/#home"
                        ),
                    },
                ),
                widget.Sep(
                    foreground=Color.DARK_GRAY,
                    linewidth=widget_widths["sep"],
                    padding=0,
                    size_percent=100,
                ),
                widget.Spacer(
                    mouse_callbacks={"Button1": lazy.spawn("easyeffects")}
                ),
                widget.StatusNotifier(icon_size=font_main_size),
                widget.Mpris2(
                    background=[Color.BLACK, Color.DARK_BLUE_GRAY],
                    fontshadow=Color.BLACK_BLUE,
                    foreground=Color.LIGHT_VIOLET,
                    format="{xesam:title} - {xesam:artist} │ {qtile:player} ",
                    mouse_callbacks={
                        # left click: play/pause
                        "Button1": lazy.spawn("playerctl play-pause"),
                        # right click: open music player
                        "Button3": lazy.group["0"].dropdown_toggle("music"),
                        # scroll down: seek back in 5s decrements
                        "Button4": lazy.spawn("playerctl position 5-"),
                        # scroll up: seek forward in 5s increments
                        "Button5": lazy.spawn("playerctl position 5+"),
                        # back button: previous track
                        "Button8": lazy.spawn("playerctl previous"),
                        # forward button: next track
                        "Button9": lazy.spawn("playerctl next"),
                    },
                    no_metadata_text=f"{'•         •         •':^40}",
                    paused_text="  {track}",
                    playing_text="  {track}",
                    poll_interval=5,
                    scroll=True,
                    scroll_fixed_width=True,
                    stopped_text="  ",
                    width=_mpris_width,
                ),
                widget.Volume(
                    check_mute_command=(
                        "wpctl get-volume @DEFAULT_SINK@ | awk '{print $3}'"
                    ),
                    check_mute_string="[MUTED]",
                    emoji=True,
                    emoji_list=[" ", " ", " ", " "],
                    fmt="<span rise='-15pt'>  {}</span>",
                    get_volume_command=(
                        "wpctl get-volume @DEFAULT_SINK@"
                        " | awk '{print $2*100 \"%\"}'"
                    ),
                    mute_command="wpctl set-mute @DEFAULT_SINK@ toggle",
                    mute_foreground=Color.YELLOW,
                    update_interval=1,
                    volume_down_command="wpctl set-volume @DEFAULT_SINK@ 2%-",
                    volume_up_command="wpctl set-volume @DEFAULT_SINK@ 2%+",
                    width=widget_widths["vol_icon"],
                ),
                widget.Volume(
                    check_mute_command=(
                        "wpctl get-volume @DEFAULT_SINK@ | awk '{print $3}'"
                    ),
                    check_mute_string="[MUTED]",
                    get_volume_command=(
                        "wpctl get-volume @DEFAULT_SINK@"
                        " | awk '{print $2*100 \"%\"}'"
                    ),
                    max_chars=3,
                    mute_command="wpctl set-mute @DEFAULT_SINK@ toggle",
                    mute_foreground=Color.YELLOW,
                    mute_format="--%",
                    volume_down_command="wpctl set-volume @DEFAULT_SINK@ 2%-",
                    volume_up_command="wpctl set-volume @DEFAULT_SINK@ 2%+",
                    width=widget_widths["vol_perc"],
                ),
                audio_output_widget,
                widget.ThermalSensor(
                    format="  {temp:.0f}{unit}",
                    mouse_callbacks={
                        "Button3": lazy.group["0"].dropdown_toggle("btop"),
                    },
                    tag_sensor="Package id 0",
                    width=widget_widths["thermal"],
                ),
                widget.CPU(
                    format="  {load_percent:2.0f}%",
                    mouse_callbacks={
                        "Button3": lazy.group["0"].dropdown_toggle("btop"),
                    },
                    width=widget_widths["cpu"],
                ),
                widget.TextBox(
                    " ",
                    fontsize=round(font_main_size * 1.15),
                    # fmt="<span rise='-19pt'>{}</span>",
                    mouse_callbacks={
                        "Button3": lazy.group["0"].dropdown_toggle("btop"),
                    },
                    width=widget_widths["mem_icon"],
                ),
                widget.Memory(
                    format="{MemUsed:2.1f}{mm}",
                    mouse_callbacks={
                        "Button3": lazy.group["0"].dropdown_toggle("btop"),
                    },
                    measure_mem="G",
                    width=widget_widths["mem_g"],
                ),
                widget.Net(
                    format="{down:>4.0f}{down_suffix:>2}󰶡",
                    width=widget_widths["net_down"],
                ),
                widget.Net(
                    format="󰶣{up:<.0f}{up_suffix:<}",
                    width=widget_widths["net_up"],
                ),
                *display_widget,
                widget.QuickExit(
                    countdown_start=3,
                    countdown_format="{} ",
                    default_text=" ",
                    fmt="<span rise='-17pt'>{}</span>",
                    fontsize=round(font_main_size * 1.07),
                    width=widget_widths["quick_exit"],
                ),
            ],
            round(font_main_size * 1.57),  # bar height
            background=[Color.DARK_GRAY, Color.BLACK],
            border_width=2,
            border_color=[
                Color.PURE_BLACK,
                Color.PURE_BLACK,
                Color.BLACK,
                Color.PURE_BLACK,
            ],
        ),
        # wallpaper=str(Path("~/Pictures/background/Neon.png").expanduser()),
        wallpaper_mode="fill",
    )


def get_other_screen():
    return Screen(
        top=bar.Bar(
            [
                widget.GroupBox(
                    active=Color.PURPLE,
                    background=[Color.DARK_GRAY, Color.BLACK],
                    fontsize=font_other_size,
                    inactive=Color.MID_GRAY,
                    mouse_callbacks={"Button3": default_app()},
                    other_current_screen_border=Color.PURPLE,
                    other_screen_border=Color.MID_GRAY,
                    this_current_screen_border=Color.BLUE,
                    this_screen_border=Color.SOFT_BLUE,
                    urgent_border=Color.PINK,
                ),
                widget.WindowName(
                    background=[Color.BLACK, Color.DARK_BLUE_GRAY],
                    fontshadow=Color.BLACK,
                    fontsize=font_other_size,
                    foreground=Color.LIGHT_VIOLET,
                    mouse_callbacks={
                        "Button1": lazy.widget["notify"].display(),
                        "Button3": lazy.window.kill(),
                    },
                ),
                widget.StatusNotifier(),
                widget.QuickExit(
                    countdown_start=3,
                    countdown_format=" {} ",
                    default_text="  ",
                    fmt="<span rise='-17pt'>{}</span>",
                    fontsize=round(font_other_size * 1.07),
                    width=round(font_other_size * 2.14),
                ),
            ],
            round(font_main_size * 1.57),  # bar height
            background=[Color.DARK_GRAY, Color.BLACK],
            border_width=2,
            border_color=[
                Color.PURE_BLACK,
                Color.PURE_BLACK,
                Color.BLACK,
                Color.PURE_BLACK,
            ],
        ),
        wallpaper_mode="fill",
    )


def generate_screens(outputs) -> list[Screen]:
    screens = []
    widest_monitor = max(outputs, key=lambda x: x.rect.width)

    for i, output in enumerate(outputs):
        if output is widest_monitor:
            scr = get_main_screen(output.rect)
        else:
            scr = get_other_screen()

        screens.append(scr)
        port_to_screen[output.port] = i

    if not outputs:
        logger.warning("No outputs found")
    else:
        logger.warning(
            "outputs: %s",
            [(o.port, o.rect.x, o.rect.y) for o in outputs],
        )

    return screens
