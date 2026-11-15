from pathlib import Path

from libqtile import hook, qtile


def change_wallpaper(screen, wallpaper):
    screen.set_wallpaper(str(Path(wallpaper).expanduser()))


@hook.subscribe.startup
def run_on_startup():
    screen = qtile.screens[0]
    change_wallpaper(screen, "~/Pictures/background/Neon_Light_v2.png")

    qtile.call_later(
        5, change_wallpaper, screen, "~/Pictures/background/Neon_Dark_v2.png"
    )


@hook.subscribe.resume
def run_on_resume():
    change_wallpaper(
        qtile.screens[0], "~/Pictures/background/Neon_Green_v2.png"
    )


@hook.subscribe.user("run_on_unlock")  # type: ignore
def run_on_unlock():
    screen = qtile.screens[0]

    qtile.call_later(
        2, change_wallpaper, screen, "~/Pictures/background/Neon_Light_v2.png"
    )
    qtile.call_later(
        4, change_wallpaper, screen, "~/Pictures/background/Neon_Dark_v2.png"
    )
