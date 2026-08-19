"""App-wide paths and constants."""
import os

APP_NAME = "BotMaker"

APP_DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
PROJECTS_INDEX_FILE = os.path.join(APP_DATA_DIR, "botmaker.json")

PROJECT_FILE_NAME = "project.json"
CODE_FILE_NAME = "code.dsl"
MACROS_DIR_NAME = "Macros"

SCHEMA_VERSION = 1

VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt")
GITHUB_REPO_URL = "https://github.com/123Maciek/BotMaker"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/123Maciek/BotMaker/main/version.txt"


def ensure_app_data_dir():
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    return APP_DATA_DIR
