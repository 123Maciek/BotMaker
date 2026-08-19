"""Macro recorder screen — replaces macros.py.

Full recorded actions always live in self.actions; the "hide mouse movement"
checkbox only changes what's shown in the read-only preview. The old macros.py
mutated the underlying action list to hide/restore movement via fragile
string-equality position matching — here the raw data is never touched by the
display toggle, so there's nothing to restore incorrectly.
"""
import time
import tkinter as tk
from threading import Thread
from tkinter import messagebox

from execution import runner
from models.macro import MOUSE_MOVE, Macro
from models.project import NameValidationError, validate_name
from recorder.hooks import MacroRecorder
from ui import theme
from ui.widgets import buttons
from ui.widgets.thread_bridge import ThreadBridge


def _display_line(action):
    parts = [action.type]
    if action.x is not None:
        parts.append(f"x={action.x}")
    if action.y is not None:
        parts.append(f"y={action.y}")
    if action.button is not None:
        parts.append(f"button={action.button}")
    if action.key is not None:
        parts.append(f"key={action.key}")
    parts.append(f"t={action.t:.3f}")
    return "  ".join(parts)


def _filtered_for_display(actions, hide_movement):
    if not hide_movement:
        return actions
    result = []
    previous_type = None
    for a in actions:
        if a.type != MOUSE_MOVE or previous_type != MOUSE_MOVE:
            result.append(a)
        previous_type = a.type
    return result


class MacroRecorderScreen(tk.Frame, ThreadBridge):
    def __init__(self, parent, ctx, return_to):
        super().__init__(parent, bg=theme.BG_APP)
        self.ctx = ctx
        self.return_to = return_to
        self.project = ctx.current_project
        self.actions = []
        self.hide_movement = tk.IntVar(value=0)
        self.init_thread_bridge()

        self.recorder = MacroRecorder(on_action=self._on_action, on_toggle=self._on_toggle)

        buttons.heading_label(self, "Record Macro", font=theme.heading_font(22)).pack(pady=(20, 10))

        name_row = buttons.app_frame(self)
        name_row.pack(pady=6)
        buttons.body_label(name_row, "Macro name:").pack(side="left")
        self.name_var = tk.StringVar()
        buttons.entry(name_row, textvariable=self.name_var, width=30).pack(side="left", padx=8)

        buttons.muted_label(self, "Press F8 to start/stop recording anywhere on screen.").pack(pady=(0, 6))

        chk = tk.Checkbutton(
            self, text="Hide mouse movement (display only)", variable=self.hide_movement,
            command=self._refresh_preview, bg=theme.BG_APP, fg=theme.FG_PRIMARY,
            activebackground=theme.BG_APP, activeforeground=theme.FG_PRIMARY,
            selectcolor=theme.BG_INPUT, font=theme.body_font(),
        )
        chk.pack(pady=6)

        preview_frame = buttons.panel_frame(self)
        preview_frame.pack(fill="both", expand=True, padx=40, pady=10)
        self.preview = tk.Text(
            preview_frame, height=18, bg=theme.BG_INPUT, fg=theme.FG_PRIMARY,
            insertbackground=theme.FG_PRIMARY, border=0, font=theme.mono_font(10),
            state="disabled",
        )
        self.preview.pack(fill="both", expand=True, padx=8, pady=8)

        btn_row = buttons.app_frame(self)
        btn_row.pack(pady=16)
        self.record_btn = buttons.primary_button(btn_row, "START - F8", command=self.recorder.toggle)
        self.record_btn.pack(side="left", padx=8)
        buttons.info_button(btn_row, "Preview (3s delay)", command=self._preview_play).pack(side="left", padx=8)
        buttons.primary_button(btn_row, "Save", command=self._save).pack(side="left", padx=8)
        buttons.ghost_button(btn_row, "Cancel", command=self._cancel).pack(side="left", padx=8)

        self.recorder.start_listening()

    def on_leave(self):
        self.recorder.stop_listening()
        self.stop_thread_bridge()

    # --- recording callbacks (called from the pynput listener thread) ---------
    def _on_action(self, action):
        self.actions.append(action)
        self.post_to_ui(self._refresh_preview)

    def _on_toggle(self, is_recording):
        self.post_to_ui(self._apply_toggle_ui, is_recording)

    def _apply_toggle_ui(self, is_recording):
        if is_recording:
            self.actions = []
            self.record_btn.config(text="STOP - F8", bg=theme.ACCENT_RED, activebackground=theme.ACCENT_RED_HOVER)
        else:
            self.record_btn.config(text="START - F8", bg=theme.ACCENT_GREEN, activebackground=theme.ACCENT_GREEN_HOVER)
            self._refresh_preview()

    # --- preview -----------------------------------------------------
    def _refresh_preview(self):
        shown = _filtered_for_display(self.actions, bool(self.hide_movement.get()))
        text = "\n".join(_display_line(a) for a in shown)
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("end", text)
        self.preview.configure(state="disabled")

    def _preview_play(self):
        if not self.actions:
            messagebox.showerror("Recording error", "There is nothing recorded to preview.")
            return
        actions = list(self.actions)

        def run_preview():
            time.sleep(3)
            runner.play_actions(actions)

        Thread(target=run_preview, daemon=True).start()

    # --- save/cancel -----------------------------------------------------
    def _save(self):
        if not self.actions:
            messagebox.showerror("Recording error", "You cannot save an empty recording.")
            return
        name = self.name_var.get()
        try:
            validate_name(name)
        except NameValidationError as e:
            messagebox.showerror("Macro Name Error", str(e))
            return

        from models.macro import MacroRepo
        macro_repo = MacroRepo(self.project)
        if name in macro_repo.list_names():
            result = messagebox.askquestion("Confirmation", f'A macro named "{name}" already exists. Replace it?')
            if result != "yes":
                return

        macro_repo.save(Macro(name=name, actions=self.actions))
        self.recorder.stop_listening()
        self.ctx.navigator.go_to(self.return_to)

    def _cancel(self):
        self.recorder.stop_listening()
        self.ctx.navigator.go_to(self.return_to)
