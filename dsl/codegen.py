"""Validated command list -> standalone, runnable Python source.

Pure function, no Tk import — the same generated source is used both for live
"Start" playback (execution/runner.py execs it) and for export (execution/exporter.py
writes it out and opens it in Notepad), so there's exactly one code path instead of
the old exec-then-regex-strip-for-export split.
"""

_PREAMBLE = '''\
import pyautogui
import time
import keyboard
import sys
import os
import json
from PIL import ImageGrab

console_lines = []
program_start_time = time.time()
end_loop = False


def format_time(seconds):
    minutes = int(seconds // 60)
    whole_seconds = int(seconds % 60)
    fractional_seconds = seconds - (minutes * 60 + whole_seconds)
    fractional_str = f"{fractional_seconds:.4f}".split('.')[1]
    return f"{minutes:02}:{whole_seconds:02}:{fractional_str}"


def play_actions(actions):
    start = time.time()
    for action in actions:
        elapsed_time = time.time() - start
        delay = action["t"] - elapsed_time
        pyautogui.PAUSE = max(0, delay)
        action_type = action["type"]
        if action_type == "mouse_move":
            pyautogui.moveTo(action["x"], action["y"])
        elif action_type == "mouse_down":
            pyautogui.mouseDown(action["x"], action["y"], action["button"])
        elif action_type == "mouse_up":
            pyautogui.mouseUp(action["x"], action["y"], action["button"])
        elif action_type == "key_press":
            pyautogui.keyDown(action["key"])
        elif action_type == "key_release":
            pyautogui.keyUp(action["key"])
    pyautogui.PAUSE = 0.1

'''


def _add_tabs(n):
    return "\t" * n


def _iteration_var(tabs):
    return "i" * (tabs + 1)


def _action_literal(action):
    d = {"type": action.type, "t": action.t}
    if action.x is not None:
        d["x"] = action.x
    if action.y is not None:
        d["y"] = action.y
    if action.button is not None:
        d["button"] = action.button
    if action.key is not None:
        d["key"] = action.key
    return d


def generate(commands, *, stop_key, start_delay=1.0, macros_dir=None, pack_macros=False, macro_provider=None):
    """Render validated ParsedCommand objects (from dsl.parser.parse) into Python source.

    macros_dir: pathlib.Path to the project's Macros folder, used to build the
      load path for non-packed Macro(name) commands.
    pack_macros: if True, Macro(name) commands are resolved via macro_provider(name)
      at generation time and their actions inlined as a Python literal instead of
      read from disk at runtime — used for the "shown with macros packed" display
      mode so the exported script is self-contained. macro_provider(name) must
      return a models.macro.Macro.
    """
    lines = [_PREAMBLE, f"time.sleep({start_delay})\n"]
    tabs = 0
    stack = []  # 'loop' | 'if', mirrors the parser's own balance stack

    def emit(code):
        lines.append(_add_tabs(tabs) + code)

    def emit_stop_check():
        emit(f"if keyboard.is_pressed({stop_key!r}):\n")
        lines.append(_add_tabs(tabs + 1) + "sys.exit()\n")

    show_duration = False

    for cmd in commands:
        name, a = cmd.name, cmd.args

        if name == "ClickOnKeyboard":
            emit(f"keyboard.press_and_release({a['key']!r})\n")
        elif name == "KeyDown":
            emit(f"keyboard.press({a['key']!r})\n")
        elif name == "KeyUp":
            emit(f"keyboard.release({a['key']!r})\n")
        elif name == "WaitSeconds":
            emit(f"time.sleep({a['seconds']})\n")
        elif name == "WaitForKeyboard":
            key = a["key"]
            emit("while end_loop == False:\n")
            lines.append(_add_tabs(tabs + 1) + f"if keyboard.is_pressed({key!r}):\n")
            lines.append(_add_tabs(tabs + 2) + "end_loop = True\n")
            lines.append(_add_tabs(tabs + 1) + f"while keyboard.is_pressed({key!r}):\n")
            lines.append(_add_tabs(tabs + 2) + "pass\n")
            lines.append(_add_tabs(tabs + 1) + f"if keyboard.is_pressed({stop_key!r}):\n")
            lines.append(_add_tabs(tabs + 2) + "sys.exit()\n")
            emit("end_loop = False\n")
        elif name == "MoveMouseTo":
            emit(f"pyautogui.moveTo({a['x']}, {a['y']})\n")
        elif name == "MouseUp":
            emit(f"pyautogui.mouseUp(button={a['button']!r})\n")
        elif name == "MouseDown":
            emit(f"pyautogui.mouseDown(button={a['button']!r})\n")
        elif name == "Loop":
            emit(f"for {_iteration_var(tabs)} in range({a['count']}):\n")
            tabs += 1
            stack.append("loop")
        elif name == "EndLoop":
            tabs -= 1
            stack.pop()
        elif name == "WaitForPixel":
            emit("screen_width, screen_height = pyautogui.size()\n")
            emit("while True:\n")
            lines.append(_add_tabs(tabs + 1) + "screen = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))\n")
            lines.append(_add_tabs(tabs + 1) + f"pix = screen.getpixel(({a['x']}, {a['y']}))\n")
            lines.append(_add_tabs(tabs + 1) + f"tar = ({a['r']}, {a['g']}, {a['b']})\n")
            lines.append(_add_tabs(tabs + 1) + "if pix == tar:\n")
            lines.append(_add_tabs(tabs + 2) + "break\n")
        elif name == "InfLoop":
            emit("while True:\n")
            tabs += 1
            stack.append("loop")
        elif name == "ExitLoop":
            emit("break\n")
        elif name == "IfPixelColor":
            emit("screen_width, screen_height = pyautogui.size()\n")
            emit("screen = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))\n")
            emit(f"pix = screen.getpixel(({a['x']}, {a['y']}))\n")
            emit(f"tar = ({a['r']}, {a['g']}, {a['b']})\n")
            emit("if pix == tar:\n")
            tabs += 1
            stack.append("if")
        elif name == "Else":
            lines.append(_add_tabs(tabs - 1) + "else:\n")
        elif name == "EndIf":
            tabs -= 1
            stack.pop()
        elif name == "Macro":
            macro_name = a["name"]
            if pack_macros and macro_provider is not None:
                macro = macro_provider(macro_name)
                actions_literal = repr([_action_literal(act) for act in (macro.actions if macro else [])])
                emit(f"play_actions({actions_literal})\n")
            else:
                macro_path = str((macros_dir / f"{macro_name}.json")) if macros_dir else f"{macro_name}.json"
                emit(f"with open({macro_path!r}, 'r', encoding='utf-8') as f:\n")
                lines.append(_add_tabs(tabs + 1) + "play_actions(json.load(f))\n")
        elif name == "WriteText":
            emit(f"pyautogui.write({a['text']!r})\n")
        elif name == "ClickMouse":
            emit(f"pyautogui.mouseDown(button={a['button']!r})\n")
            emit(f"pyautogui.mouseUp(button={a['button']!r})\n")
        elif name == "MoveAndClickMouse":
            emit(f"pyautogui.moveTo({a['x']}, {a['y']})\n")
            emit(f"pyautogui.mouseDown(button={a['button']!r})\n")
            emit(f"pyautogui.mouseUp(button={a['button']!r})\n")
        elif name == "ShowProgramDuration":
            show_duration = True
            continue  # no inline code — duration is appended once, at the very end
        elif name == "ShowText":
            emit(f"arg = {a['text']!r}\n")
            emit('console_lines.append(f"{format_time(time.time()-program_start_time)} - {arg}")\n')
        else:
            raise AssertionError(f"unhandled command in codegen: {name}")

        emit_stop_check()

    if show_duration:
        lines.append(
            'console_lines.append(f"{format_time(time.time()-program_start_time)} '
            '- Program duration: {time.time()-program_start_time} seconds.")\n'
        )

    return "".join(lines)
