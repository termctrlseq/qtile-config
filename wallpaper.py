from asyncio import Handle
from pathlib import Path

from libqtile import hook, qtile

handles: list[Handle] = []

backgrounds = Path().home() / "Pictures" / "background"
dark = (
    str(backgrounds / "Neon_Dark_v2.png"),
    str(backgrounds / "Neon_Dark_v2_1680.png"),
)
light = (
    str(backgrounds / "Neon_Light_v2.png"),
    str(backgrounds / "Neon_Light_v2_1680.png"),
)
green = (
    str(backgrounds / "Neon_Green_v2.png"),
    str(backgrounds / "Neon_Green_v2_1680.png"),
)
red = (
    str(backgrounds / "Neon_Red_v2.png"),
    str(backgrounds / "Neon_Red_v2_1680.png"),
)


def call_later_maybe(delay_pic: list[tuple[int, tuple[str, str]]]) -> None:
    for handle in handles:
        handle.cancel()

    for tp in delay_pic:
        for scr in range(len(qtile.get_screens())):
            screen = qtile.screens[scr]
            bg = tp[1][scr]

            if tp[0] == 0:
                screen.set_wallpaper(bg)
            else:
                handles.append(
                    qtile.call_later(tp[0], screen.set_wallpaper, bg)
                )


@hook.subscribe.startup
def wallpaper_on_startup():
    call_later_maybe([(0, light), (5, dark)])


@hook.subscribe.user("run_on_lock")  # type: ignore
def wallpaper_on_lock():
    call_later_maybe([(0, light), (2, green)])


@hook.subscribe.user("run_on_unlock")  # type: ignore
def wallpaper_on_unlock():
    call_later_maybe([(2, light), (4, dark)])
