"""DSL text -> validated command list. Pure Python, no Tk import, unit-testable.

Ports the validation logic that used to live inline in program.py's start()
(line-by-line if/elif chain), but separates "is this DSL valid" (here) from
"what Python does this produce" (codegen.py) — the two were tangled together
in one 400-line Tkinter callback before.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

from dsl import tokens


@dataclass
class ParsedCommand:
    name: str
    args: Dict[str, Any]
    line_no: int
    line_text: str


@dataclass
class ParseError:
    line_no: int
    message: str
    line_text: str = ""

    def __str__(self):
        return self.message


@dataclass
class ParseResult:
    commands: List[ParsedCommand] = field(default_factory=list)
    errors: List[ParseError] = field(default_factory=list)

    @property
    def ok(self):
        return not self.errors


def _err(result, line_no, message, line_text=""):
    result.errors.append(ParseError(line_no, message, line_text))


def _split_csv(raw):
    return [p for p in raw.replace(" ", "").split(",")]


def parse(dsl_text, console_enabled=True):
    """Parse BotMaker DSL source into a validated ParsedCommand list.

    console_enabled gates ShowProgramDuration/ShowText, matching the project's
    console_mode setting (these commands only make sense if console output is on).
    """
    result = ParseResult()
    stack = []  # 'loop' | 'if', tracks nesting for balance checking

    for line_no, raw_line in enumerate(dsl_text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0]
        parts = line.split("(")
        name = parts[0].replace(" ", "").replace("\t", "")

        if len(parts) > 2:
            _err(result, line_no, f"Bad implementation in line {line_no}.\n{raw_line}", raw_line)
            continue

        if name == "":
            continue  # blank or comment-only line

        if name not in tokens.ALL_COMMANDS:
            _err(result, line_no, f"Not recognized command '{name}' in line {line_no}.\n{raw_line}", raw_line)
            continue

        has_parens = len(parts) == 2
        raw_arg = parts[1][:-1] if has_parens and parts[1].endswith(")") else ""

        if name in tokens.NO_ARG_COMMANDS:
            if has_parens:
                _err(result, line_no, f"Bad implementation in line {line_no}.\n{raw_line}", raw_line)
                continue
            args = {}
        elif name in tokens.EMPTY_PAREN_COMMANDS:
            if not has_parens:
                _err(result, line_no, f"Bad implementation in line {line_no}.\n{raw_line}", raw_line)
                continue
            if not console_enabled:
                _err(result, line_no, "You have to enable console in settings to use console functions.", raw_line)
                continue
            args = {}
        else:
            if not has_parens:
                _err(result, line_no, f"Bad implementation in line {line_no}.\n{raw_line}", raw_line)
                continue
            args = _validate_args(result, name, raw_arg, line_no, raw_line, console_enabled)
            if args is None:
                continue  # validator already recorded the error

        if name in tokens.BLOCK_OPENERS:
            stack.append(tokens.BLOCK_OPENERS[name])
        elif name in tokens.BLOCK_CLOSERS:
            expected = tokens.BLOCK_CLOSERS[name]
            if not stack or stack[-1] != expected:
                _err(result, line_no, f"'{name}' has no matching opener (line {line_no}).", raw_line)
                continue
            stack.pop()

        result.commands.append(ParsedCommand(name=name, args=args, line_no=line_no, line_text=raw_line))

    for kind in reversed(stack):
        closer = "EndLoop" if kind == "loop" else "EndIf"
        _err(result, 0, f"Unclosed block: missing {closer}.")

    return result


def _validate_args(result, name, raw_arg, line_no, raw_line, console_enabled):
    def fail(msg):
        _err(result, line_no, f"{msg} (line {line_no}).\n{raw_line}", raw_line)
        return None

    key_commands = ("ClickOnKeyboard", "KeyDown", "KeyUp", "WaitForKeyboard")
    if name in key_commands:
        key = raw_arg.replace(" ", "")
        if not tokens.is_key_on_keyboard(key):
            return fail(f"Not recognized key name '{key}'")
        return {"key": key}

    if name == "WaitSeconds":
        arg = raw_arg.replace(" ", "")
        if not tokens.is_number(arg):
            return fail(f"Not recognized number '{arg}'")
        return {"seconds": float(arg)}

    if name == "MoveMouseTo":
        pos = _split_csv(raw_arg)
        if len(pos) != 2 or not all(p.isdigit() for p in pos):
            return fail("Bad position implementation")
        return {"x": int(pos[0]), "y": int(pos[1])}

    if name in ("MouseUp", "MouseDown", "ClickMouse"):
        button = raw_arg.replace(" ", "")
        if button not in tokens.MOUSE_BUTTONS:
            return fail("Not recognized mouse button")
        return {"button": button}

    if name == "Loop":
        arg = raw_arg.replace(" ", "")
        if not arg.isdigit():
            return fail(f"Not recognized digit '{arg}'")
        return {"count": int(arg)}

    if name in ("WaitForPixel", "IfPixelColor"):
        parts = _split_csv(raw_arg)
        if len(parts) != 5:
            return fail("Bad arguments implementation")
        if not all(p.isdigit() for p in parts):
            return fail("Bad position implementation")
        x, y, r, g, b = (int(p) for p in parts)
        if not all(0 <= v <= 256 for v in (r, g, b)):
            return fail("Bad position implementation")
        return {"x": x, "y": y, "r": r, "g": g, "b": b}

    if name == "Macro":
        macro_name = raw_arg.replace(" ", "")
        return {"name": macro_name}

    if name == "WriteText":
        return {"text": raw_arg}

    if name == "MoveAndClickMouse":
        parts = _split_csv(raw_arg)
        if len(parts) != 3:
            return fail("Bad position implementation")
        x, y, button = parts
        if not x.isdigit() or not y.isdigit():
            return fail("Bad position implementation")
        if button not in tokens.MOUSE_BUTTONS:
            return fail("Not recognized mouse button")
        return {"x": int(x), "y": int(y), "button": button}

    if name == "ShowText":
        if not console_enabled:
            return fail("You have to enable console in settings to use console functions")
        return {"text": raw_arg}

    raise AssertionError(f"unhandled command in _validate_args: {name}")
