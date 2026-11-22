import time

from libqtile import hook, qtile, widget
from libqtile.lazy import lazy

# from libqtile.log_utils import logger
from globals_config import (
    IS_WAYLAND,
    Color,
    display_modes,
    display_ports,
    display_rates,
    display_v_offsets,
    display_widths,
    port_to_screen,
    widget_widths,
)


def display_on(display_port: str):
    return display_port.casefold() in [
        qtile.screens[scr["index"]].info()["port"].casefold()
        for scr in qtile.get_screens()
    ]


@lazy.function
def toggle_other_displays(_qtile):
    second_display_on = bool(len(qtile.get_screens()) - 1)
    _qtile.to_screen(port_to_screen[display_ports[0]])

    if IS_WAYLAND:
        qtile.spawn(f"wlr-randr --output {display_ports[1]} --toggle")
        qtile.reload_config()

    else:
        cmd = ["xrandr"]
        cmd.append(
            f"--output {display_ports[0]}"
            f" --mode {display_modes[0]}"
            f" --rate {display_rates[0]} --primary"
        )
        for port in display_ports:
            if port != display_ports[0]:
                if second_display_on:
                    cmd.append(f"--output {display_ports[1]} --off")

                else:
                    cmd.append(
                        f"--output {display_ports[1]}"
                        f" --mode {display_modes[1]}"
                        f" --rate {display_rates[1]}"
                        " --pos 2560x0"
                    )

        qtile.spawn(" ".join(cmd))
        time.sleep(1)
        qtile.restart()


@lazy.function
def toggle_display(_qtile, display_port: str) -> None:
    if IS_WAYLAND:
        randr_cmd = ["wlr-randr"]
        pos_sep = ","

    else:
        randr_cmd = ["xrandr"]
        pos_sep = "x"

    h_offset = 0
    for i, port in enumerate(display_ports):
        dsp_on = display_on(port)

        if (dsp_on and port != display_port) or (
            not dsp_on and port == display_port
        ):
            v_offset = (
                display_v_offsets[i] if display_on(display_ports[0]) else 0
            )
            randr_cmd.append(f"--output {port}")
            if IS_WAYLAND:
                randr_cmd.append(
                    f"--mode {display_modes[i]}@{display_rates[i]}"
                )
            else:
                randr_cmd.append(f"--mode {display_modes[i]}")
                randr_cmd.append(f"--rate {display_rates[i]}")
                if port == "DP-1":
                    randr_cmd.append("--primary")
            randr_cmd.append(f"--pos {h_offset}{pos_sep}{v_offset}")
            h_offset += display_widths[i]

        else:
            # _qtile.to_screen(port_to_screen[display_ports[i - 1]])
            randr_cmd.append(f"--output {port} --off")

    randr_cmd_str = " ".join(randr_cmd)
    # logger.warning(f"{randr_cmd_str=}")
    qtile.spawn(randr_cmd_str)
    time.sleep(0.5)

    if IS_WAYLAND:
        qtile.reload_config()
    else:
        qtile.restart()


display_widget = []
for i, port in enumerate(display_ports):
    display_widget.append(
        widget.TextBox(
            text=" ",
            fmt="<span rise='-17pt'>{}</span>",
            foreground=Color.SLATE_BLUE,
            mouse_callbacks={
                "Button1": toggle_display(port),
                "Button3": lazy.group["0"].dropdown_toggle("key_bindings"),
            },
            width=widget_widths[f"disp{i + 1}"],
        )
    )


@hook.subscribe.startup
def update_displays():
    for i, port in enumerate(display_ports):
        display_widget[i].update("󰍹 " if display_on(port) else "󰶐 ")
