import sys

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog, QMainWindow, QMessageBox

from Installer import Installer, UnregisterInstanceStatus
from gen.ParentConfirm import Ui_ParentConfirm
from gen.SettingsWindow import Ui_SettingsWindow
from Settings import Settings, UptimeMethod


class CheckPasswordWorker(QThread):
    result_ready = Signal(UnregisterInstanceStatus)

    def __init__(self, username, password):
        super().__init__()
        self.password = password
        self.username = username

    def run(self):
        response = Installer.uninstall(self.username, self.password)
        self.result_ready.emit(response)


class ParentConfirm(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ParentConfirm()
        self.ui.setupUi(self)


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        self.parent_confirm = ParentConfirm()
        self.ui.resetButton.clicked.connect(self.parent_confirm.show)
        self.ui.disableButton.clicked.connect(self.uninstall_autorun)
        self.parent_confirm.accepted.connect(self.check_password)
        self.ui.progressBar.setHidden(True)
        settings = Settings.load()
        match settings.uptime_method:
            case UptimeMethod.PS:
                self.ui.uptimeMethodPs.setChecked(True)
            case UptimeMethod.APPLE_SCREEN_TIME:
                self.ui.uptimeMethodApple.setChecked(True)
        self.ui.buttonGroup.buttonClicked.connect(self.save_uptime_method)

    def save_uptime_method(self):
        settings = Settings.load()
        if self.ui.uptimeMethodPs.isChecked():
            settings.uptime_method = UptimeMethod.PS
        if self.ui.uptimeMethodApple.isChecked():
            settings.uptime_method = UptimeMethod.APPLE_SCREEN_TIME
        Settings.save(settings)

    def uninstall_autorun(self):
        Installer.uninstall_autorun()
        sys.exit(0)

    def check_password(self):
        self.ui.progressBar.setHidden(False)
        username = self.parent_confirm.ui.username.text()
        password = self.parent_confirm.ui.password.text()
        self.worker = CheckPasswordWorker(username, password)
        self.worker.result_ready.connect(self.uninstall_finished)
        self.worker.start()

    def uninstall_finished(self, status):
        if status == UnregisterInstanceStatus.OK:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Uninstall finished")
            msg_box.setText(f"Uninstall finished.")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(lambda: sys.exit(0))
            msg_box.exec()
        else:
            self.ui.progressBar.setHidden(True)
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Uninstall failed")
            msg_box.setText(f"Uninstall failed\n\n{status}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(msg_box.close)
            msg_box.exec()
