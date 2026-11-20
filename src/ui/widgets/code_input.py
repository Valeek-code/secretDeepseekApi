from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout


class CodeInput(QWidget):
    text_changed_debounced = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Вставь raw-код из промпта сюда…")
        layout.addWidget(self.editor, 1)

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)
        self._debounce.timeout.connect(self._emit_debounced)
        self.editor.textChanged.connect(self._debounce.start)

    def _emit_debounced(self) -> None:
        self.text_changed_debounced.emit(self.editor.toPlainText())

    def text(self) -> str:
        return self.editor.toPlainText()

    def set_text(self, value: str) -> None:
        self.editor.setPlainText(value)
