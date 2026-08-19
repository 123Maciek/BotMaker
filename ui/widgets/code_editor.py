"""The DSL code editor widget — replaces program.py's bare
`tk.Text(root, width=155, height=55)` (no font, no highlighting, no line numbers,
no scrollbar, full-file write on every keystroke).

Pure stdlib tkinter: a line-number gutter Text kept in sync with the main Text,
a real ttk scrollbar, regex+tag syntax highlighting keyed off dsl.tokens (so it
can never highlight something the parser wouldn't accept), a debounced autosave,
and live inline feedback when Loop/EndLoop or If/EndIf are unbalanced.
"""
import re
import tkinter as tk
from tkinter import ttk

from dsl import parser, tokens
from ui import theme

_KEYWORD_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in tokens.ALL_COMMANDS) + r")\b")
_NUMBER_RE = re.compile(r"(?<![\w])\d+(\.\d+)?\b")
_STRING_RE = re.compile(r"'[^']*'|\"[^\"]*\"")
_COMMENT_RE = re.compile(r"#.*$")

AUTOSAVE_DELAY_MS = 750
DEBOUNCE_MS = 400
INDENT_UNIT = "  "  # 2 spaces — deliberately narrower than a raw Tab character


class CodeEditor(tk.Frame):
    def __init__(self, parent, on_save=None, console_enabled=True, **kwargs):
        opts = dict(bg=theme.BG_APP)
        opts.update(kwargs)
        super().__init__(parent, **opts)
        self.on_save = on_save
        self.console_enabled = console_enabled
        self._autosave_job = None
        self._dirty = False

        editor_row = tk.Frame(self, bg=theme.BG_APP)
        editor_row.pack(fill="both", expand=True)

        self.gutter = tk.Text(
            editor_row, width=4, padx=6, pady=8, takefocus=0, border=0,
            state="disabled", wrap="none",
            bg=theme.GUTTER_BG, fg=theme.GUTTER_FG,
            font=theme.mono_font(11),
        )
        self.gutter.pack(side="left", fill="y")

        self.text = tk.Text(
            editor_row, undo=True, wrap="none", padx=8, pady=8,
            bg=theme.BG_INPUT, fg=theme.FG_PRIMARY, insertbackground=theme.FG_PRIMARY,
            selectbackground=theme.SELECTION, border=0, highlightthickness=0,
            font=theme.mono_font(11),
        )
        self.text.pack(side="left", fill="both", expand=True)
        # narrow the on-screen width of a literal Tab character too, in case one
        # ends up in the buffer (pasted content, older files, etc.)
        tab_px = theme.mono_font(11).measure(" " * 4)
        self.text.configure(tabs=(tab_px,))

        self.scrollbar = ttk.Scrollbar(editor_row, orient="vertical", command=self._on_scrollbar)
        self.scrollbar.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=self._on_text_scroll)

        self._configure_tags()

        self.status = tk.Label(
            self, text="", anchor="w", bg=theme.BG_APP, fg=theme.ACCENT_RED,
            font=theme.body_font(9),
        )
        self.status.pack(fill="x", padx=4)

        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", lambda e: self._sync_gutter())
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.gutter.bind("<MouseWheel>", self._on_mousewheel)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<Shift-Tab>", self._on_shift_tab)
        self.text.bind("<Return>", self._on_return)

        self._sync_gutter()

    # --- content API -----------------------------------------------------
    def get_text(self):
        return self.text.get("1.0", "end-1c")

    def set_text(self, content):
        self.text.delete("1.0", "end")
        self.text.insert("end", content)
        self.text.edit_modified(False)
        self._dirty = False
        self._sync_gutter()
        self._highlight_and_check()

    def insert_snippet_at_cursor(self, snippet):
        """Insert a DSL snippet at the cursor's line, replacing an empty line if
        the cursor sits on one. Bounds-checked against the trailing implicit blank
        line (the old program.py could IndexError here)."""
        line_no = int(self.text.index(tk.INSERT).split(".")[0])
        content = self.get_text()
        lines = content.split("\n")
        idx = min(line_no - 1, len(lines) - 1)
        if idx < 0:
            lines = [snippet]
        elif lines[idx] == "":
            lines[idx] = snippet
        else:
            lines.insert(idx + 1, snippet)
        self.set_text("\n".join(lines))
        # set_text() is normally used for loading (it deliberately does not
        # autosave) and clears the dirty flag, so _trigger_autosave() would
        # no-op here. This is a real content change, so save unconditionally.
        if self.on_save is not None:
            self.on_save(self.get_text())

    # --- tab / indent / enter ------------------------------------------------
    def _on_tab(self, event):
        if self.text.tag_ranges("sel"):
            self._indent_selection(dedent=False)
        else:
            self.text.insert(tk.INSERT, INDENT_UNIT)
        return "break"

    def _on_shift_tab(self, event):
        if self.text.tag_ranges("sel"):
            self._indent_selection(dedent=True)
        else:
            self._dedent_line(self.text.index(tk.INSERT).split(".")[0])
        return "break"

    def _indent_selection(self, dedent):
        start_line = int(self.text.index("sel.first").split(".")[0])
        end_index = self.text.index("sel.last")
        end_line = int(end_index.split(".")[0])
        end_col = int(end_index.split(".")[1])
        # if the selection merely touches the start of the last line (e.g. a
        # triple-click or drag that ends at column 0), don't indent that line —
        # matches how other editors treat a selection ending at line-start
        if end_col == 0 and end_line > start_line:
            end_line -= 1

        for line_no in range(start_line, end_line + 1):
            if dedent:
                self._dedent_line(line_no)
            else:
                self.text.insert(f"{line_no}.0", INDENT_UNIT)

        self.text.tag_remove("sel", "1.0", "end")
        self.text.tag_add("sel", f"{start_line}.0", f"{end_line}.end")
        self.text.mark_set(tk.INSERT, f"{end_line}.end")

    def _dedent_line(self, line_no):
        line_text = self.text.get(f"{line_no}.0", f"{line_no}.end")
        if line_text.startswith(INDENT_UNIT):
            remove = len(INDENT_UNIT)
        elif line_text.startswith("\t"):
            remove = 1
        elif line_text.startswith(" "):
            remove = min(len(line_text) - len(line_text.lstrip(" ")), len(INDENT_UNIT))
        else:
            remove = 0
        if remove:
            self.text.delete(f"{line_no}.0", f"{line_no}.{remove}")

    def _on_return(self, event):
        line_no = self.text.index(tk.INSERT).split(".")[0]
        line_text = self.text.get(f"{line_no}.0", f"{line_no}.end")
        leading = line_text[: len(line_text) - len(line_text.lstrip(" \t"))]
        self.text.insert(tk.INSERT, "\n" + leading)
        return "break"

    # --- gutter ------------------------------------------------------------
    def _on_text_scroll(self, first, last):
        self.scrollbar.set(first, last)
        self.gutter.yview_moveto(first)

    def _on_scrollbar(self, *args):
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_mousewheel(self, event):
        self.text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.gutter.yview_moveto(self.text.yview()[0])
        return "break"

    def _sync_gutter(self):
        line_count = int(self.text.index("end-1c").split(".")[0])
        numbers = "\n".join(str(i) for i in range(1, line_count + 1))
        self.gutter.configure(state="normal")
        self.gutter.delete("1.0", "end")
        self.gutter.insert("1.0", numbers)
        self.gutter.configure(state="disabled")
        self.gutter.yview_moveto(self.text.yview()[0])

    # --- highlighting + validation ------------------------------------------
    def _configure_tags(self):
        self.text.tag_configure("keyword", foreground=theme.SYNTAX_KEYWORD)
        self.text.tag_configure("number", foreground=theme.SYNTAX_NUMBER)
        self.text.tag_configure("string", foreground=theme.SYNTAX_STRING)
        self.text.tag_configure("comment", foreground=theme.SYNTAX_COMMENT)
        self.text.tag_configure("error_line", background=theme.SYNTAX_ERROR_BG)
        # tag priority is creation order in Tk — "sel" is created internally
        # before our tags, so without this it loses to error_line's background
        # and a selection on a red error line was invisible.
        self.text.tag_raise("sel")

    def _on_modified(self, event=None):
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        self._dirty = True
        self._sync_gutter()
        if self._autosave_job:
            self.after_cancel(self._autosave_job)
        self._autosave_job = self.after(DEBOUNCE_MS, self._highlight_and_check)

    def _highlight_and_check(self):
        self._autosave_job = None
        self._apply_syntax_highlighting()
        self._check_balance()
        self._trigger_autosave()

    def _apply_syntax_highlighting(self):
        for tag in ("keyword", "number", "string", "comment", "error_line"):
            self.text.tag_remove(tag, "1.0", "end")

        content = self.get_text()
        for line_no, line in enumerate(content.split("\n"), start=1):
            for match in _KEYWORD_RE.finditer(line):
                self._tag_range("keyword", line_no, match)
            for match in _STRING_RE.finditer(line):
                self._tag_range("string", line_no, match)
            for match in _NUMBER_RE.finditer(line):
                self._tag_range("number", line_no, match)
            comment_match = _COMMENT_RE.search(line)
            if comment_match:
                self._tag_range("comment", line_no, comment_match)

    def _tag_range(self, tag, line_no, match):
        self.text.tag_add(tag, f"{line_no}.{match.start()}", f"{line_no}.{match.end()}")

    def _check_balance(self):
        result = parser.parse(self.get_text(), console_enabled=self.console_enabled)
        if result.ok:
            self.status.configure(text="")
            return
        first = result.errors[0]
        if first.line_no:
            self.text.tag_add("error_line", f"{first.line_no}.0", f"{first.line_no}.end+1c")
        self.status.configure(text=first.message.splitlines()[0])

    def parse_current(self):
        """Re-parse the current buffer immediately (not debounced) — used by Start/export."""
        return parser.parse(self.get_text(), console_enabled=self.console_enabled)

    # --- autosave ------------------------------------------------------------
    def _trigger_autosave(self):
        if not self._dirty or self.on_save is None:
            return
        self.on_save(self.get_text())
        self._dirty = False

    def flush(self):
        """Save immediately, bypassing the debounce — call on navigate-away/close
        so the last few keystrokes are never lost."""
        if self._dirty and self.on_save is not None:
            self.on_save(self.get_text())
            self._dirty = False
