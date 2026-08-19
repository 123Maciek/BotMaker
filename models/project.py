"""Project model and repository (replaces addproject.py + main.py's projects.txt handling)."""
import os
import re
from dataclasses import dataclass
from pathlib import Path

import config
from models.settings import ProjectSettings
from persistence import json_store

_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')
_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class NameValidationError(ValueError):
    pass


def validate_name(name, min_len=1, max_len=50):
    """Shared name validation for project and macro names.

    Rejects anything that isn't a safe Windows filename component: illegal
    characters, reserved device names, trailing dot/space, and out-of-range length.
    """
    if name is None:
        raise NameValidationError("Name cannot be empty.")
    stripped = name.strip()
    if not (min_len <= len(stripped) <= max_len):
        raise NameValidationError(f"Name must be between {min_len} and {max_len} characters.")
    if stripped != name:
        raise NameValidationError("Name cannot start or end with whitespace.")
    if name.endswith(".") or name.endswith(" "):
        raise NameValidationError("Name cannot end with a dot or space.")
    if _ILLEGAL_CHARS.search(name):
        raise NameValidationError(r'Name cannot contain any of: \ / : * ? " < > |')
    if name.upper().split(".")[0] in _RESERVED_NAMES:
        raise NameValidationError(f'"{name}" is a reserved Windows name.')
    return name


@dataclass
class Project:
    name: str
    root: Path
    settings: ProjectSettings

    @property
    def code_file(self):
        return self.root / config.CODE_FILE_NAME

    @property
    def project_file(self):
        return self.root / config.PROJECT_FILE_NAME

    @property
    def macros_dir(self):
        return self.root / config.MACROS_DIR_NAME

    def to_dict(self):
        return {
            "schema_version": config.SCHEMA_VERSION,
            "name": self.name,
            "settings": self.settings.to_dict(),
        }

    def save(self):
        json_store.write_json(str(self.project_file), self.to_dict())

    @staticmethod
    def load(root: Path):
        root = Path(root)
        data = json_store.read_json(str(root / config.PROJECT_FILE_NAME), default={})
        name = data.get("name", root.name)
        settings = ProjectSettings.from_dict(data.get("settings"))
        return Project(name=name, root=root, settings=settings)


class ProjectRepo:
    """Owns the app-level project index (botmaker.json) and per-project creation/deletion."""

    def __init__(self, index_path=None):
        self.index_path = index_path or config.PROJECTS_INDEX_FILE

    def _read_index(self):
        return json_store.read_json(self.index_path, default=[])

    def _write_index(self, entries):
        json_store.write_json(self.index_path, entries)

    def list_projects(self):
        """Returns Project objects for every entry in the index whose folder still exists.
        Entries pointing at a missing folder are dropped (self-healing, replaces the old
        delete-broken-line-and-restart-parse loop in main.py)."""
        entries = self._read_index()
        projects = []
        changed = False
        kept_entries = []
        for entry in entries:
            root = Path(entry.get("path", ""))
            if root.is_dir() and (root / config.PROJECT_FILE_NAME).is_file():
                projects.append(Project.load(root))
                kept_entries.append(entry)
            else:
                changed = True
        if changed:
            self._write_index(kept_entries)
        return projects

    def create(self, name, parent_dir):
        validate_name(name)
        parent_dir = Path(parent_dir)
        root = parent_dir / name
        if root.exists():
            raise NameValidationError(f'A folder named "{name}" already exists there.')

        os.makedirs(root, exist_ok=True)
        os.makedirs(root / config.MACROS_DIR_NAME, exist_ok=True)
        (root / config.CODE_FILE_NAME).write_text("", encoding="utf-8")

        project = Project(name=name, root=root, settings=ProjectSettings())
        project.save()

        entries = self._read_index()
        entries.append({"name": name, "path": str(root)})
        self._write_index(entries)
        return project

    def delete(self, project: Project):
        import shutil
        entries = [e for e in self._read_index() if Path(e.get("path", "")) != project.root]
        self._write_index(entries)
        if project.root.is_dir():
            shutil.rmtree(project.root, ignore_errors=True)
