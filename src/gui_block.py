import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow

from gen.BlockScreen import Ui_BlockScreen
from guiutils import show_on_all_desktops


class BlockScreenWindow(QWidget):
    def __init__(self, basedir):
        super().__init__()
        self.ui = Ui_BlockScreen()
        self.ui.setupUi(self)
        self.basedir = basedir

        self.ui.label.setPixmap(QPixmap(os.path.join(self.basedir, "resources", "lockscreen.png")))

        self.move(0, 0)
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.setFixedSize(screen_width, screen_height)
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint)
        show_on_all_desktops(self)

    def moveEvent(self, event):
        self.move(0, 0)
        event.ignore()

    def resizeEvent(self, event):
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_height = screen_geometry.height()
        screen_width = screen_geometry.width()
        self.setFixedSize(screen_width, screen_height)
        event.ignore()
