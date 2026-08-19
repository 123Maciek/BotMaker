"""DSL command table — the single source of truth for valid BotMaker DSL commands.

Used by the parser (validation/dispatch) AND the code editor's syntax highlighter,
so highlighting can never drift from what the parser actually accepts.
"""
import pyautogui

# Commands written with no parentheses at all, e.g. "EndLoop"
NO_ARG_COMMANDS = ("EndLoop", "InfLoop", "ExitLoop", "Else", "EndIf")

# Commands written as Name(arg) with exactly one argument expression inside the parens
# (the argument may itself be a comma-separated list, validated per-command in parser.py)
ONE_ARG_COMMANDS = (
    "ClickOnKeyboard", "KeyDown", "KeyUp", "WaitSeconds", "WaitForKeyboard",
    "MoveMouseTo", "MouseUp", "MouseDown", "Loop", "WaitForPixel",
    "IfPixelColor", "Macro", "WriteText", "ClickMouse", "MoveAndClickMouse",
    "ShowText",
)

# Written with empty parens: "ShowProgramDuration()"
EMPTY_PAREN_COMMANDS = ("ShowProgramDuration",)

ALL_COMMANDS = NO_ARG_COMMANDS + ONE_ARG_COMMANDS + EMPTY_PAREN_COMMANDS

# Block structure: which commands open/close a Loop or an If, for balance checking
BLOCK_OPENERS = {"Loop": "loop", "InfLoop": "loop", "IfPixelColor": "if"}
BLOCK_CLOSERS = {"EndLoop": "loop", "EndIf": "if"}

MOUSE_BUTTONS = ("left", "right")

# Display/insertion template for each command — the full block, not just the
# bare name (e.g. "MoveMouseTo(x, y)"). Single source of truth for both the
# Blocks sidebar and the code editor's autocomplete dropdown.
COMMAND_TEMPLATES = {
    "ShowProgramDuration": "ShowProgramDuration()",
    "ShowText": "ShowText(text)",
    "Loop": "Loop(number_of_repeats)",
    "ExitLoop": "ExitLoop",
    "InfLoop": "InfLoop",
    "EndLoop": "EndLoop",
    "IfPixelColor": "IfPixelColor(x, y, r, g, b)",
    "Else": "Else",
    "EndIf": "EndIf",
    "WaitSeconds": "WaitSeconds(number_of_seconds)",
    "WaitForKeyboard": "WaitForKeyboard(keyname)",
    "WaitForPixel": "WaitForPixel(x, y, r, g, b)",
    "MouseDown": "MouseDown(left)",
    "MouseUp": "MouseUp(left)",
    "MoveMouseTo": "MoveMouseTo(x, y)",
    "ClickMouse": "ClickMouse(left)",
    "MoveAndClickMouse": "MoveAndClickMouse(x, y, left)",
    "ClickOnKeyboard": "ClickOnKeyboard(keyname)",
    "KeyDown": "KeyDown(keyname)",
    "KeyUp": "KeyUp(keyname)",
    "WriteText": "WriteText(text)",
    "Macro": "Macro(macro_name)",
}


def is_key_on_keyboard(name):
    return name in pyautogui.KEYBOARD_KEYS


def is_number(text):
    try:
        float(text)
        return True
    except (TypeError, ValueError):
        return False
