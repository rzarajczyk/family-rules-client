import os
import sys
import webbrowser
from datetime import timedelta

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow, \
    QTableWidgetItem, QHeaderView, QMessageBox, QLayout

from Installer import Installer, RegisterInstanceStatus
from Launcher import Launcher
from UptimeDb import UptimeDb, UsageUpdate
from basedir import Basedir
from gen.InitialSetup import Ui_InitialSetup
from gen.MainWindow import Ui_MainWindow
from gui_block import BlockScreenWindow
from gui_countdown import CountDownWindow
from gui_settings import SettingsWindow
from osutils import is_dist, get_os, SupportedOs
from permissions import (
    check_all_permissions, 
    get_required_permissions, 
    get_permission_name, 
    get_permission_description,
    get_permission_instructions,
    open_permission_settings,
    PermissionStatus,
    PermissionType
)
from translations import tr


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.label_2.linkActivated.connect(self.open_family_rules_website)
        self.ui.grantPermissionButton.clicked.connect(self.grant_permission)
        
        self.check_permissions()
        
        self.ui.retranslateUi(self)

    def open_family_rules_website(self, link):
        """Open the FamilyRules website in the default browser"""
        webbrowser.open(link)

    def update_screen_time(self, time: timedelta):
        self.ui.screen_time_label.setText(str(time))

    def update_applications_usage(self, apps: dict[str, timedelta]):
        self.ui.table.setHorizontalHeaderLabels([tr("Application"), tr("Runtime")])
        self.ui.table.setRowCount(len(apps))
        self.ui.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.ui.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        for i, app in enumerate(apps):
            time = apps[app]
            item_name = QTableWidgetItem(app)
            item_duration = QTableWidgetItem(str(time))
            self.ui.table.setItem(i, 0, item_name)
            self.ui.table.setItem(i, 1, item_duration)

    def check_permissions(self):
        """Check permissions and show/hide the warning widget."""
        permissions = check_all_permissions()
        required_permissions = get_required_permissions()
        
        if not required_permissions:
            # No permissions required for this system
            self.ui.permissionWarningWidget.setVisible(False)
            return
        
        # Check if all permissions are granted
        all_granted = all(status == PermissionStatus.GRANTED for status in permissions.values())
        
        if all_granted:
            # All permissions granted, hide warning
            self.ui.permissionWarningLabel.setVisible(False)
            self.ui.grantPermissionButton.setVisible(False)
        else:
            # Missing permissions, show warning
            self.ui.permissionWarningLabel.setVisible(True)
            self.ui.grantPermissionButton.setVisible(True)
            # Update the warning text to be more specific
            missing_permissions = []
            for perm_type, status in permissions.items():
                if status != PermissionStatus.GRANTED:
                    missing_permissions.append(get_permission_name(perm_type))
            
            if missing_permissions:
                warning_text = tr("Accessibility permission not granted")
                self.ui.permissionWarningLabel.setText(warning_text)

    def grant_permission(self):
        """Attempt to grant the required permission."""
        required_permissions = get_required_permissions()
        permissions = check_all_permissions()
        
        # Find the first permission that's not granted
        for perm_type in required_permissions:
            if permissions.get(perm_type) != PermissionStatus.GRANTED:
                self._handle_permission_grant(perm_type)
                break

    def _handle_permission_grant(self, permission_type: PermissionType):
        """Handle granting a specific permission type."""
        permission_name = get_permission_name(permission_type)
        permission_description = get_permission_description(permission_type)
        instructions = get_permission_instructions(permission_type)
        
        # Try to open system settings first
        if open_permission_settings(permission_type):
            msg_box = QMessageBox()
            msg_box.setWindowTitle(tr("Permission Settings"))
            msg_box.setText(tr("Opening system settings for {permission_name}...").format(permission_name=permission_name))
            msg_box.setInformativeText(tr("Please grant the permission in the system settings that just opened, then click OK to restart the application."))
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.setText(tr("OK - Restart app now"))
            ok_button.clicked.connect(self.restart_application)
            msg_box.exec()
        else:
            # Show manual instructions
            msg_box = QMessageBox()
            msg_box.setWindowTitle(tr("Grant {permission_name}").format(permission_name=permission_name))
            msg_box.setText(tr("To grant {permission_name}:").format(permission_name=permission_name))
            msg_box.setInformativeText(instructions)
            msg_box.setDetailedText(permission_description)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

    def restart_application(self):
        """Restart the application."""
        import subprocess
        import sys
        import os
        
        # Get the current script path
        script_path = os.path.abspath(sys.argv[0])
        
        # Close the current application
        QApplication.quit()
        
        # Start a new instance of the application
        subprocess.Popen([sys.executable, script_path] + sys.argv[1:])
        
        # Exit the current process
        sys.exit(0)


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
        self.setFixedSize(800, 322)
        self.ui.progressBar.setHidden(True)
        self.ui.installButton.clicked.connect(self.install)
        
        # Retranslate UI after setup
        self.ui.retranslateUi(self)

    def install(self):
        self.ui.progressBar.setHidden(False)
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
            msg_box.setWindowTitle(tr("Installation completed"))
            text = tr("Installation completed. ")
            match get_os():
                case SupportedOs.MAC_OS:
                    text += tr("Installation completed. The application will be automatically restarted.")
                case SupportedOs.WINDOWS:
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
        self.block_access_window = BlockScreenWindow()
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

        db = UptimeDb()

        Launcher().run()

        def uptime_tick():
            usage_update: UsageUpdate = uptime_tick_function()
            absolute_usage = db.update(usage_update)
            self.main_window.update_screen_time(absolute_usage.screen_time)
            self.main_window.update_applications_usage(absolute_usage.applications)

        def report_tick(first_run=False):
            usage = db.get()
            report_tick_function(self, usage, first_run)

        uptime_tick()
        uptime_timer = QTimer()
        uptime_timer.timeout.connect(uptime_tick)
        uptime_timer.start(uptime_tick_interval_ms)

        report_tick(first_run=True)
        report_timer = QTimer()
        report_timer.timeout.connect(report_tick)
        report_timer.start(report_tick_interval_ms)

        self.dont_gc += [
            tray_icon, tray_menu, uptime_timer, report_timer, db
        ]

    def run(self):
        return self.app.exec()
