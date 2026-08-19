"""Macro model and repository (replaces macros.py's repr()+bracket-substitution
text format and the duplicated slice-based text_to_action parser)."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import config
from models.project import validate_name, Project
from persistence import json_store

# Action "type" values
MOUSE_MOVE = "mouse_move"
MOUSE_DOWN = "mouse_down"
MOUSE_UP = "mouse_up"
KEY_PRESS = "key_press"
KEY_RELEASE = "key_release"


@dataclass
class Action:
    type: str
    t: float  # elapsed seconds since recording started
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[str] = None
    key: Optional[str] = None

    def to_dict(self):
        d = {"type": self.type, "t": self.t}
        if self.x is not None:
            d["x"] = self.x
        if self.y is not None:
            d["y"] = self.y
        if self.button is not None:
            d["button"] = self.button
        if self.key is not None:
            d["key"] = self.key
        return d

    @staticmethod
    def from_dict(d):
        return Action(
            type=d["type"],
            t=d.get("t", 0.0),
            x=d.get("x"),
            y=d.get("y"),
            button=d.get("button"),
            key=d.get("key"),
        )


@dataclass
class Macro:
    name: str
    actions: list = field(default_factory=list)

    def to_dict(self):
        return {
            "schema_version": config.SCHEMA_VERSION,
            "name": self.name,
            "actions": [a.to_dict() for a in self.actions],
        }

    @staticmethod
    def from_dict(data):
        return Macro(
            name=data.get("name", ""),
            actions=[Action.from_dict(a) for a in data.get("actions", [])],
        )


class MacroRepo:
    def __init__(self, project: Project):
        self.project = project

    def _path(self, name):
        return self.project.macros_dir / f"{name}.json"

    def list_names(self):
        macros_dir = self.project.macros_dir
        if not macros_dir.is_dir():
            return []
        return sorted(p.stem for p in macros_dir.glob("*.json"))

    def load(self, name):
        data = json_store.read_json(str(self._path(name)))
        if data is None:
            return None
        return Macro.from_dict(data)

    def save(self, macro: Macro):
        validate_name(macro.name)
        self.project.macros_dir.mkdir(parents=True, exist_ok=True)
        json_store.write_json(str(self._path(macro.name)), macro.to_dict())

    def delete(self, name):
        path = self._path(name)
        if path.is_file():
            path.unlink()
