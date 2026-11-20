from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget


class RussiaFlag(QWidget):
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h // 3, QColor("#ffffff"))
        painter.fillRect(0, h // 3, w, h // 3, QColor("#0039a6"))
        painter.fillRect(0, 2 * h // 3, w, h // 3, QColor("#d52b1e"))


class EasterEggDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("…")
        self.setFixedSize(360, 260)
        layout = QVBoxLayout(self)
        flag = RussiaFlag()
        flag.setFixedHeight(90)
        layout.addWidget(flag)
        self.label = QLabel("Россия, путин, победа")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: 700; color: #ffffff;")
        layout.addWidget(self.label)
        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._blink)
        self._visible = True
        self._timer.start()

    def _blink(self) -> None:
        self._visible = not self._visible
        self.label.setVisible(self._visible)
