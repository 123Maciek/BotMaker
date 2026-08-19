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
_WORD_PREFIX_RE = re.compile(r"[A-Za-z]+$")

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

        self._build_autocomplete_popup()

        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.gutter.bind("<MouseWheel>", self._on_mousewheel)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<Shift-Tab>", self._on_shift_tab)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<Up>", self._on_up)
        self.text.bind("<Down>", self._on_down)
        self.text.bind("<Button-1>", lambda e: self._hide_autocomplete())
        self.text.bind("<FocusOut>", lambda e: self._hide_autocomplete())
        self.text.bind("<Escape>", lambda e: self._hide_autocomplete())

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
        """Insert a DSL snippet at the cursor's line. If that line is empty or
        contains only whitespace (e.g. leading indentation with nothing typed
        yet), the snippet is appended to the end of that same line instead of
        starting a new one — otherwise a new line is inserted below. Bounds-
        checked against the trailing implicit blank line (the old program.py
        could IndexError here)."""
        line_no = int(self.text.index(tk.INSERT).split(".")[0])
        content = self.get_text()
        lines = content.split("\n")
        idx = min(line_no - 1, len(lines) - 1)
        if idx < 0:
            lines = [snippet]
        elif lines[idx].strip() == "":
            lines[idx] = lines[idx] + snippet
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
        if self._autocomplete_visible():
            self._accept_autocomplete()
            return "break"
        if self.text.tag_ranges("sel"):
            self._indent_selection(dedent=False)
        else:
            self.text.insert(tk.INSERT, INDENT_UNIT)
        return "break"

    def _on_shift_tab(self, event):
        self._hide_autocomplete()
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
        if self._autocomplete_visible():
            self._accept_autocomplete()
            return "break"
        line_no = self.text.index(tk.INSERT).split(".")[0]
        line_text = self.text.get(f"{line_no}.0", f"{line_no}.end")
        leading = line_text[: len(line_text) - len(line_text.lstrip(" \t"))]
        self.text.insert(tk.INSERT, "\n" + leading)
        return "break"

    def _on_up(self, event):
        if not self._autocomplete_visible():
            return None
        self._move_autocomplete_selection(-1)
        return "break"

    def _on_down(self, event):
        if not self._autocomplete_visible():
            return None
        self._move_autocomplete_selection(1)
        return "break"

    # --- autocomplete (themed dropdown, Tab/Enter/click to accept) -----------
    def _build_autocomplete_popup(self):
        self._autocomplete_names = []  # command names, aligned to dropdown rows
        self._autocomplete_range = None  # (start_index, end_index) to replace on accept
        self._autocomplete_index = 0  # currently highlighted row

        self.autocomplete_frame = tk.Frame(
            self.text, bg=theme.BG_INPUT, highlightthickness=1, highlightbackground=theme.BORDER,
        )
        # A read-only Text (not a Listbox) so each row can have the command
        # name colored like a keyword while the rest of the template stays
        # the normal text color — a Listbox can only color a whole row.
        self.autocomplete_list = tk.Text(
            self.autocomplete_frame, bg=theme.BG_INPUT, fg=theme.FG_PRIMARY,
            highlightthickness=0, bd=0, wrap="none", cursor="arrow", takefocus=0,
            font=theme.mono_font(11), state="disabled",
        )
        self.autocomplete_list.tag_configure("kw", foreground=theme.SYNTAX_KEYWORD)
        self.autocomplete_list.tag_configure("row_selected", background=theme.SELECTION_SOFT)
        self.autocomplete_scrollbar = ttk.Scrollbar(
            self.autocomplete_frame, orient="vertical", command=self.autocomplete_list.yview,
        )
        self.autocomplete_list.configure(yscrollcommand=self.autocomplete_scrollbar.set)
        self.autocomplete_list.pack(side="left", fill="both", expand=True)
        self.autocomplete_scrollbar.pack(side="right", fill="y")
        self.autocomplete_list.bind("<ButtonRelease-1>", self._on_autocomplete_click)

    def _on_key_release(self, event):
        self._sync_gutter()
        if event.keysym not in ("Tab", "ISO_Left_Tab", "Return", "Escape", "Up", "Down"):
            self._update_autocomplete()

    def _autocomplete_visible(self):
        return bool(self._autocomplete_names)

    def _update_autocomplete(self):
        self._hide_autocomplete()
        if self.text.tag_ranges("sel"):
            return

        index = self.text.index(tk.INSERT)
        line_no, col_str = index.split(".")
        col = int(col_str)
        line_text = self.text.get(f"{line_no}.0", f"{line_no}.end")
        before, after = line_text[:col], line_text[col:]

        if after[:1].isalpha():
            return  # cursor is in the middle of a word, not at its end

        match = _WORD_PREFIX_RE.search(before)
        if not match:
            return
        prefix = match.group(0)

        candidates = sorted(
            (c for c in tokens.ALL_COMMANDS if c.lower().startswith(prefix.lower())),
            key=lambda c: (c.lower() != prefix.lower(), c),
        )
        if not candidates or candidates == [prefix]:
            return

        self._autocomplete_names = candidates
        self._autocomplete_range = (f"{line_no}.{col - len(prefix)}", f"{line_no}.{col}")
        self._autocomplete_index = 0

        self.autocomplete_list.configure(state="normal")
        self.autocomplete_list.delete("1.0", "end")
        for i, name in enumerate(candidates, start=1):
            self.autocomplete_list.insert("end", tokens.COMMAND_TEMPLATES[name] + "\n")
            self.autocomplete_list.tag_add("kw", f"{i}.0", f"{i}.{len(name)}")
        self.autocomplete_list.configure(state="disabled")
        self._highlight_autocomplete_row()

        visible_rows = min(len(candidates), 8)
        row_width = max(len(tokens.COMMAND_TEMPLATES[n]) for n in candidates)
        self.autocomplete_list.configure(height=visible_rows, width=min(row_width + 2, 40))

        bbox = self.text.bbox(tk.INSERT)
        if bbox:
            x, y, _w, h = bbox
            self.autocomplete_frame.place(x=x, y=y + h)
            self.autocomplete_frame.lift()

    def _highlight_autocomplete_row(self):
        self.autocomplete_list.tag_remove("row_selected", "1.0", "end")
        row = self._autocomplete_index + 1
        self.autocomplete_list.tag_add("row_selected", f"{row}.0", f"{row + 1}.0")
        self.autocomplete_list.see(f"{row}.0")

    def _move_autocomplete_selection(self, delta):
        size = len(self._autocomplete_names)
        if size == 0:
            return
        self._autocomplete_index = (self._autocomplete_index + delta) % size
        self._highlight_autocomplete_row()

    def _on_autocomplete_click(self, event):
        index = self.autocomplete_list.index(f"@{event.x},{event.y}")
        row = int(index.split(".")[0]) - 1
        if 0 <= row < len(self._autocomplete_names):
            self._autocomplete_index = row
            self._accept_autocomplete()

    def _accept_autocomplete(self):
        if not self._autocomplete_visible():
            return
        name = self._autocomplete_names[self._autocomplete_index]
        template = tokens.COMMAND_TEMPLATES[name]
        start, end = self._autocomplete_range
        self._hide_autocomplete()
        self.text.delete(start, end)
        self.text.insert(start, template)
        self.text.mark_set(tk.INSERT, f"{start} + {len(template)}c")

    def _hide_autocomplete(self):
        self._autocomplete_names = []
        self._autocomplete_range = None
        self.autocomplete_frame.place_forget()

    # --- gutter ------------------------------------------------------------
    def _on_text_scroll(self, first, last):
        self.scrollbar.set(first, last)
        self.gutter.yview_moveto(first)

    def _on_scrollbar(self, *args):
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_mousewheel(self, event):
        self._hide_autocomplete()
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
