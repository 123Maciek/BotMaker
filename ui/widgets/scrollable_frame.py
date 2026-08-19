"""Shared canvas+scrollbar scrollable list pattern (replaces the copy-pasted
canvas/scrollbar block duplicated across the old main.py and program.py)."""
import tkinter as tk
from tkinter import ttk

from ui import theme


class ScrollableFrame(tk.Frame):
    """A vertically scrollable frame. Put child widgets in `.body`."""

    def __init__(self, parent, **kwargs):
        opts = dict(bg=theme.BG_APP)
        opts.update(kwargs)
        super().__init__(parent, **opts)

        self._canvas = tk.Canvas(self, bg=theme.BG_APP, highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self.body = tk.Frame(self._canvas, bg=theme.BG_APP)

        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")
        self._window = self._canvas.create_window((0, 0), window=self.body, anchor="nw")

        self.body.bind("<Configure>", self._on_body_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

    def _on_body_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._window, width=event.width)

    def _on_mousewheel(self, event):
        # Without this guard, scrolling when the content is shorter than the
        # visible area still shifts the canvas's view within its (tiny)
        # scrollregion — the body then renders lower than the canvas top,
        # leaving blank space below it (e.g. the "Add Macro" button drifting
        # down when there are few/no macros to scroll through).
        bbox = self._canvas.bbox("all")
        if bbox is None:
            return
        content_height = bbox[3] - bbox[1]
        if content_height <= self._canvas.winfo_height():
            return
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def scroll_to_top(self):
        self._canvas.yview_moveto(0)
