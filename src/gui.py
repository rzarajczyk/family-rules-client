import os
from datetime import timedelta

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow, \
    QTableWidgetItem, QHeaderView, QMessageBox, QLayout

from Installer import Installer, RegisterInstanceStatus
from UptimeDb import UptimeDb, UsageUpdate
from gen.InitialSetup import Ui_InitialSetup
from gen.MainWindow import Ui_MainWindow
from gui_block import BlockScreenWindow
from gui_countdown import CountDownWindow
from gui_settings import SettingsWindow
from osutils import is_dist
from basedir import Basedir


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

    def __init__(self, server, username, password, instance):
        super().__init__()
        self.instance_name = instance
        self.password = password
        self.username = username
        self.server = server

    def run(self):
        response = Installer.install(self.server, self.username, self.password, self.instance_name)
        if response.status == RegisterInstanceStatus.OK:
            Installer.save_settings(self.server, self.username, response.instance_id, self.instance_name, response.token)
            Installer.install_autorun()
            self.result_ready.emit([True, ""])
        else:
            match response.status:
                case RegisterInstanceStatus.ILLEGAL_INSTANCE_NAME:
                    message = "Nieprawidłowa nazwa tego komputera"
                case RegisterInstanceStatus.INSTANCE_ALREADY_EXISTS:
                    message = "Komputer o takiej nazwie już został zarejestrowany"
                case RegisterInstanceStatus.HOST_NOT_REACHABLE:
                    message = "Brak połączenia z serwerem"
                case RegisterInstanceStatus.INVALID_PASSWORD:
                    message = "Nieprawidłowa nazwa użytkownika lub hasło"
                case RegisterInstanceStatus.SERVER_ERROR:
                    message = "Serwer zwrócił błąd"
                case _:
                    message = f"Wykryto nieznany błąd: {response.status}"
            if response.message is not None:
                message += f"\n\n{message}"
            self.result_ready.emit([False, message])


class InitialSetup(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.worker = InitialSetupWorker(server, username, password, instance)
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


class Gui:
    def __init__(self, argv):
        self.app = QApplication(argv)
        self.dont_gc = []
        self.tick_count: int = 0

    def setup_initial_setup_ui(self):
        self.installer_window = InitialSetup()
        self.installer_window.show()

    def setup_main_ui(self,
                      uptime_tick_interval_ms: int,
                      uptime_tick_function,
                      report_tick_interval_ms: int,
                      report_tick_function
                      ):
        self.app.setQuitOnLastWindowClosed(False)

        # self.top_wight_window = TopRightWindow()
        self.block_access_window = BlockScreenWindow()
        self.main_window = MainWindow()
        self.settings_window = SettingsWindow()
        self.count_down_window = CountDownWindow()

        tray_icon = QSystemTrayIcon()
        tray_icon.setIcon(QIcon(os.path.join(Basedir.get_str(), "resources", "icon.png" if is_dist() else "icon-dev.png")))

        tray_menu = QMenu()

        def add_menu_item(name, signal):
            action = QAction(name)
            action.triggered.connect(signal)
            tray_menu.addAction(action)
            self.dont_gc += [action]
            return action

        def show_main_window():
            if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
                self.settings_window.show()
            else:
                self.main_window.show()

        add_menu_item("Show", show_main_window)
        # add_menu_item("Countdown", lambda: self.count_down_window.start(10, lambda: print("done")))
        # add_menu_item("Lock screen", lambda: self.block_access_window.show())
        # add_menu_item("Kill Notes.ap", lambda: KillApplication("Notes.app").execute(self))
        if not is_dist():
            add_menu_item("Quit", self.app.quit)

        tray_icon.setContextMenu(tray_menu)

        tray_icon.show()

        db = UptimeDb()

        def uptime_tick():
            usage_update: UsageUpdate = uptime_tick_function()
            absolute_usage = db.update(usage_update)
            self.main_window.update_screen_time(absolute_usage.screen_time)
            self.main_window.update_applications_usage(absolute_usage.applications)

        def report_tick():
            usage = db.get()
            report_tick_function(self, usage)

        uptime_tick()
        uptime_timer = QTimer()
        uptime_timer.timeout.connect(uptime_tick)
        uptime_timer.start(uptime_tick_interval_ms)

        report_tick()
        report_timer = QTimer()
        report_timer.timeout.connect(report_tick)
        report_timer.start(report_tick_interval_ms)

        self.dont_gc += [
            tray_icon, tray_menu, uptime_timer, report_timer, db
        ]

    def run(self):
        return self.app.exec()
