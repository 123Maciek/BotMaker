"""Per-project settings (replaces the old fixed-column set.txt / two-line settings.txt)."""
from dataclasses import dataclass, asdict

CODE_DISPLAY_HIDDEN = "hidden"
CODE_DISPLAY_SHOWN = "shown"
CODE_DISPLAY_SHOWN_PACKED = "shown_with_macros_packed"

CODE_DISPLAY_MODES = (CODE_DISPLAY_HIDDEN, CODE_DISPLAY_SHOWN, CODE_DISPLAY_SHOWN_PACKED)

CONSOLE_HIDDEN = "hidden"
CONSOLE_SHOWN = "shown"

CONSOLE_MODES = (CONSOLE_HIDDEN, CONSOLE_SHOWN)


@dataclass
class ProjectSettings:
    code_display_mode: str = CODE_DISPLAY_HIDDEN
    console_mode: str = CONSOLE_SHOWN
    stop_key: str = "esc"
    start_delay: float = 1.0

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        if not data:
            return ProjectSettings()
        return ProjectSettings(
            code_display_mode=data.get("code_display_mode", CODE_DISPLAY_HIDDEN),
            console_mode=data.get("console_mode", CONSOLE_SHOWN),
            stop_key=data.get("stop_key", "esc"),
            start_delay=float(data.get("start_delay", 1.0)),
        )
