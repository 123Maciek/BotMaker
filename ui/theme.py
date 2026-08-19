"""Single source of truth for BotMaker's dark theme: palette, fonts, ttk.Style."""
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# --- Palette -----------------------------------------------------------
BG_APP = "#1e1f24"
BG_PANEL = "#26282f"
BG_PANEL_ALT = "#2c2f38"
BG_INPUT = "#1a1b1f"
BORDER = "#3a3d47"
SELECTION = "#3a5478"
SELECTION_SOFT = "#4f6f96"  # lighter, more muted tint of SELECTION — for hover/highlight rows

FG_PRIMARY = "#e6e6e9"
FG_MUTED = "#9a9ca6"
FG_DISABLED = "#5c5e68"

ACCENT_GREEN = "#3fb950"
ACCENT_GREEN_HOVER = "#4fd363"
ACCENT_RED = "#e5534b"
ACCENT_RED_HOVER = "#f0685f"
ACCENT_BLUE = "#4c8bf5"
ACCENT_BLUE_HOVER = "#6ea0f7"
ACCENT_YELLOW = "#d9a52c"

# Syntax highlight colors (code editor)
SYNTAX_KEYWORD = "#c586c0"
SYNTAX_STRING = "#ce9178"
SYNTAX_NUMBER = "#b5cea8"
SYNTAX_COMMENT = "#6a9955"
SYNTAX_ERROR_BG = "#4a1f22"
GUTTER_BG = "#202127"
GUTTER_FG = "#5c5e68"

# --- Fonts ---------------------------------------------------------------
_HEADING_FAMILY = "Segoe UI"
_BODY_FAMILY = "Segoe UI"
_MONO_FALLBACKS = ("Consolas", "Courier New", "TkFixedFont")

_font_cache = {}


def _pick_available_family(candidates):
    try:
        available = set(tkfont.families())
    except tk.TclError:
        return candidates[0]
    for name in candidates:
        if name in available or name == "TkFixedFont":
            return name
    return candidates[-1]


def heading_font(size=22, weight="bold"):
    return _cached_font(_HEADING_FAMILY, size, weight)


def body_font(size=11, weight="normal"):
    return _cached_font(_BODY_FAMILY, size, weight)


def mono_font(size=11, weight="normal"):
    family = _pick_available_family(list(_MONO_FALLBACKS))
    return _cached_font(family, size, weight)


def _cached_font(family, size, weight):
    key = (family, size, weight)
    if key not in _font_cache:
        _font_cache[key] = tkfont.Font(family=family, size=size, weight=weight)
    return _font_cache[key]


def configure_style(root):
    """Apply the dark theme to ttk widgets and root window. Call once at startup."""
    root.configure(bg=BG_APP)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=BG_APP)
    style.configure("Panel.TFrame", background=BG_PANEL)

    style.configure(
        "TScrollbar",
        background=BG_PANEL_ALT,
        troughcolor=BG_APP,
        bordercolor=BG_APP,
        arrowcolor=FG_MUTED,
        relief="flat",
    )
    style.map("TScrollbar", background=[("active", BORDER)])

    style.configure(
        "TProgressbar",
        background=ACCENT_BLUE,
        troughcolor=BG_PANEL_ALT,
        bordercolor=BG_PANEL_ALT,
        lightcolor=ACCENT_BLUE,
        darkcolor=ACCENT_BLUE,
    )

    style.configure(
        "TCheckbutton",
        background=BG_PANEL,
        foreground=FG_PRIMARY,
        font=body_font(),
    )
    style.map(
        "TCheckbutton",
        background=[("active", BG_PANEL)],
        foreground=[("disabled", FG_DISABLED)],
    )

    return style


def apply_widget_defaults(widget_class, **overrides):
    """Return kwargs for a plain-tk widget with sane dark-theme defaults applied."""
    defaults = {
        "bg": BG_PANEL,
        "fg": FG_PRIMARY,
        "highlightthickness": 0,
        "bd": 0,
    }
    defaults.update(overrides)
    return defaults
