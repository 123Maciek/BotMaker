"""Global mouse/keyboard listener lifecycle for the macro recorder screen.

Replaces macros.py, which was its own always-running subprocess with global
pynput hooks installed at import time. Here the hooks are started/stopped
explicitly by the recorder screen (on_enter/on_leave), so they never run in
the background once the user has navigated away.
"""
import time

from pynput import keyboard, mouse

from models.macro import KEY_PRESS, KEY_RELEASE, MOUSE_DOWN, MOUSE_MOVE, MOUSE_UP, Action

TOGGLE_KEY_NAME = "f8"


def normalize_key(key):
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)
    key_char = key_char.lower()
    if key_char.startswith("key."):
        key_char = key_char[len("key."):]
    if key_char == "cmd":
        key_char = "win"
    if key_char == "alt_l":
        key_char = "alt"
    return key_char


def normalize_button(button):
    name = str(button)
    if name.startswith("Button."):
        name = name[len("Button."):]
    if name.startswith("x") and len(name) > 1:
        name = name[1:]
    return name


class MacroRecorder:
    def __init__(self, on_action=None, on_toggle=None):
        self.on_action = on_action  # callback(Action)
        self.on_toggle = on_toggle  # callback(is_recording: bool)
        self._mouse_listener = None
        self._keyboard_listener = None
        self.is_recording = False
        self._start_time = 0.0

    def start_listening(self):
        if self._mouse_listener is not None:
            return
        self._mouse_listener = mouse.Listener(on_move=self._on_move, on_click=self._on_click)
        self._keyboard_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop_listening(self):
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        self.is_recording = False

    def toggle(self):
        if self.is_recording:
            self._end_recording()
        else:
            self._begin_recording()

    def _elapsed(self):
        return time.time() - self._start_time

    def _begin_recording(self):
        self.is_recording = True
        self._start_time = time.time()
        if self.on_toggle:
            self.on_toggle(True)

    def _end_recording(self):
        self.is_recording = False
        if self.on_toggle:
            self.on_toggle(False)

    def _emit(self, action):
        if self.on_action:
            self.on_action(action)

    def _on_move(self, x, y):
        if not self.is_recording:
            return
        self._emit(Action(type=MOUSE_MOVE, t=self._elapsed(), x=x, y=y))

    def _on_click(self, x, y, button, pressed):
        if not self.is_recording:
            return
        kind = MOUSE_DOWN if pressed else MOUSE_UP
        self._emit(Action(type=kind, t=self._elapsed(), x=x, y=y, button=normalize_button(button)))

    def _on_press(self, key):
        if not self.is_recording:
            return
        key_char = normalize_key(key)
        if key_char == TOGGLE_KEY_NAME:
            return
        self._emit(Action(type=KEY_PRESS, t=self._elapsed(), key=key_char))

    def _on_release(self, key):
        key_char = normalize_key(key)
        if key_char == TOGGLE_KEY_NAME:
            self.toggle()
            return
        if not self.is_recording:
            return
        self._emit(Action(type=KEY_RELEASE, t=self._elapsed(), key=key_char))
