"""Position/pixel-color helper screen — replaces posHelper.py.

Captures the mouse position and pixel color under the cursor after a short
delay, then lets the user insert a matching DSL snippet. The old version wrote
directly to the project's code file and hard-exit()ed its own subprocess; here
it appends to the same code file (project.code_file) and navigates back to the
editor, which reloads fresh from disk — same on-disk effect, no subprocess.
"""
import tkinter as tk

import pyautogui
from PIL import ImageGrab

from ui import theme
from ui.widgets import buttons

CAPTURE_DELAY_MS = 5000


def _append_snippet_to_code_file(project, snippet):
    path = project.code_file
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = text.splitlines()
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines.append(snippet)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class PositionHelperScreen(tk.Frame):
    def __init__(self, parent, ctx, return_to):
        super().__init__(parent, bg=theme.BG_APP)
        self.ctx = ctx
        self.return_to = return_to
        self.project = ctx.current_project
        self.captured = None  # (x, y, r, g, b)
        self._pending_after = None

        buttons.heading_label(self, "Position && Color Helper", font=theme.heading_font(22)).pack(pady=(30, 10))
        buttons.muted_label(
            self,
            f"Click Check, then move the mouse to the target spot and wait {CAPTURE_DELAY_MS // 1000} seconds.",
        ).pack(pady=(0, 20))

        info = buttons.panel_frame(self)
        info.pack(pady=10)
        buttons.body_label(info, "X, Y:", bg=theme.BG_PANEL).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.pos_var = tk.StringVar()
        buttons.entry(info, textvariable=self.pos_var, width=24, state="readonly").grid(row=0, column=1, padx=10)
        buttons.body_label(info, "RGB:", bg=theme.BG_PANEL).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.color_var = tk.StringVar()
        buttons.entry(info, textvariable=self.color_var, width=24, state="readonly").grid(row=1, column=1, padx=10)

        self.check_btn = buttons.primary_button(self, "Check", command=self._begin_capture)
        self.check_btn.pack(pady=20)

        self.snippet_frame = buttons.app_frame(self)
        self.snippet_frame.pack(pady=10)
        self._snippet_buttons = []
        for label in ("MoveMouseTo", "WaitForPixel", "IfPixelColor", "MoveAndClickMouse (left)", "MoveAndClickMouse (right)"):
            b = buttons.ghost_button(self.snippet_frame, label, command=lambda l=label: self._insert(l))
            b.pack(pady=4, fill="x")
            b.config(state="disabled")
            self._snippet_buttons.append(b)

        buttons.ghost_button(self, "◀ Back to editor", command=self._back).pack(pady=20)

    def _begin_capture(self):
        self.check_btn.config(state="disabled", text="Move mouse now...")
        self._pending_after = self.after(CAPTURE_DELAY_MS, self._capture)

    def _capture(self):
        self.ctx.root.deiconify()
        self.ctx.root.lift()
        x, y = pyautogui.position()
        screen_width, screen_height = pyautogui.size()
        screen = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))
        r, g, b = screen.getpixel((x, y))
        self.captured = (x, y, r, g, b)

        self.pos_var.set(f"{x}, {y}")
        self.color_var.set(f"{r}, {g}, {b}")
        self.check_btn.config(state="normal", text="Check")
        for b_ in self._snippet_buttons:
            b_.config(state="normal")

    def _insert(self, label):
        if not self.captured:
            return
        x, y, r, g, b = self.captured
        if label == "MoveMouseTo":
            snippet = f"MoveMouseTo({x}, {y})"
        elif label == "WaitForPixel":
            snippet = f"WaitForPixel({x}, {y}, {r}, {g}, {b})"
        elif label == "IfPixelColor":
            snippet = f"IfPixelColor({x}, {y}, {r}, {g}, {b})"
        elif label == "MoveAndClickMouse (left)":
            snippet = f"MoveAndClickMouse({x}, {y}, left)"
        elif label == "MoveAndClickMouse (right)":
            snippet = f"MoveAndClickMouse({x}, {y}, right)"
        else:
            return
        _append_snippet_to_code_file(self.project, snippet)
        self.ctx.navigator.go_to(self.return_to)

    def on_leave(self):
        if self._pending_after:
            self.after_cancel(self._pending_after)

    def _back(self):
        self.ctx.navigator.go_to(self.return_to)
