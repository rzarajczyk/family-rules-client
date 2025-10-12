import logging
from enum import Enum, auto
import pygame

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QApplication

from gen.CountDownWindow import Ui_CountDownWindow
from guiutils import show_on_all_desktops, set_window_above_fullscreen
from osutils import get_os, SupportedOs
from basedir import Basedir


class CountDownState(Enum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    DONE = auto()


class CountDownWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CountDownWindow()
        self.ui.setupUi(self)
        
        # Retranslate UI after setup
        self.ui.retranslateUi(self)
        
        match get_os():
            case SupportedOs.MAC_OS:
                self.setWindowFlags(
                    Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
                )
            case SupportedOs.WINDOWS:
                self.setWindowFlags(
                    Qt.Tool | Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
                )
            case _:
                raise Exception("Unsupported operating system")
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.width() - self.width(), 0)
        show_on_all_desktops(self)
        set_window_above_fullscreen(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.amount_seconds = 0
        self.onTimeout = lambda *args: None
        self.state = CountDownState.NOT_STARTED
        self.name = None

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        self.tick_sound = pygame.mixer.Sound(str(Basedir.get() / 'resources' / 'tick.wav'))

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

    def hide(self):
        super().hide()

    def show(self):
        super().show()
    
    def _play_tick_sound(self):
        try:
            self.tick_sound.play()
        except Exception as e:
            logging.warning("Unable to play a sound: %s", e)

    # def paintEvent(self, event):
    #     # This method is used to paint the window with a transparent background
    #     painter = QPainter(self)
    #     painter.setCompositionMode(QPainter.CompositionMode_Clear)
    #     painter.fillRect(self.rect(), Qt.transparent)
    #     painter.end()

    def tick(self):
        if self.state.value == CountDownState.IN_PROGRESS.value:
            # Play tick sound
            self._play_tick_sound()
            
            self.ui.label.setText(
                "<div style=\"background-color: yellow; color: red;\">" + str(self.amount_seconds) + "</div>")
            self.amount_seconds -= 1
            if self.amount_seconds <= 0:
                self.amount_seconds = 0
                self.state = CountDownState.DONE
                self.onTimeout()
