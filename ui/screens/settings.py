"""Per-project settings + update check screen — replaces settings.py."""
import os
import tkinter as tk
from tkinter import messagebox

import pyperclip

from models.settings import (
    CODE_DISPLAY_HIDDEN, CODE_DISPLAY_MODES, CODE_DISPLAY_SHOWN, CODE_DISPLAY_SHOWN_PACKED,
    CONSOLE_HIDDEN, CONSOLE_MODES, CONSOLE_SHOWN,
)
from update import version as version_mod
from ui import theme
from ui.widgets import buttons

_CODE_LABELS = {
    CODE_DISPLAY_HIDDEN: "Don't show python code",
    CODE_DISPLAY_SHOWN: "Show python code (for personal use on this computer)",
    CODE_DISPLAY_SHOWN_PACKED: "Show python code with macros packed (for sharing / compiling)",
}
_CONSOLE_LABELS = {
    CONSOLE_HIDDEN: "Don't show console",
    CONSOLE_SHOWN: "Show console",
}


class SettingsScreen(tk.Frame):
    def __init__(self, parent, ctx, return_to):
        super().__init__(parent, bg=theme.BG_APP)
        self.ctx = ctx
        self.return_to = return_to
        self.project = ctx.current_project

        buttons.heading_label(self, "Settings", font=theme.heading_font(22)).pack(pady=(30, 20))

        folder_panel = buttons.panel_frame(self)
        folder_panel.pack(padx=60, pady=10, fill="x")
        buttons.body_label(folder_panel, "Project folder", bg=theme.BG_PANEL).pack(anchor="w", padx=20, pady=(16, 4))
        buttons.muted_label(folder_panel, str(self.project.root), bg=theme.BG_PANEL, wraplength=700).pack(anchor="w", padx=20)
        row = buttons.app_frame(folder_panel, bg=theme.BG_PANEL)
        row.pack(anchor="w", padx=20, pady=(8, 16))
        buttons.ghost_button(row, "Copy Path", command=self._copy_path).pack(side="left", padx=(0, 8))
        buttons.ghost_button(row, "Open Folder", command=self._open_folder).pack(side="left")

        code_panel = buttons.panel_frame(self)
        code_panel.pack(padx=60, pady=10, fill="x")
        buttons.body_label(code_panel, "Code display", bg=theme.BG_PANEL).pack(anchor="w", padx=20, pady=(16, 4))
        self.code_var = tk.StringVar(value=self.project.settings.code_display_mode)
        for mode in CODE_DISPLAY_MODES:
            tk.Radiobutton(
                code_panel, text=_CODE_LABELS[mode], variable=self.code_var, value=mode,
                command=self._save, bg=theme.BG_PANEL, fg=theme.FG_PRIMARY,
                selectcolor=theme.BG_INPUT, activebackground=theme.BG_PANEL,
                activeforeground=theme.FG_PRIMARY, font=theme.body_font(),
            ).pack(anchor="w", padx=20)
        tk.Frame(code_panel, bg=theme.BG_PANEL, height=10).pack()

        console_panel = buttons.panel_frame(self)
        console_panel.pack(padx=60, pady=10, fill="x")
        buttons.body_label(console_panel, "Console", bg=theme.BG_PANEL).pack(anchor="w", padx=20, pady=(16, 4))
        self.console_var = tk.StringVar(value=self.project.settings.console_mode)
        for mode in CONSOLE_MODES:
            tk.Radiobutton(
                console_panel, text=_CONSOLE_LABELS[mode], variable=self.console_var, value=mode,
                command=self._save, bg=theme.BG_PANEL, fg=theme.FG_PRIMARY,
                selectcolor=theme.BG_INPUT, activebackground=theme.BG_PANEL,
                activeforeground=theme.FG_PRIMARY, font=theme.body_font(),
            ).pack(anchor="w", padx=20)
        tk.Frame(console_panel, bg=theme.BG_PANEL, height=10).pack()

        version_panel = buttons.panel_frame(self)
        version_panel.pack(padx=60, pady=10, fill="x")
        buttons.body_label(version_panel, "Version", bg=theme.BG_PANEL).pack(anchor="w", padx=20, pady=(16, 4))
        self.version_label = buttons.muted_label(version_panel, "Checking for updates...", bg=theme.BG_PANEL)
        self.version_label.pack(anchor="w", padx=20, pady=(0, 10))
        self.update_btn = buttons.info_button(version_panel, "Update", command=self._start_update)
        self.update_btn.pack(anchor="w", padx=20, pady=(0, 16))
        self.update_btn.pack_forget()

        buttons.ghost_button(self, "◀ Back", command=self._back).pack(pady=20)

        self.after(50, self._check_update)

    def _save(self):
        self.project.settings.code_display_mode = self.code_var.get()
        self.project.settings.console_mode = self.console_var.get()
        self.project.save()

    def _copy_path(self):
        pyperclip.copy(str(self.project.root))

    def _open_folder(self):
        os.startfile(str(self.project.root))

    def _check_update(self):
        available, local, remote = version_mod.check_for_update()
        if remote is None:
            self.version_label.config(text=f"Current version: v{local or '?'} (couldn't reach update server)")
        elif available:
            self.version_label.config(text=f"Current version: v{local}  —  new version available: v{remote}")
            self.update_btn.pack(anchor="w", padx=20, pady=(0, 16))
        else:
            self.version_label.config(text=f"Current version: v{local}  —  up to date")

    def _start_update(self):
        result = messagebox.askyesno(
            "Update BotMaker",
            "This will download the latest version and restart the app. Continue?",
        )
        if not result:
            return
        from ui.screens.update_progress import UpdateProgressScreen
        self.ctx.navigator.go_to(UpdateProgressScreen, return_to=self.return_to)

    def _back(self):
        self.ctx.navigator.go_to(self.return_to)
