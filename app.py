"""In-process navigation and shared app state — replaces name.txt/needreset.txt
and the old subprocess-per-screen handoff with one long-running process."""
from ui import theme
from ui.widgets import buttons


class Navigator:
    def __init__(self, root, container, ctx):
        self.root = root
        self.container = container
        self.ctx = ctx
        self._current = None

    def go_to(self, screen_class, **kwargs):
        if self._current is not None:
            teardown = getattr(self._current, "on_leave", None)
            if teardown:
                teardown()
            self._current.destroy()
        screen = screen_class(self.container, self.ctx, **kwargs)
        screen.pack(fill="both", expand=True)
        self._current = screen
        on_enter = getattr(screen, "on_enter", None)
        if on_enter:
            on_enter()
        return screen


class AppContext:
    def __init__(self, root, project_repo):
        self.root = root
        self.project_repo = project_repo
        self.current_project = None
        container = buttons.app_frame(root)
        container.pack(fill="both", expand=True)
        self.navigator = Navigator(root, container, self)

    def set_current_project(self, project):
        self.current_project = project


def build_root():
    import tkinter as tk
    root = tk.Tk()
    root.title("Bot Maker")
    _fix_word_boundaries(root)
    theme.configure_style(root)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width, height = 1050, 850
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    return root


def _fix_word_boundaries(root):
    """Tk/Tcl's default double-click "select word" boundary (tcl_wordchars /
    tcl_nonwordchars) is known to behave inconsistently on Windows, sometimes
    selecting a whole `Command(arg)`-style run instead of stopping at the
    parens. These are process-wide Tcl variables (not per-widget), so setting
    them once here — to the straightforward "word char = letter/digit/
    underscore" definition — fixes double-click selection for every Text/
    Entry widget in the app, including the code editor's DSL, e.g. double-
    clicking "keyname" in WaitForKeyboard(keyname) now selects just that word."""
    root.tk.eval(r"""
        set ::tcl_wordchars {\w}
        set ::tcl_nonwordchars {\W}
    """)
