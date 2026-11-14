from libqtile.lazy import lazy

from globals_config import get_pos, restore_pos, save_pos


@lazy.function
def toggle_fullscreen(qtile):
    """
    Save/restore floating window position
    when enabling/disabling fullscreen.
    """
    cur_win = qtile.current_window
    if not cur_win:
        return
    cur_win_info = cur_win.info().copy()
    wm_class = cur_win_info["wm_class"][0]
    # fullscreen window is also floating, so if current window
    # is floating but not fullscreen, save position and size
    if not cur_win_info["fullscreen"] and cur_win_info["floating"]:
        save_pos(cur_win)
        cur_win.enable_fullscreen()
    # restore if fullscreen window has a saved state
    elif cur_win_info["fullscreen"] and (saved_state := get_pos(wm_class)):
        cur_win.disable_fullscreen()
        cur_win.enable_floating()
        # restore position and size
        cur_win.set_position_floating(
            saved_state["x"],
            saved_state["y"],
        )
        cur_win.set_size_floating(
            saved_state["width"],
            saved_state["height"],
        )
    else:
        cur_win.toggle_fullscreen()


@lazy.function
def toggle_floating(qtile):
    """Restore floating window position and size."""
    cur_win = qtile.current_window
    if not cur_win:
        return
    if cur_win.info()["floating"]:
        save_pos(cur_win)
        cur_win.toggle_floating()
    else:
        cur_win.toggle_floating()
        qtile.call_later(0.1, restore_pos, cur_win)
