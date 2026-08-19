"""Executes generated DSL Python source. Replaces program.py's inline
`exec(code_to_exec)` wrapped in a bare `except:` that also swallowed
KeyboardInterrupt — this catches Exception specifically instead."""
import time

import pyautogui


def play_actions(actions):
    """Play back a list of models.macro.Action directly in-process — used by the
    macro recorder's preview button (dsl/codegen.py's generated `play_actions` is
    a separate copy embedded as source text, since it must run standalone without
    importing this app)."""
    start = time.time()
    for action in actions:
        elapsed = time.time() - start
        pyautogui.PAUSE = max(0, action.t - elapsed)
        if action.type == "mouse_move":
            pyautogui.moveTo(action.x, action.y)
        elif action.type == "mouse_down":
            pyautogui.mouseDown(action.x, action.y, action.button)
        elif action.type == "mouse_up":
            pyautogui.mouseUp(action.x, action.y, action.button)
        elif action.type == "key_press":
            pyautogui.keyDown(action.key)
        elif action.type == "key_release":
            pyautogui.keyUp(action.key)
    pyautogui.PAUSE = 0.1


def run(source):
    """Exec generated source in a fresh namespace.

    Returns (stopped, console_lines, error):
      stopped     -- True if the script called sys.exit() (the user's configured
                      stop key was pressed), matching the old "Bot Stopped" message.
      console_lines -- whatever the script appended to its own `console_lines` list.
      error       -- the raised exception, or None on a clean finish.
    """
    namespace = {}
    try:
        exec(source, namespace)
    except SystemExit:
        return True, namespace.get("console_lines", []), None
    except Exception as e:  # noqa: BLE001 - intentionally broad, but not bare:
        return False, namespace.get("console_lines", []), e
    return False, namespace.get("console_lines", []), None
