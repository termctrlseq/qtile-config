from enum import Enum
from subprocess import CalledProcessError, run

from libqtile import qtile, widget
from libqtile.lazy import lazy
from libqtile.log_utils import logger
from libqtile.utils import send_notification

from globals_config import Color, font_main_size, widget_widths


class Output(Enum):
    icon: str

    def __new__(cls, description: str, icon: str) -> "Output":  # noqa: PYI034
        obj = object.__new__(cls)
        obj._value_ = description
        obj.icon = icon
        return obj

    BUILTIN = "IEC958", "󱀞"
    EASY_EFFECTS = "Easy Effects Sink", ""
    HDMI = "HDMI", "󰽟"
    HEADPHONES = "Built-in Audio Analog Stereo", ""
    SOUNDCORE = "soundcore", "󱡏"
    SRSBTX = "SRS-BTX300", "󰦢"
    UNKNOWN = "__UNKNOWN__", " "

    @classmethod
    def from_wpctl_inspect(cls, stdout: str) -> "Output":
        for line in stdout.splitlines():
            if "node.description" in line:
                for output in cls:
                    if output.value in line:
                        return output

        return Output.UNKNOWN


_prev_sink: Output = Output.UNKNOWN


def inspect_audio() -> str:
    """Return current audio output string"""
    global _prev_sink
    audio_sink: Output = Output.UNKNOWN
    cmd = ["wpctl", "inspect", "@DEFAULT_AUDIO_SINK@"]

    try:
        result = run(
            cmd,
            capture_output=True,
            encoding="utf-8",
            check=True,
        )

    except CalledProcessError as e:
        # send_notification("Audio Sink:", "Called Process Error")
        logger.error(f"{' '.join(cmd)}: {e}")
        return audio_sink.icon

    if result.returncode == 0:
        audio_sink = Output.from_wpctl_inspect(result.stdout)

    if audio_sink is not _prev_sink:
        _prev_sink = audio_sink
        if audio_sink is not Output.SOUNDCORE:
            qtile.spawn("playerctl pause")
        # if audio_sink == Output.BUILTIN:
        #     next_audio_sink()

    return audio_sink.icon


def next_audio_sink(reverse: bool = False) -> None:
    """Switch to next/previous audio sink."""
    cmd = ["wpctl", "list", "audio", "sinks"]
    try:
        result = run(
            cmd,
            capture_output=True,
            check=True,
            encoding="utf-8",
        )

    except CalledProcessError as e:
        send_notification(
            "Audio Sink Error:", f"{' '.join(cmd)} exited with {e.returncode}"
        )
        logger.error(f"{' '.join(cmd)}: {e}")
        return

    sinks: list = []
    for sink in result.stdout.splitlines():
        if "*" not in sink and "easyeffects" in sink:
            continue
        sinks.append(sink.split())

    if len(sinks) < 2:
        logger.warning(f"No other sinks available: {sinks}")
        return

    next_sink_id: str | None = None
    for i, sink in enumerate(sinks):
        if sink[-1] == "*":
            next_sink_id = (
                sinks[(i + 1) % len(sinks)][0] if reverse else sinks[i - 1][0]
            )
            break

    if next_sink_id is None:
        logger.warning(f"Failed to get next sink id: {sinks}")
        return

    cmd = ["wpctl", "set-default", next_sink_id]
    try:
        result = run(
            cmd,
            capture_output=True,
            check=True,
            encoding="utf-8",
        )

    except CalledProcessError as e:
        send_notification("Audio Sink:", "Called Process Error")
        logger.error(f"{' '.join(cmd)}: {e}")
        return
    # logger.error(f"{' '.join(cmd)}: {result.stdout}")


@lazy.function
def next_sink(_, reverse: bool = False) -> None:
    next_audio_sink(reverse)


audio_output_widget = widget.GenPollText(
    fontsize=round(font_main_size * 1.15),
    foreground=Color.MUTED_BLUE,
    fmt="<span rise='6pt'>{}</span>",
    mouse_callbacks={
        "Button1": next_sink(),
        "Button8": next_sink(reverse=True),
        "Button9": next_sink(),
    },
    func=inspect_audio,
    update_interval=3,
    width=widget_widths["audio_out"],
)
