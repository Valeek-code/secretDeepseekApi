from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QMenu

from services.project_service import list_children


class ProjectTree(QWidget):
    set_main_requested = Signal(str)
    open_file_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(12)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self.tree, 1)

        self._project_root: Path | None = None
        self._main_file: str | None = None

    def clear(self) -> None:
        self.tree.clear()
        self._project_root = None
        self._main_file = None

    def load_project(self, project_root: Path, main_file: str | None) -> None:
        self.tree.clear()
        self._project_root = project_root
        self._main_file = main_file
        root_item = self._build_item(project_root, project_root.name or str(project_root))
        self.tree.addTopLevelItem(root_item)
        root_item.setExpanded(True)

    def set_main_file(self, main_file: str | None) -> None:
        self._main_file = main_file
        self._refresh_main_marks()

    def _build_item(self, path: Path, label: str) -> QTreeWidgetItem:
        item = QTreeWidgetItem([label])
        item.setData(0, Qt.UserRole, str(path))
        if path.is_dir():
            for child in list_children(path):
                child_item = self._build_item(child, child.name)
                item.addChild(child_item)
        else:
            self._apply_file_style(item, path)
        return item

    def _apply_file_style(self, item: QTreeWidgetItem, path: Path) -> None:
        if self._is_main(path):
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
            item.setForeground(0, Qt.GlobalColor.cyan)
            item.setText(0, f"{path.name}  ● main")

    def _is_main(self, path: Path) -> bool:
        if not self._project_root or not self._main_file:
            return False
        try:
            rel = path.resolve().relative_to(self._project_root.resolve())
        except ValueError:
            return False
        return str(rel).replace("\\", "/") == self._main_file.replace("\\", "/")

    def _refresh_main_marks(self) -> None:
        root = self.tree.topLevelItem(0)
        if root is None:
            return
        self._walk_and_remark(root)

    def _walk_and_remark(self, item: QTreeWidgetItem) -> None:
        path_str = item.data(0, Qt.UserRole)
        if path_str:
            path = Path(path_str)
            if path.is_file():
                font = item.font(0)
                font.setBold(False)
                item.setFont(0, font)
                item.setForeground(0, Qt.GlobalColor.white)
                item.setText(0, path.name)
                if self._is_main(path):
                    self._apply_file_style(item, path)
        for i in range(item.childCount()):
            self._walk_and_remark(item.child(i))

    def _on_context_menu(self, pos) -> None:
        item = self.tree.itemAt(pos)
        if item is None or self._project_root is None:
            return
        path_str = item.data(0, Qt.UserRole)
        if not path_str:
            return
        path = Path(path_str)
        if not path.is_file():
            return

        menu = QMenu(self)
        open_action = QAction("Открыть содержимое", self)
        open_action.triggered.connect(lambda: self._emit_open_file(path))
        menu.addAction(open_action)

        make_main = QAction("Сделать main-файлом", self)
        make_main.triggered.connect(lambda: self._emit_set_main(path))
        menu.addAction(make_main)

        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def _emit_set_main(self, path: Path) -> None:
        if not self._project_root:
            return
        try:
            rel = path.resolve().relative_to(self._project_root.resolve())
        except ValueError:
            return
        self.set_main_requested.emit(str(rel).replace("\\", "/"))

    def _emit_open_file(self, path: Path) -> None:
        if not self._project_root:
            return
        try:
            rel = path.resolve().relative_to(self._project_root.resolve())
        except ValueError:
            return
        self.open_file_requested.emit(str(rel).replace("\\", "/"))