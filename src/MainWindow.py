import webbrowser
import os
from datetime import timedelta

from gen.MainWindow import Ui_MainWindow
from osutils import app_version
from permissions import Permissions
from AppDb import App
from translations import tr

from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.permissions = Permissions.instance()

        self.ui.label_2.linkActivated.connect(self.open_family_rules_website)

        self.check_permissions()

        self.ui.retranslateUi(self)

        # This must be done after retranslateUi!
        self.update_family_rules_link_with_version()

    def update_family_rules_link_with_version(self):
        """Update the FamilyRules link to include version number"""
        version = app_version()
        link_text = f"[FamilyRules {version}](https://familyrules.org)"
        self.ui.label_2.setText(link_text)

    def open_family_rules_website(self, link):
        """Open the FamilyRules website in the default browser"""
        webbrowser.open(link)

    def update_screen_time(self, time: timedelta):
        self.ui.screen_time_label.setText(str(time))

    def update_applications_usage(self, apps: list[tuple[App, timedelta]]):
        self.ui.table.setHorizontalHeaderLabels([tr("Icon"), tr("Application"), tr("Runtime")])
        self.ui.table.setRowCount(len(apps))
        self.ui.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.ui.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.ui.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        for i, (app, time) in enumerate(apps):
            # Icon column
            icon_item = QTableWidgetItem()
            if app.icon_path and os.path.exists(app.icon_path):
                pixmap = QPixmap(app.icon_path)
                if not pixmap.isNull():
                    # Scale the icon to a reasonable size (32x32)
                    scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_item.setIcon(QIcon(scaled_pixmap))
            self.ui.table.setItem(i, 0, icon_item)
            
            # Application name column
            item_name = QTableWidgetItem(f"{app.app_name} - {app.app_path}")
            self.ui.table.setItem(i, 1, item_name)
            
            # Runtime column
            item_duration = QTableWidgetItem(str(time))
            self.ui.table.setItem(i, 2, item_duration)

    def check_permissions(self):
        if self.permissions.all_granted():
            self.ui.permissionWarningLabel.setVisible(False)
            self.ui.grantPermissionButton.setVisible(False)
            # Set layout height to 0 to remove blank space
            self.ui.permissionWarningLayout.setContentsMargins(0, 0, 0, 0)
            self.ui.permissionWarningLayout.setSpacing(0)
        else:
            self.ui.permissionWarningLabel.setVisible(True)
            self.ui.grantPermissionButton.setVisible(True)
            # Restore normal margins and spacing
            self.ui.permissionWarningLayout.setContentsMargins(12, 8, 12, 8)
            self.ui.permissionWarningLayout.setSpacing(0)

            first_missing_permission = self.permissions.get_missing_permissions()[0]
            warning_text = tr("Missing permission")
            self.ui.permissionWarningLabel.setText(f"{warning_text}: {first_missing_permission.name}")
            self.ui.grantPermissionButton.clicked.connect(lambda: first_missing_permission.grant())
