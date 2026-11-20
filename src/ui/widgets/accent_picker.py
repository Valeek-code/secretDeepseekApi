from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider


class HsvWheel(QWidget):
    color_changed = Signal(QColor)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self._hue = 0
        self._sat = 255
        self._val = 255
        self._ring = self._build_ring()

    def _build_ring(self):
        from PySide6.QtGui import QImage
        size = 180
        img = QImage(size, size, QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        cx, cy = size / 2, size / 2
        outer = size / 2 - 2
        inner = outer - 24
        for y in range(size):
            for x in range(size):
                dx, dy = x - cx, y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if inner <= dist <= outer:
                    import math
                    hue = int((math.degrees(math.atan2(dy, dx)) + 360) % 360)
                    color = QColor.fromHsv(hue, 255, 255)
                    img.setPixelColor(x, y, color)
        return img

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawImage(0, 0, self._ring)
        center = QColor.fromHsv(self._hue, self._sat, self._val)
        painter.setBrush(center)
        painter.setPen(QPen(Qt.white, 2))
        painter.drawEllipse(self.rect().center(), 24, 24)

    def mousePressEvent(self, event) -> None:
        self._update_from_pos(event.position().toPoint())

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.LeftButton:
            self._update_from_pos(event.position().toPoint())

    def _update_from_pos(self, pos) -> None:
        import math
        cx, cy = self.width() / 2, self.height() / 2
        dx, dy = pos.x() - cx, pos.y() - cy
        hue = int((math.degrees(math.atan2(dy, dx)) + 360) % 360)
        self._hue = hue
        self.color_changed.emit(QColor.fromHsv(self._hue, self._sat, self._val))
        self.update()

    def set_color(self, color: QColor) -> None:
        self._hue = max(0, color.hue())
        self._sat = color.saturation()
        self._val = color.value()
        self.update()


class AccentPicker(QWidget):
    accent_changed = Signal(QColor)
    preset_clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        presets = QHBoxLayout()
        self.btn_white = QPushButton("Белый")
        self.btn_blue = QPushButton("Синий")
        self.btn_red = QPushButton("Красный")
        self.btn_white.clicked.connect(lambda: self._on_preset("white"))
        self.btn_blue.clicked.connect(lambda: self._on_preset("blue"))
        self.btn_red.clicked.connect(lambda: self._on_preset("red"))
        presets.addWidget(self.btn_white)
        presets.addWidget(self.btn_blue)
        presets.addWidget(self.btn_red)
        layout.addLayout(presets)

        wheel_row = QHBoxLayout()
        self.wheel = HsvWheel()
        self.wheel.color_changed.connect(self._on_wheel)
        wheel_row.addWidget(self.wheel)

        sliders = QVBoxLayout()
        self.sat_slider = QSlider(Qt.Horizontal)
        self.sat_slider.setRange(0, 255)
        self.sat_slider.setValue(255)
        self.sat_slider.valueChanged.connect(self._on_sliders)
        self.val_slider = QSlider(Qt.Horizontal)
        self.val_slider.setRange(0, 255)
        self.val_slider.setValue(255)
        self.val_slider.valueChanged.connect(self._on_sliders)
        sliders.addWidget(QLabel("Насыщенность"))
        sliders.addWidget(self.sat_slider)
        sliders.addWidget(QLabel("Яркость"))
        sliders.addWidget(self.val_slider)
        wheel_row.addLayout(sliders)
        layout.addLayout(wheel_row)

        self.preview = QLabel()
        self.preview.setFixedHeight(28)
        self.preview.setStyleSheet("border-radius: 6px; border: 1px solid #3a3a3a;")
        layout.addWidget(self.preview)

        self._current = QColor("#6cb6ff")
        self._update_preview(self._current)

    def _on_preset(self, name: str) -> None:
        from domain.settings_store import ACCENT_PRESETS
        color = QColor(ACCENT_PRESETS[name])
        self._current = color
        self.wheel.set_color(color)
        self._update_preview(color)
        self.preset_clicked.emit(name)
        self.accent_changed.emit(color)

    def _on_wheel(self, color: QColor) -> None:
        self._current = color
        self._update_preview(color)
        self.accent_changed.emit(color)

    def _on_sliders(self) -> None:
        color = QColor.fromHsv(self.wheel._hue, self.sat_slider.value(), self.val_slider.value())
        self._current = color
        self.wheel.set_color(color)
        self._update_preview(color)
        self.accent_changed.emit(color)

    def _update_preview(self, color: QColor) -> None:
        self.preview.setStyleSheet(
            f"background-color: {color.name()}; border-radius: 6px; border: 1px solid #3a3a3a;"
        )

    def current_color(self) -> QColor:
        return self._current