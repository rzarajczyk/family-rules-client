import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QApplication, QSystemTrayIcon, QMenu, QVBoxLayout, QLabel

from actions import LockSystem, BlockAccess, KillApplication


class TopRightWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Top Right Window")
        self.setWindowIcon(QIcon("../resources/foaf.png"))  # Replace with your icon path
        self.setFixedSize(200, 100)  # Set the size of the window

        # Center the content inside the window
        layout = QVBoxLayout()
        label = QLabel("This is a small window")
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.move_to_top_right()

    def move_to_top_right(self):
        # Get the screen geometry
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Get the window geometry
        window_width = self.frameGeometry().width()
        window_height = self.frameGeometry().height()

        # Calculate the top-right position
        x = screen_width - window_width
        y = 0

        # Move the window to the top-right corner
        self.move(x, y)


class BlockAccessWindow(QWidget):
    def __init__(self):
        super().__init__()

        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.setWindowTitle("Blokada ekranu!")
        self.setWindowIcon(QIcon("../resources/foaf.png"))  # Replace with your icon path
        self.setFixedSize(screen_width, screen_height)  # Set the size of the window
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint)

        # Center the content inside the window
        layout = QVBoxLayout()
        label = QLabel("Ekran zablokowany")
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
        self.move(0, 0)

    def moveEvent(self, event):
        self.move(0, 0)
        event.ignore()

    def resizeEvent(self, event):
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_height = screen_geometry.height()
        screen_width = screen_geometry.width()
        self.setFixedSize(screen_width, screen_height)
        event.ignore()


class Gui:
    def run(self, tick_interval_ms: int, tick_function, argv):
        app = QApplication(argv)
        app.setQuitOnLastWindowClosed(False)

        top_right_window = TopRightWindow()
        self.top_wight_window = top_right_window

        block_access_window = BlockAccessWindow()
        self.block_access_window = block_access_window

        tray_icon = QSystemTrayIcon()
        tray_icon.setIcon(QIcon("../resources/foaf.png"))

        tray_menu = QMenu()

        def add_menu_item(name, signal):
            action = QAction(name)
            action.triggered.connect(signal)
            tray_menu.addAction(action)
            return action

        show_action = add_menu_item("Show", top_right_window.show)
        lock_action = add_menu_item("Lock screen", lambda: LockSystem().execute(self))
        block_action = add_menu_item("Block screen", lambda: BlockAccess().execute(self))
        kill_action = add_menu_item("Kill Notes.ap", lambda: KillApplication("Notes.app").execute(self))
        quit_action = add_menu_item("Quit", app.quit)

        tray_icon.setContextMenu(tray_menu)

        tray_icon.show()

        def tick():
            tick_function(self)

        # Set up a timer to show the window every 10 seconds
        timer = QTimer()
        timer.timeout.connect(tick)
        timer.start(tick_interval_ms)

        # Start the application event loop
        sys.exit(app.exec())
