import os
import sys
from datetime import timedelta

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QApplication, QSystemTrayIcon, QMenu, QVBoxLayout, QLabel, QMainWindow, \
    QTableWidgetItem, QHeaderView

from actions import LockSystem, BlockAccess, KillApplication
from gen.MainWindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def update_screen_time(self, time: timedelta):
        self.ui.screen_time_label.setText(str(time))

    def update_applications_usage(self, apps: dict[str, timedelta]):
        self.ui.table.setHorizontalHeaderLabels(["Aplikacja", "Czas działania"])
        self.ui.table.setRowCount(len(apps))
        self.ui.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.ui.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        for i, app in enumerate(apps):
            time = apps[app]
            item_name = QTableWidgetItem(app)
            item_duration = QTableWidgetItem(str(time))
            self.ui.table.setItem(i, 0, item_name)
            self.ui.table.setItem(i, 1, item_duration)


class BlockAccessWindow(QWidget):
    def __init__(self):
        super().__init__()

        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.setWindowTitle("Blokada ekranu!")
        self.setFixedSize(screen_width, screen_height)
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
    def __init__(self, basedir):
        self.basedir = basedir

    def run(self, tick_interval_ms: int, tick_function, argv):
        app = QApplication(argv)
        app.setQuitOnLastWindowClosed(False)

        # self.top_wight_window = TopRightWindow()
        self.block_access_window = BlockAccessWindow()
        self.main_window = MainWindow()

        tray_icon = QSystemTrayIcon()
        tray_icon.setIcon(QIcon(os.path.join(self.basedir, "resources", "foaf.png")))

        tray_menu = QMenu()

        def add_menu_item(name, signal):
            action = QAction(name)
            action.triggered.connect(signal)
            tray_menu.addAction(action)
            return action

        show_action = add_menu_item("Show", self.main_window.show)
        lock_action = add_menu_item("Lock screen", lambda: LockSystem().execute(self))
        # block_action = add_menu_item("Block screen", lambda: BlockAccess().execute(self))
        # kill_action = add_menu_item("Kill Notes.ap", lambda: KillApplication("Notes.app").execute(self))
        quit_action = add_menu_item("Quit", app.quit)

        tray_icon.setContextMenu(tray_menu)

        tray_icon.show()

        def tick():
            tick_function(self)

        tick()
        # Set up a timer to show the window every 10 seconds
        timer = QTimer()
        timer.timeout.connect(tick)
        timer.start(tick_interval_ms)

        # Start the application event loop
        sys.exit(app.exec())
