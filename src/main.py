import sys

from PySide6.QtWidgets import QApplication

from config import APP_NAME, APP_VERSION
from domain.settings_store import SettingsStore
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    store = SettingsStore()
    window = MainWindow(store)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())