from enum import Enum, auto

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QApplication

from gen.CountDownWindow import Ui_CountDownWindow
from guiutils import show_on_all_desktops


class CountDownState(Enum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    DONE = auto()


class CountDownWindow(QWidget):
    def __init__(self, basedir):
        super().__init__()
        self.ui = Ui_CountDownWindow()
        self.ui.setupUi(self)
        self.basedir = basedir
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.width() - self.width(), 0)
        show_on_all_desktops(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.amount_seconds = 0
        self.onTimeout = lambda *args: None
        self.state = CountDownState.NOT_STARTED
        self.name = None

    def start(self, initial_amount_seconds: int, name=None, onTimeout=lambda *args: None):
        self.state = CountDownState.IN_PROGRESS
        self.name = name
        self.show()
        self.amount_seconds = initial_amount_seconds
        self.onTimeout = onTimeout
        self.tick()

    def stop_reset(self):
        self.hide()
        self.name = None
        self.amount_seconds = 0
        self.onTimeout = lambda *args: None
        self.state = CountDownState.NOT_STARTED

    # def paintEvent(self, event):
    #     # This method is used to paint the window with a transparent background
    #     painter = QPainter(self)
    #     painter.setCompositionMode(QPainter.CompositionMode_Clear)
    #     painter.fillRect(self.rect(), Qt.transparent)
    #     painter.end()

    def tick(self):
        if self.state.value == CountDownState.IN_PROGRESS.value:
            self.ui.label.setText("<div style=\"background-color: yellow; color: red;\">" + str(self.amount_seconds) + "</div>")
            self.amount_seconds -= 1
            if self.amount_seconds <= 0:
                self.amount_seconds = 0
                self.state = CountDownState.DONE
                self.onTimeout()