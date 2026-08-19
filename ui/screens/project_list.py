"""Project list screen — replaces main.py."""
import tkinter as tk
from tkinter import messagebox

from models.project import Project
from ui import theme
from ui.widgets import buttons
from ui.widgets.scrollable_frame import ScrollableFrame


class ProjectListScreen(tk.Frame):
    def __init__(self, parent, ctx):
        super().__init__(parent, bg=theme.BG_APP)
        self.ctx = ctx
        self.selected: Project = None
        self._row_widgets = {}

        buttons.heading_label(self, "Bot Maker").pack(pady=(30, 10))

        self.scroll = ScrollableFrame(self, bg=theme.BG_APP)
        self.scroll.pack(fill="both", expand=True, padx=60, pady=10)

        btn_row = buttons.app_frame(self)
        btn_row.pack(pady=20)
        buttons.primary_button(btn_row, "Create New Project", command=self._create_project).pack(side="left", padx=10)
        buttons.danger_button(btn_row, "Remove Project", command=self._delete_project).pack(side="left", padx=10)
        buttons.info_button(btn_row, "Open Project", command=self._open_project).pack(side="left", padx=10)

        self.refresh()

    def refresh(self):
        for child in self.scroll.body.winfo_children():
            child.destroy()
        self._row_widgets.clear()
        self.selected = None

        projects = self.ctx.project_repo.list_projects()
        for project in projects:
            row = tk.Button(
                self.scroll.body,
                text=project.name,
                anchor="w",
                fg=theme.FG_PRIMARY,
                bg=theme.BG_PANEL_ALT,
                activebackground=theme.SELECTION,
                activeforeground=theme.FG_PRIMARY,
                bd=0,
                relief=tk.FLAT,
                highlightthickness=0,
                font=theme.body_font(12),
                padx=20,
                pady=14,
                cursor="hand2",
                command=lambda p=project: self._select(p),
            )
            row.pack(fill="x", pady=2)
            self._row_widgets[project.name] = row

        if projects:
            self._select(projects[0])

    def _select(self, project):
        self.selected = project
        for name, widget in self._row_widgets.items():
            widget.config(bg=theme.SELECTION if name == project.name else theme.BG_PANEL_ALT)

    def _create_project(self):
        from ui.screens.new_project import NewProjectScreen
        self.ctx.navigator.go_to(NewProjectScreen)

    def _delete_project(self):
        if not self.selected:
            return
        result = messagebox.askquestion("Confirmation", f'Are you sure you want to delete "{self.selected.name}"?')
        if result == "yes":
            self.ctx.project_repo.delete(self.selected)
            self.refresh()

    def _open_project(self):
        if not self.selected:
            return
        from ui.screens.editor import EditorScreen
        self.ctx.set_current_project(self.selected)
        self.ctx.navigator.go_to(EditorScreen)
