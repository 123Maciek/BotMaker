"""The project editor screen — replaces program.py (956 lines mixing DSL parsing,
codegen, Tk widgets, and execution). This file is UI only; DSL logic lives in
dsl/, execution in execution/."""
import tkinter as tk
from tkinter import messagebox

from dsl import codegen
from execution import exporter, runner
from models.macro import MacroRepo
from models.settings import CODE_DISPLAY_HIDDEN, CODE_DISPLAY_SHOWN_PACKED, CONSOLE_SHOWN
from ui import theme
from ui.widgets import buttons
from ui.widgets.code_editor import CodeEditor
from ui.widgets.scrollable_frame import ScrollableFrame

BLOCK_CATEGORIES = [
    ("Console", ["ShowProgramDuration()", "ShowText(text)"]),
    ("Loop", ["Loop(number_of_repeats)", "ExitLoop", "InfLoop", "EndLoop"]),
    ("If", ["IfPixelColor(x, y, r, g, b)", "Else", "EndIf"]),
    ("Wait", ["WaitSeconds(number_of_seconds)", "WaitForKeyboard(keyname)", "WaitForPixel(x, y, r, g, b)"]),
    ("Mouse", ["MouseDown(left)", "MouseUp(left)", "MoveMouseTo(x, y)", "ClickMouse(left)", "MoveAndClickMouse(x, y, left)"]),
    ("Keyboard", ["ClickOnKeyboard(keyname)", "KeyDown(keyname)", "KeyUp(keyname)", "WriteText(text)"]),
]


class EditorScreen(tk.Frame):
    def __init__(self, parent, ctx):
        super().__init__(parent, bg=theme.BG_APP)
        self.ctx = ctx
        self.project = ctx.current_project
        self.macro_repo = MacroRepo(self.project)
        self.sidebar_mode = "blocks"

        self._build_top_bar()
        self._build_body()

        self.code_editor.console_enabled = self.project.settings.console_mode == CONSOLE_SHOWN
        self.code_editor.set_text(self._read_code())
        self._refresh_sidebar()

    # --- layout ------------------------------------------------------------
    def _build_top_bar(self):
        bar = buttons.app_frame(self)
        bar.pack(fill="x", padx=16, pady=10)

        buttons.ghost_button(bar, "◀ Projects", command=self._back_to_list).pack(side="left")
        buttons.heading_label(bar, self.project.name, font=theme.heading_font(16)).pack(side="left", padx=20)

        buttons.primary_button(bar, "Start", command=self._start).pack(side="right")
        buttons.info_button(bar, "Position && Color Helper", command=self._open_helper).pack(side="right", padx=8)
        buttons.ghost_button(bar, "Settings", command=self._open_settings).pack(side="right", padx=8)

    def _build_body(self):
        body = buttons.app_frame(self)
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        sidebar = buttons.panel_frame(body, width=260)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        main = buttons.app_frame(body)
        main.pack(side="left", fill="both", expand=True)

        controls = buttons.app_frame(main)
        controls.pack(fill="x", pady=(0, 8))
        buttons.body_label(controls, "Time before start (s):").pack(side="left")
        self.time_var = tk.StringVar(value=str(self.project.settings.start_delay))
        time_entry = buttons.entry(controls, textvariable=self.time_var, width=8)
        time_entry.pack(side="left", padx=(6, 20))
        time_entry.bind("<FocusOut>", self._save_start_delay)

        buttons.body_label(controls, "Stop key:").pack(side="left")
        self.stop_var = tk.StringVar(value=self.project.settings.stop_key)
        stop_entry = buttons.entry(controls, textvariable=self.stop_var, width=8)
        stop_entry.pack(side="left", padx=6)
        stop_entry.bind("<FocusOut>", self._save_stop_key)

        self.code_editor = CodeEditor(main, on_save=self._save_code)
        self.code_editor.pack(fill="both", expand=True)

    def _build_sidebar(self, sidebar):
        toggle_row = buttons.app_frame(sidebar, bg=theme.BG_PANEL)
        toggle_row.pack(fill="x", pady=8, padx=8)
        self.blocks_btn = buttons.ghost_button(toggle_row, "Blocks", command=self._show_blocks)
        self.blocks_btn.pack(side="left", expand=True, fill="x")
        self.macro_btn = buttons.ghost_button(toggle_row, "Macro", command=self._show_macros)
        self.macro_btn.pack(side="left", expand=True, fill="x")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_sidebar())
        buttons.entry(sidebar, textvariable=self.search_var).pack(fill="x", padx=8, pady=(0, 8))

        self.sidebar_scroll = ScrollableFrame(sidebar, bg=theme.BG_PANEL)
        self.sidebar_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.sidebar_scroll.body.configure(bg=theme.BG_PANEL)

    def _refresh_sidebar(self):
        for child in self.sidebar_scroll.body.winfo_children():
            child.destroy()

        self.blocks_btn.config(bg=theme.SELECTION if self.sidebar_mode == "blocks" else theme.BG_PANEL_ALT)
        self.macro_btn.config(bg=theme.SELECTION if self.sidebar_mode == "macro" else theme.BG_PANEL_ALT)

        if self.sidebar_mode == "blocks":
            self._render_blocks()
        else:
            self._render_macros()
        self.sidebar_scroll.scroll_to_top()

    def _render_blocks(self):
        body = self.sidebar_scroll.body
        query = self.search_var.get().strip().lower()
        any_shown = False
        for title, snippets in BLOCK_CATEGORIES:
            title_matches = query in title.lower()
            matching_snippets = snippets if title_matches else [s for s in snippets if query in s.lower()]
            if query and not matching_snippets:
                continue
            any_shown = True
            buttons.muted_label(body, title.upper(), bg=theme.BG_PANEL).pack(anchor="w", pady=(10, 2))
            for snippet in matching_snippets:
                b = buttons.ghost_button(body, snippet, command=lambda s=snippet: self._insert_snippet(s))
                b.pack(fill="x", pady=2)
        if query and not any_shown:
            buttons.muted_label(body, "No blocks match your search.", bg=theme.BG_PANEL).pack(pady=10)

    def _render_macros(self):
        body = self.sidebar_scroll.body
        buttons.primary_button(body, "+ Add Macro", command=self._open_recorder).pack(fill="x", pady=(0, 10))
        query = self.search_var.get().strip().lower()
        names = [n for n in self.macro_repo.list_names() if query in n.lower()]
        for name in names:
            row = buttons.app_frame(body, bg=theme.BG_PANEL)
            row.pack(fill="x", pady=2)
            b = buttons.ghost_button(row, name, command=lambda n=name: self._insert_snippet(f"Macro({n})"))
            b.pack(side="left", fill="x", expand=True)
            buttons.danger_button(row, "x", command=lambda n=name: self._delete_macro(n), padx=8, pady=4).pack(side="left")
        if query and not names:
            buttons.muted_label(body, "No macros match your search.", bg=theme.BG_PANEL).pack(pady=10)

    # --- sidebar actions -----------------------------------------------------
    def _show_blocks(self):
        self.sidebar_mode = "blocks"
        self._refresh_sidebar()

    def _show_macros(self):
        self.sidebar_mode = "macro"
        self._refresh_sidebar()

    def _insert_snippet(self, snippet):
        self.code_editor.insert_snippet_at_cursor(snippet)

    def _delete_macro(self, name):
        result = messagebox.askquestion("Confirmation", f'Are you sure you want to delete "{name}" macro?')
        if result == "yes":
            self.macro_repo.delete(name)
            self._refresh_sidebar()

    def _open_recorder(self):
        from ui.screens.macro_recorder import MacroRecorderScreen
        self.code_editor.flush()
        self.ctx.navigator.go_to(MacroRecorderScreen, return_to=EditorScreen)

    def _open_helper(self):
        from ui.screens.position_helper import PositionHelperScreen
        self.code_editor.flush()
        self.ctx.navigator.go_to(PositionHelperScreen, return_to=EditorScreen)

    def _open_settings(self):
        from ui.screens.settings import SettingsScreen
        self.code_editor.flush()
        self.ctx.navigator.go_to(SettingsScreen, return_to=EditorScreen)

    def _back_to_list(self):
        from ui.screens.project_list import ProjectListScreen
        self.code_editor.flush()
        self.ctx.navigator.go_to(ProjectListScreen)

    # --- persistence -----------------------------------------------------
    def _read_code(self):
        try:
            return self.project.code_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""

    def _save_code(self, content):
        self.project.code_file.write_text(content, encoding="utf-8")

    def _save_start_delay(self, event=None):
        value = self.time_var.get()
        try:
            self.project.settings.start_delay = float(value)
        except ValueError:
            messagebox.showerror("Time Start Error", f"'{value}' is not a number")
            self.time_var.set(str(self.project.settings.start_delay))
            return
        self.project.save()

    def _save_stop_key(self, event=None):
        from dsl.tokens import is_key_on_keyboard
        value = self.stop_var.get()
        if not is_key_on_keyboard(value):
            messagebox.showerror("Stop Key Error", f"'{value}' is not a recognized key")
            self.stop_var.set(self.project.settings.stop_key)
            return
        self.project.settings.stop_key = value
        self.project.save()

    def on_leave(self):
        self.code_editor.flush()

    # --- running -----------------------------------------------------
    def _start(self):
        self.code_editor.flush()
        result = self.code_editor.parse_current()
        if not result.ok:
            messagebox.showerror("Program Error", result.errors[0].message)
            return

        settings = self.project.settings
        pack_macros = settings.code_display_mode == CODE_DISPLAY_SHOWN_PACKED
        source = codegen.generate(
            result.commands,
            stop_key=settings.stop_key,
            start_delay=settings.start_delay,
            macros_dir=self.project.macros_dir,
            pack_macros=pack_macros,
            macro_provider=self.macro_repo.load if pack_macros else None,
        )

        stopped, console_lines, error = runner.run(source)
        if stopped:
            messagebox.showinfo("Bot Stopped", f"Bot successfully stopped using key '{settings.stop_key}'")
        elif error is not None:
            messagebox.showerror("Executing Error", "There was an error while executing the program")

        if settings.console_mode == CONSOLE_SHOWN and console_lines:
            exporter.show_in_notepad("\n".join(console_lines))
        if settings.code_display_mode != CODE_DISPLAY_HIDDEN:
            exporter.show_in_notepad(source, suffix=".py")
