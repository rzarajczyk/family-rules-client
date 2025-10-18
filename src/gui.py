import logging
import os
import sys
from datetime import timedelta

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow, QMessageBox

from Basedir import Basedir
from MultiMonitorBlockScreenManager import MultiMonitorBlockScreenManager
from CountDownWindow import CountDownWindow
from Installer import Installer, RegisterInstanceStatus
from ClientInfoUpdater import ClientInfoUpdater
from SettingsWindow import SettingsWindow
from UptimeDb import UptimeDb, UsageUpdate
from gen.InitialSetup import Ui_InitialSetup
from osutils import is_dist, get_os, OperatingSystem
from AppDb import AppDb
from MainWindow import MainWindow
from translations import tr


class InitialSetupWorker(QThread):
    result_ready = Signal(list)

    def __init__(self, server, username, password, instance, language='en'):
        super().__init__()
        self.instance_name = instance
        self.password = password
        self.username = username
        self.server = server
        self.language = language

    def run(self):
        response = Installer.install(self.server, self.username, self.password, self.instance_name)
        if response.status == RegisterInstanceStatus.OK:
            Installer.save_settings(self.server, self.username, response.instance_id, self.instance_name,
                                    response.token, self.language)
            Installer.install_autorun_with_autorespawn()
            self.result_ready.emit([True, ""])
        else:
            match response.status:
                case RegisterInstanceStatus.ILLEGAL_INSTANCE_NAME:
                    message = tr("Invalid computer name")
                case RegisterInstanceStatus.INSTANCE_ALREADY_EXISTS:
                    message = tr("Computer with this name has already been registered")
                case RegisterInstanceStatus.HOST_NOT_REACHABLE:
                    message = tr("No connection to server")
                case RegisterInstanceStatus.INVALID_PASSWORD:
                    message = tr("Invalid username or password")
                case RegisterInstanceStatus.SERVER_ERROR:
                    message = tr("Server returned an error")
                case _:
                    message = f"{tr('Unknown error detected:')} {response.status}"
            if response.message is not None:
                message += f"\n\n{message}"
            self.result_ready.emit([False, message])


class InitialSetup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_InitialSetup()
        self.ui.setupUi(self)
        # Ensure the window maintains its fixed 800px width
        self.setFixedSize(800, 350)  # Compact height with unified layout
        self.ui.progressBar.setHidden(True)
        self.ui.installButton.clicked.connect(self.install)

        # Set up language selection
        self.ui.languageComboBox.currentIndexChanged.connect(self.on_language_changed)

        # Set initial language selection based on current translation
        from translations import get_translation_manager
        current_lang = get_translation_manager().get_current_language()
        if current_lang == 'pl':
            self.ui.languageComboBox.setCurrentIndex(1)
        else:
            self.ui.languageComboBox.setCurrentIndex(0)

        # Retranslate UI after setup
        self.ui.retranslateUi(self)

    def on_language_changed(self, index):
        """Handle language selection change"""
        from translations import get_translation_manager

        # Map index to language code
        language_codes = ['en', 'pl']
        if 0 <= index < len(language_codes):
            language_code = language_codes[index]

            # Change language
            translation_manager = get_translation_manager()
            if translation_manager.change_language(language_code):
                # Retranslate the UI
                self.ui.retranslateUi(self)
                print(f"Language changed to: {language_code}")

    def install(self):
        self.ui.progressBar.setHidden(False)
        self.ui.installButton.setDisabled(True)
        self.ui.serverInput.setDisabled(True)
        self.ui.usernameInput.setDisabled(True)
        self.ui.passwordInput.setDisabled(True)
        self.ui.instanceName.setDisabled(True)
        self.ui.languageComboBox.setDisabled(True)

        server = self.ui.serverInput.text()
        username = self.ui.usernameInput.text()
        password = self.ui.passwordInput.text()
        instance = self.ui.instanceName.text()

        # Get selected language
        language_codes = ['en', 'pl']
        selected_language = language_codes[self.ui.languageComboBox.currentIndex()]

        self.worker = InitialSetupWorker(server, username, password, instance, selected_language)
        self.worker.result_ready.connect(self.done)
        self.worker.start()

    def done(self, result):
        msg_box = QMessageBox()
        success = result[0]
        message = result[1]
        if success:
            msg_box.setWindowTitle(tr("Installation completed"))
            text = tr("Installation completed. ")
            match get_os():
                case OperatingSystem.MAC_OS:
                    text += tr("Installation completed. The application will be automatically restarted.")
                case OperatingSystem.WINDOWS:
                    text += tr("Installation completed. Restart the application.")
                case _:
                    raise Exception("Unsupported operating system")
            msg_box.setText(text)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(self.finish_close)
        else:
            msg_box.setWindowTitle(tr("Failure"))
            msg_box.setText(f"{tr('Check the data correctness and try again.')}\n\n" + message)
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
        self.ui.languageComboBox.setDisabled(False)
        self.ui.instanceName.setDisabled(False)


class Gui:
    def __init__(self, argv):
        self.app = QApplication.instance()
        if self.app is None:
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
        self.block_access_window = MultiMonitorBlockScreenManager()
        self.main_window = MainWindow()
        self.settings_window = SettingsWindow()
        self.count_down_window = CountDownWindow()

        tray_icon = QSystemTrayIcon()
        tray_icon.setIcon(
            QIcon(os.path.join(Basedir.get_str(), "resources", "icon.png" if is_dist() else "icon-dev.png")))

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
                self.settings_window.raise_()
                self.settings_window.activateWindow()
            else:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()

        add_menu_item(tr("Show"), show_main_window)
        if not is_dist():
            add_menu_item(tr("Quit"), lambda: sys.exit(0))

        def menu_triggered(reason):
            match reason:
                case QSystemTrayIcon.ActivationReason.Trigger:
                    show_main_window()
                case QSystemTrayIcon.ActivationReason.Context:
                    tray_menu.exec(QtGui.QCursor.pos())

        # tray_icon.setContextMenu(tray_menu)
        tray_icon.activated.connect(menu_triggered)
        tray_icon.show()

        uptime_db = UptimeDb()
        app_db = AppDb()

        ClientInfoUpdater.run()

        def launcher_tick():
            """Periodic launcher request every 10 minutes"""
            logging.info("Sending periodic launcher request")
            ClientInfoUpdater.run()

        def uptime_tick():
            usage_update: UsageUpdate = uptime_tick_function()
            absolute_usage = uptime_db.update(usage_update)
            self.main_window.update_screen_time(absolute_usage.screen_time)
            apps: dict[str, timedelta] = absolute_usage.applications
            converted_apps = []
            for app_path, time in apps.items():
                app = app_db[app_path]
                converted_apps.append((app, time))
            self.main_window.update_applications_usage(converted_apps)

        def report_tick(first_run=False):
            usage = uptime_db.get()
            report_tick_function(self, usage, first_run)

        uptime_tick()
        uptime_timer = QTimer()
        uptime_timer.timeout.connect(uptime_tick)
        uptime_timer.start(uptime_tick_interval_ms)

        report_tick(first_run=True)
        report_timer = QTimer()
        report_timer.timeout.connect(report_tick)
        report_timer.start(report_tick_interval_ms)

        # Set up periodic launcher timer (every 10 minutes = 10 * 60 * 1000 ms)
        launcher_timer = QTimer()
        launcher_timer.timeout.connect(launcher_tick)
        launcher_timer.start(10 * 60 * 1000)  # 10 minutes in milliseconds

        self.dont_gc += [
            tray_icon, tray_menu, uptime_timer, report_timer, launcher_timer, uptime_db
        ]

    def run(self):
        return self.app.exec()
