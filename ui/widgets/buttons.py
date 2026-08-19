"""Themed widget factories. Screens should build widgets through these instead of
calling tk.Button/tk.Label/tk.Entry directly, so the dark theme applies by construction."""
import tkinter as tk

from ui import theme


def _button(parent, text, command, bg, hover_bg, fg="#ffffff", **kwargs):
    opts = dict(
        text=text,
        command=command,
        fg=fg,
        bg=bg,
        activebackground=hover_bg,
        activeforeground=fg,
        bd=0,
        relief=tk.FLAT,
        highlightthickness=0,
        font=theme.body_font(11, "bold"),
        padx=16,
        pady=8,
        cursor="hand2",
    )
    opts.update(kwargs)
    btn = tk.Button(parent, **opts)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def primary_button(parent, text, command=None, **kwargs):
    return _button(parent, text, command, theme.ACCENT_GREEN, theme.ACCENT_GREEN_HOVER, **kwargs)


def danger_button(parent, text, command=None, **kwargs):
    return _button(parent, text, command, theme.ACCENT_RED, theme.ACCENT_RED_HOVER, **kwargs)


def info_button(parent, text, command=None, **kwargs):
    return _button(parent, text, command, theme.ACCENT_BLUE, theme.ACCENT_BLUE_HOVER, **kwargs)


def ghost_button(parent, text, command=None, **kwargs):
    opts = dict(
        text=text,
        command=command,
        fg=theme.FG_PRIMARY,
        bg=theme.BG_PANEL_ALT,
        activebackground=theme.BORDER,
        activeforeground=theme.FG_PRIMARY,
        bd=0,
        relief=tk.FLAT,
        highlightthickness=0,
        font=theme.body_font(10),
        padx=10,
        pady=5,
        cursor="hand2",
    )
    opts.update(kwargs)
    btn = tk.Button(parent, **opts)
    btn.bind("<Enter>", lambda e: btn.config(bg=theme.BORDER))
    btn.bind("<Leave>", lambda e: btn.config(bg=theme.BG_PANEL_ALT))
    return btn


def heading_label(parent, text, **kwargs):
    opts = dict(text=text, bg=theme.BG_APP, fg=theme.FG_PRIMARY, font=theme.heading_font())
    opts.update(kwargs)
    return tk.Label(parent, **opts)


def body_label(parent, text, **kwargs):
    opts = dict(text=text, bg=theme.BG_APP, fg=theme.FG_PRIMARY, font=theme.body_font())
    opts.update(kwargs)
    return tk.Label(parent, **opts)


def muted_label(parent, text, **kwargs):
    opts = dict(text=text, bg=theme.BG_APP, fg=theme.FG_MUTED, font=theme.body_font(9))
    opts.update(kwargs)
    return tk.Label(parent, **opts)


def entry(parent, textvariable=None, **kwargs):
    opts = dict(
        textvariable=textvariable,
        bg=theme.BG_INPUT,
        fg=theme.FG_PRIMARY,
        insertbackground=theme.FG_PRIMARY,
        # tk.Entry uses separate colors for readonly/disabled state that don't
        # fall back to bg/fg — without these a readonly entry shows our light
        # fg text on Tk's default light system background (invisible).
        readonlybackground=theme.BG_INPUT,
        disabledbackground=theme.BG_INPUT,
        disabledforeground=theme.FG_MUTED,
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=theme.BORDER,
        highlightcolor=theme.ACCENT_BLUE,
        font=theme.body_font(),
    )
    opts.update(kwargs)
    return tk.Entry(parent, **opts)


def panel_frame(parent, **kwargs):
    opts = dict(bg=theme.BG_PANEL, highlightthickness=1, highlightbackground=theme.BORDER)
    opts.update(kwargs)
    return tk.Frame(parent, **opts)


def app_frame(parent, **kwargs):
    opts = dict(bg=theme.BG_APP)
    opts.update(kwargs)
    return tk.Frame(parent, **opts)
