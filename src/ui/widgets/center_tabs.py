from pathlib import Path

from PySide6.QtWidgets import (
    QTabBar,
    QTabWidget,
    QPlainTextEdit,
    QWidget,
    QVBoxLayout,
)

from services.project_service import read_text_file
from ui.widgets.code_input import CodeInput


class CenterTabs(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._on_tab_close)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.tabs)

        self.code_input = CodeInput()
        self.tabs.addTab(self.code_input, "Ввод raw")
        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)

    def raw_text(self) -> str:
        return self.code_input.text()

    def set_raw_text(self, value: str) -> None:
        self.code_input.set_text(value)

    def open_file_tab(self, project_root: Path, rel_path: str) -> None:
        target = (project_root / rel_path).resolve()
        try:
            target.relative_to(project_root.resolve())
        except ValueError:
            return

        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)
            if isinstance(widget, QPlainTextEdit) and widget.property("rel_path") == rel_path:
                self.tabs.setCurrentIndex(index)
                return

        ok, content = read_text_file(target)
        viewer = QPlainTextEdit()
        viewer.setReadOnly(True)
        viewer.setProperty("rel_path", rel_path)
        viewer.setPlainText(content if ok else f"// {content}")
        index = self.tabs.addTab(viewer, rel_path)
        self.tabs.setCurrentIndex(index)

    def _on_tab_close(self, index: int) -> None:
        if index == 0:
            return
        self.tabs.removeTab(index)
