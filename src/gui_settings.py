import sys

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog, QMainWindow, QMessageBox

from Installer import Installer
from gen.ParentConfirm import Ui_ParentConfirm
from gen.SettingsWindow import Ui_SettingsWindow


class CheckPasswordWorker(QThread):
    result_ready = Signal(bool)

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
        self.parent_confirm.accepted.connect(self.check_password)
        self.ui.progressBar.setHidden(True)

    def check_password(self):
        self.ui.progressBar.setHidden(False)
        username = self.parent_confirm.ui.username.text()
        password = self.parent_confirm.ui.password.text()
        self.worker = CheckPasswordWorker(username, password)
        self.worker.result_ready.connect(self.uninstall_finished)
        self.worker.start()

    def uninstall_finished(self, status):
        if status:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Uninstall finished")
            msg_box.setText(f"Uninstall finished.")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(lambda : sys.exit(0))
            msg_box.exec()
        else:
            self.ui.progressBar.setHidden(True)
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Uninstall failed")
            msg_box.setText(f"Incorrect credentials.")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(msg_box.close)
            msg_box.exec()
