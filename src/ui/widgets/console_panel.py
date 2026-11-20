from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit


class ConsolePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title = QLabel("Консоль")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Вывод запуска main-файла")
        layout.addWidget(self.output, 1)

    def append(self, text: str) -> None:
        self.output.appendPlainText(text)

    def clear(self) -> None:
        self.output.clear()
