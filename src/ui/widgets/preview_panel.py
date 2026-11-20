from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
)


class PreviewPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        header = QHBoxLayout()
        title = QLabel("Предпросмотр изменений")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch(1)

        layout.addLayout(header)

        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Здесь появится: добавится / изменится / удалится")
        layout.addWidget(self.preview, 1)

    def set_preview(self, text: str) -> None:
        self.preview.setPlainText(text)
