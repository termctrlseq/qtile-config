from datetime import datetime
from pathlib import Path

from libqtile.lazy import lazy
from libqtile.utils import send_notification


@lazy.function
def screenshot(qtile):
    try:
        from PIL import ImageGrab

        img = ImageGrab.grab()

        name = datetime.now().strftime("IMG_%Y%m%d_%H%M%S.jpg")
        pic_dir = Path("~/Pictures/Screenshots").expanduser()
        pic_dir.mkdir(parents=True, exist_ok=True)

        img.save(str(pic_dir / name))
        send_notification("screenshot:", f"{name}")

    except Exception as e:
        send_notification("screenshot:", f"{e}")
