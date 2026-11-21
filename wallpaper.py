from asyncio import Handle
from collections import namedtuple
from pathlib import Path

from libqtile import hook, qtile

bg_exists: bool = True
handles: list[Handle] = []

backgrounds = Path().home() / "Pictures" / "background"
if bg_exists := backgrounds.exists():
    Background = namedtuple(
        "Background",
        ["dark", "light", "green", "red"],
    )
    background = Background(
        dark={
            "2560": backgrounds / "Neon_Dark_v2.png",
            "1680": backgrounds / "Neon_Dark_v2_1680.png",
        },
        light={
            "2560": backgrounds / "Neon_Light_v2.png",
            "1680": backgrounds / "Neon_Light_v2_1680.png",
        },
        green={
            "2560": backgrounds / "Neon_Green_v2.png",
            "1680": backgrounds / "Neon_Green_v2_1680.png",
        },
        red={
            "2560": backgrounds / "Neon_Red_v2.png",
            "1680": backgrounds / "Neon_Red_v2_1680.png",
        },
    )

    for bg in background:
        if bg_exists:
            for width, path in bg.items():
                if path.exists():
                    bg[width] = str(path)
                else:
                    bg_exists = False
                    break


def call_later_maybe(delay_pics: list[tuple[int, dict[str, str]]]) -> None:
    if not bg_exists:
        return

    for handle in handles:
        handle.cancel()

    for d_pic in delay_pics:
        for scr in qtile.get_screens():
            screen = qtile.screens[scr["index"]]
            bg = d_pic[1].get(str(scr["width"]), background.dark["2560"])

            if d_pic[0] == 0:
                screen.set_wallpaper(bg)
            else:
                handles.append(
                    qtile.call_later(d_pic[0], screen.set_wallpaper, bg)
                )


@hook.subscribe.startup
def wallpaper_on_startup() -> None:
    call_later_maybe([(0, background.light), (5, background.dark)])


@hook.subscribe.user("run_on_lock")  # type: ignore
def wallpaper_on_lock() -> None:
    call_later_maybe([(0, background.light), (2, background.green)])


@hook.subscribe.user("run_on_unlock")  # type: ignore
def wallpaper_on_unlock() -> None:
    call_later_maybe([(2, background.light), (4, background.dark)])
