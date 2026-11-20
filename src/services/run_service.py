import shutil
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal


class RunService(QObject):
    output_ready = Signal(str)
    finished = Signal(int)
    failed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process: QProcess | None = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.state() != QProcess.NotRunning

    def poetry_available(self) -> bool:
        return shutil.which("poetry") is not None

    def start(self, project_root: Path, main_file: str) -> None:
        if self.is_running():
            self.failed.emit("Процесс уже запущен")
            return
        if not self.poetry_available():
            self.failed.emit("poetry не найден в PATH")
            return

        self._process = QProcess(self)
        self._process.setWorkingDirectory(str(project_root))
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.finished.connect(self._on_finished)
        self._process.errorOccurred.connect(self._on_error)

        args = ["run", "python", main_file]
        self.output_ready.emit(f"$ poetry {' '.join(args)}\n")
        self._process.start("poetry", args)

    def _on_stdout(self) -> None:
        if not self._process:
            return
        data = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if data:
            self.output_ready.emit(data)

    def _on_finished(self, code: int, _status) -> None:
        self._process = None
        self.finished.emit(code)

    def _on_error(self, error) -> None:
        self._process = None
        if error == QProcess.FailedToStart:
            self.failed.emit("Не удалось запустить poetry. Проверь, что poetry в PATH.")
        else:
            self.failed.emit(f"Ошибка процесса: {error}")