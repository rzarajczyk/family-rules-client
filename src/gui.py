import os
from datetime import timedelta

from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QApplication, QSystemTrayIcon, QMenu, QVBoxLayout, QLabel, QMainWindow, \
    QTableWidgetItem, QHeaderView, QMessageBox, QLayout

from Installer import Installer, ServerLoginStatus
from actions import LockSystem
from gen.InitialSetup import Ui_InitialSetup
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


class InitialSetupWorker(QThread):
    result_ready = Signal(list)

    def __init__(self, basedir, server, username, password, instance):
        super().__init__()
        self.basedir = basedir
        self.instance = instance
        self.password = password
        self.username = username
        self.server = server

    def run(self):
        response = Installer.do_server_login(self.server, self.username, self.password, self.instance)
        if response.status == ServerLoginStatus.OK:
            Installer.save_settings(self.server, self.username, self.instance, response.token)
            Installer.install_autorun(self.basedir)
            self.result_ready.emit([True,""])
        else:
            self.result_ready.emit([False, response.message])


class InitialSetup(QMainWindow):
    def __init__(self, basedir):
        super().__init__()
        self.basedir = basedir
        self.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.ui = Ui_InitialSetup()
        self.ui.setupUi(self)
        self.ui.progressBar.setHidden(True)
        self.ui.installButton.clicked.connect(self.install)

    def install(self):
        self.ui.progressBar.show()
        self.ui.installButton.setDisabled(True)
        self.ui.serverInput.setDisabled(True)
        self.ui.usernameInput.setDisabled(True)
        self.ui.passwordInput.setDisabled(True)
        self.ui.instanceName.setDisabled(True)

        server = self.ui.serverInput.text()
        username = self.ui.usernameInput.text()
        password = self.ui.passwordInput.text()
        instance = self.ui.instanceName.text()
        self.worker = InitialSetupWorker(self.basedir, server, username, password, instance)
        self.worker.result_ready.connect(self.done)
        self.worker.start()

    def done(self, result):
        msg_box = QMessageBox()
        success = result[0]
        message = result[1]
        if success:
            msg_box.setWindowTitle("Instalacja zakończona")
            msg_box.setText(f"Instalacja zakończona. Uruchom aplikację ponownie.")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(self.finish_close)
        else:
            msg_box.setWindowTitle("Niepowodzenie")
            msg_box.setText(f"Sprawdź poprawność danych i spróbuj ponownie.\n\n" + message)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(self.finish)
        msg_box.exec()

    def finish_close(self):
        self.finish()
        self.close()

    def finish(self):
        self.ui.progressBar.hide()
        self.ui.installButton.setDisabled(False)
        self.ui.serverInput.setDisabled(False)
        self.ui.usernameInput.setDisabled(False)
        self.ui.passwordInput.setDisabled(False)
        self.ui.instanceName.setDisabled(False)


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
    def __init__(self, basedir, argv):
        self.basedir = basedir
        self.app = QApplication(argv)
        self.dont_gc = []

    def setup_initial_setup_ui(self):
        self.installer_window = InitialSetup(self.basedir)
        self.installer_window.show()

    def setup_main_ui(self, tick_interval_ms: int, tick_function):
        self.app.setQuitOnLastWindowClosed(False)

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
            self.dont_gc += [action]
            return action

        add_menu_item("Show", self.main_window.show)
        add_menu_item("Lock screen", lambda: LockSystem().execute(self))
        # add_menu_item("Block screen", lambda: BlockAccess().execute(self))
        # add_menu_item("Kill Notes.ap", lambda: KillApplication("Notes.app").execute(self))
        add_menu_item("Quit", self.app.quit)

        tray_icon.setContextMenu(tray_menu)

        tray_icon.show()

        def tick():
            tick_function(self)

        tick()
        # Set up a timer to show the window every 10 seconds
        timer = QTimer()
        timer.timeout.connect(tick)
        timer.start(tick_interval_ms)

        self.dont_gc += [
            tray_icon, tray_menu, timer
        ]

    def run(self):
        return self.app.exec()
