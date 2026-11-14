from libqtile.config import DropDown, Group, Match, ScratchPad

SUPER = "mod4"

groups = [
    ScratchPad(
        name="0",
        single=True,
        dropdowns=[  # : {{{
            DropDown(
                name="kitty",
                cmd=(
                    "kitty "
                    "--title='scratchpad' "
                    "-o background='#0a0b11' "
                    "-o background_opacity=0.9 "
                    "-o font_size=24 "
                    "tmux new -As term"
                ),
                opacity=1.0,
                width=0.65,
                height=0.75,
                x=0.175,
                y=0.125,
                on_focus_lost_hide=False,
            ),
            DropDown(
                name="big_kitty",
                cmd=(
                    "kitty "
                    "--title='scratchpad' "
                    "-o background='#0a0b11' "
                    "-o background_opacity=0.9 "
                    "tmux new -As tmux"
                ),
                opacity=1.0,
                width=0.426,
                height=0.893,
                x=0.57,
                y=0.10,
                on_focus_lost_hide=False,
            ),
            DropDown(
                name="key_bindings",
                cmd=(
                    "kitty "
                    "--title='scratchpad' "
                    "-o background_opacity=0.9 "
                    "bash -c '"
                    'echo -e "$(qtile cmd-obj -f display_kb)" '
                    "| less'"
                ),
                opacity=1.0,
                width=1,
                height=1,
                x=0,
                y=0,
                on_focus_lost_hide=False,
            ),
            DropDown(
                name="btop",
                cmd=(
                    "kitty"
                    " --title='scratchpad'"
                    " -o background_opacity=0.95"
                    " -o background='#0a0b11'"
                    " btop"
                ),
                opacity=1.0,
                width=1,
                height=1,
                x=0,
                y=0,
                on_focus_lost_hide=False,
            ),
            DropDown(
                name="bluetooth",
                cmd=(
                    "kitty"
                    " --title='scratchpad'"
                    " -o background_opacity=0.95"
                    " -o background='#0a0b11'"
                    " bluetoothctl"
                ),
                opacity=1.0,
                width=0.5,
                height=1.0,
                x=0.5,
                y=0,
                on_focus_lost_hide=False,
            ),
            DropDown(
                name="music",
                cmd=(
                    "kitty "
                    "--title='scratchpad' "
                    "-o background_opacity=0.9 "
                    "-o background='#0a0b11' rmpc"
                ),
                opacity=1.0,
                width=0.696,
                height=0.83,
                x=0.15,
                y=0.08,
                on_focus_lost_hide=False,
            ),
        ],  # }}}
    ),
    Group(name="1", label="term"),
    Group(name="2", label="browser"),
    Group(name="3", label="media", matches=[Match(wm_class="easyeffects")]),
    Group(
        name="4",
        label="email",
        matches=[Match(wm_class="org.gnome.Evolution")],
    ),
    Group(name="5", label=""),
]
# vim:foldmethod=marker
