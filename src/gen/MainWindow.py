# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(478, 304)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.permissionWarningLayout = QHBoxLayout()
        self.permissionWarningLayout.setObjectName(u"permissionWarningLayout")
        self.permissionWarningLayout.setContentsMargins(12, 8, 12, 8)
        self.permissionWarningLabel = QLabel(self.centralwidget)
        self.permissionWarningLabel.setObjectName(u"permissionWarningLabel")
        self.permissionWarningLabel.setLineWidth(0)

        self.permissionWarningLayout.addWidget(self.permissionWarningLabel)

        self.permissionWarningSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.permissionWarningLayout.addItem(self.permissionWarningSpacer)

        self.grantPermissionButton = QPushButton(self.centralwidget)
        self.grantPermissionButton.setObjectName(u"grantPermissionButton")

        self.permissionWarningLayout.addWidget(self.grantPermissionButton)


        self.gridLayout.addLayout(self.permissionWarningLayout, 1, 0, 1, 3)

        self.table = QTableWidget(self.centralwidget)
        if (self.table.columnCount() < 3):
            self.table.setColumnCount(3)
        self.table.setObjectName(u"table")
        self.table.setSortingEnabled(True)
        self.table.setColumnCount(3)

        self.gridLayout.addWidget(self.table, 2, 0, 1, 3)

        self.screen_time_label = QLabel(self.centralwidget)
        self.screen_time_label.setObjectName(u"screen_time_label")

        self.gridLayout.addWidget(self.screen_time_label, 0, 2, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.ok_button = QPushButton(self.centralwidget)
        self.ok_button.setObjectName(u"ok_button")
        self.ok_button.setMouseTracking(True)

        self.gridLayout.addWidget(self.ok_button, 3, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 3, 1, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_2.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.ok_button.clicked.connect(MainWindow.hide)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Screen Time", None))
        self.permissionWarningLabel.setStyleSheet(QCoreApplication.translate("MainWindow", u"QLabel { color: #d32f2f; font-weight: bold; }", None))
        self.permissionWarningLabel.setText(QCoreApplication.translate("MainWindow", u"Accessibility permission not granted", None))
        self.grantPermissionButton.setText(QCoreApplication.translate("MainWindow", u"Grant Permission", None))
        self.screen_time_label.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Screen Time", None))
        self.ok_button.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"[FamilyRules](https://familyrules.org)", None))
    # retranslateUi

