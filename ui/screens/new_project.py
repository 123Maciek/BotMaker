"""New project creation screen — replaces addproject.py."""
import tkinter as tk
from tkinter import filedialog

from models.project import NameValidationError
from ui import theme
from ui.widgets import buttons


class NewProjectScreen(tk.Frame):
    def __init__(self, parent, ctx):
        super().__init__(parent, bg=theme.BG_APP)
        self.ctx = ctx
        self.chosen_dir = tk.StringVar(value="")

        buttons.heading_label(self, "New Project", font=theme.heading_font(26)).pack(pady=(40, 20))

        form = buttons.panel_frame(self)
        form.pack(padx=60, pady=10, fill="x")

        buttons.body_label(form, "Project name", bg=theme.BG_PANEL).pack(anchor="w", padx=20, pady=(20, 4))
        self.name_var = tk.StringVar()
        buttons.entry(form, textvariable=self.name_var, width=40).pack(anchor="w", padx=20)

        buttons.body_label(form, "Location", bg=theme.BG_PANEL).pack(anchor="w", padx=20, pady=(20, 4))
        loc_row = buttons.panel_frame(form, highlightthickness=0)
        loc_row.pack(anchor="w", padx=20, pady=(0, 20), fill="x")
        self.loc_label = buttons.muted_label(loc_row, "No folder chosen", bg=theme.BG_PANEL)
        self.loc_label.pack(side="left")
        buttons.ghost_button(loc_row, "Browse...", command=self._browse).pack(side="left", padx=10)

        self.error_label = buttons.body_label(self, "", fg=theme.ACCENT_RED)
        self.error_label.pack(pady=10)

        btn_row = buttons.app_frame(self)
        btn_row.pack(pady=20)
        buttons.primary_button(btn_row, "Create", command=self._submit).pack(side="left", padx=10)
        buttons.ghost_button(btn_row, "Cancel", command=self._cancel).pack(side="left", padx=10)

    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            self.chosen_dir.set(path)
            self.loc_label.config(text=path)

    def _submit(self):
        self.error_label.config(text="")
        name = self.name_var.get().strip()
        parent_dir = self.chosen_dir.get()
        if not parent_dir:
            self.error_label.config(text="Choose a folder first.")
            return
        try:
            project = self.ctx.project_repo.create(name, parent_dir)
        except NameValidationError as e:
            self.error_label.config(text=str(e))
            return
        except OSError as e:
            self.error_label.config(text=f"Couldn't create project folder: {e}")
            return

        from ui.screens.editor import EditorScreen
        self.ctx.set_current_project(project)
        self.ctx.navigator.go_to(EditorScreen)

    def _cancel(self):
        from ui.screens.project_list import ProjectListScreen
        self.ctx.navigator.go_to(ProjectListScreen)
