"""BotMaker entry point. Single long-running process; screens are swapped
in-place by app.Navigator instead of each screen being a separate subprocess."""
import config
from app import AppContext, build_root
from models.project import ProjectRepo
from ui.screens.project_list import ProjectListScreen


def main():
    config.ensure_app_data_dir()
    root = build_root()
    ctx = AppContext(root, ProjectRepo())
    ctx.navigator.go_to(ProjectListScreen)
    root.mainloop()


if __name__ == "__main__":
    main()
