"""Update progress screen — replaces download_repository.py's standalone
progress window. Runs update.updater.run_update in a background thread (the
clone is blocking I/O) and reports each stage; on failure it shows the error
and lets the user go back — the app is never left in a half-updated state."""
import tkinter as tk
from threading import Thread

from update import updater
from ui import theme
from ui.widgets import buttons
from ui.widgets.thread_bridge import ThreadBridge


class UpdateProgressScreen(tk.Frame, ThreadBridge):
    def __init__(self, parent, ctx, return_to):
        super().__init__(parent, bg=theme.BG_APP)
        self.ctx = ctx
        self.return_to = return_to
        self.init_thread_bridge()

        buttons.heading_label(self, "Updating BotMaker", font=theme.heading_font(22)).pack(pady=(60, 20))
        self.status_label = buttons.body_label(self, "Starting...")
        self.status_label.pack(pady=10)

        self.back_btn = buttons.ghost_button(self, "◀ Back", command=self._back)
        self.back_btn.pack(pady=30)
        self.back_btn.config(state="disabled")

        Thread(target=self._run, daemon=True).start()

    def _report(self, message):
        self.post_to_ui(lambda: self.status_label.config(text=message, fg=theme.FG_PRIMARY))

    def _run(self):
        try:
            updater.run_update(progress_callback=self._report)
            # run_update does not return on success (it relaunches the process)
        except updater.UpdateError as e:
            self.post_to_ui(self._fail, str(e))

    def _fail(self, message):
        self.status_label.config(text=f"Update failed: {message}", fg=theme.ACCENT_RED)
        self.back_btn.config(state="normal")

    def on_leave(self):
        self.stop_thread_bridge()

    def _back(self):
        self.ctx.navigator.go_to(self.return_to)
