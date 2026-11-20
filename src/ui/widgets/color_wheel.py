import math

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QColor, QConicalGradient, QPainter, QPen, QPixmap, QRadialGradient
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLabel,
    QPushButton,
)


class ColorWheel(QWidget):
    color_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._hue = 200
        self._sat = 200
        self._val = 255
        self._wheel = self._build_wheel()

        self.setMinimumSize(220, 220)
        self.setFixedSize(220, 220)

        self._updating = False

    def _build_wheel(self) -> QPixmap:
        size = 220
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        center = QPoint(size // 2, size // 2)
        for radius in range(size // 2, 0, -1):
            color = QColor.fromHsv(0, 0, 0)
            gradient = QConicalGradient(center, 0)
            for i in range(0, 360, 5):
                gradient.setColorAt(i / 360.0, QColor.fromHsv(i, 255, 255))
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, radius, radius)
        painter.end()
        return pix

    def set_color(self, hex_color: str) -> None:
        color = QColor(hex_color)
        if not color.isValid():
            return
        self._updating = True
        self._hue = color.hue() if color.hue() != -1 else 0
        self._sat = color.saturation()
        self._val = color.value()
        self._updating = False
        self.update()

    def current_color(self) -> str:
        return QColor.fromHsv(self._hue, self._sat, self._val).name()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(0, 0, self._wheel)
        center = QPoint(self.width() // 2, self.height() // 2)
        angle = math.radians(360 - self._hue)
        radius = (self._sat / 255.0) * (self.width() // 2 - 6)
        x = center.x() + radius * math.cos(angle)
        y = center.y() - radius * math.sin(angle)
        pen = QPen(Qt.white, 2)
        painter.setPen(pen)
        painter.drawEllipse(QPoint(int(x), int(y)), 5, 5)

    def mousePressEvent(self, event) -> None:
        self._pick(event.position().toPoint())

    def mouseMoveEvent(self, event) -> None:
        self._pick(event.position().toPoint())

    def _pick(self, point: QPoint) -> None:
        center = QPoint(self.width() // 2, self.height() // 2)
        dx = point.x() - center.x()
        dy = point.y() - center.y()
        dist = math.hypot(dx, dy)
        max_r = self.width() // 2 - 6
        self._sat = int(min(1.0, dist / max_r) * 255)
        angle = math.degrees(math.atan2(-dy, dx))
        if angle < 0:
            angle += 360
        self._hue = int(angle)
        self.update()
        if not self._updating:
            self.color_changed.emit(self.current_color())


class ColorWheelWidget(QWidget):
    color_changed = Signal(str)

    def __init__(self, initial: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.wheel = ColorWheel()
        self.wheel.set_color(initial)
        self.wheel.color_changed.connect(self._on_change)
        layout.addWidget(self.wheel)

        right = QVBoxLayout()
        self.preview = QLabel()
        self.preview.setFixedHeight(28)
        self.preview.setStyleSheet(
            f"background-color: {initial}; border: 1px solid #3a3a3a; border-radius: 6px;"
        )
        right.addWidget(self.preview)

        self.value_slider = QSlider(Qt.Horizontal)
        self.value_slider.setRange(0, 255)
        self.value_slider.setValue(255)
        self.value_slider.valueChanged.connect(self._on_value)
        right.addWidget(QLabel("Яркость"))
        right.addWidget(self.value_slider)
        right.addStretch(1)
        layout.addLayout(right, 1)

    def _on_value(self, value: int) -> None:
        self.wheel._val = value
        self.wheel.update()
        self._on_change(self.wheel.current_color())

    def _on_change(self, hex_color: str) -> None:
        self.preview.setStyleSheet(
            f"background-color: {hex_color}; border: 1px solid #3a3a3a; border-radius: 6px;"
        )
        self.color_changed.emit(hex_color)