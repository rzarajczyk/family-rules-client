# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingsWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLabel,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow):
        if not SettingsWindow.objectName():
            SettingsWindow.setObjectName(u"SettingsWindow")
        SettingsWindow.resize(538, 211)
        self.centralwidget = QWidget(SettingsWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.resetButton = QPushButton(self.groupBox)
        self.resetButton.setObjectName(u"resetButton")

        self.verticalLayout_2.addWidget(self.resetButton)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.openAppDataButton = QPushButton(self.groupBox_2)
        self.openAppDataButton.setObjectName(u"openAppDataButton")

        self.verticalLayout_3.addWidget(self.openAppDataButton)

        self.clearAppDbButton = QPushButton(self.groupBox_2)
        self.clearAppDbButton.setObjectName(u"clearAppDbButton")

        self.verticalLayout_3.addWidget(self.clearAppDbButton)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout = QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(-1)

        self.verticalLayout.addWidget(self.progressBar)

        self.closeButton = QPushButton(self.centralwidget)
        self.closeButton.setObjectName(u"closeButton")

        self.verticalLayout.addWidget(self.closeButton)

        SettingsWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SettingsWindow)
        self.closeButton.clicked.connect(SettingsWindow.hide)

        QMetaObject.connectSlotsByName(SettingsWindow)
    # setupUi

    def retranslateUi(self, SettingsWindow):
        SettingsWindow.setWindowTitle(QCoreApplication.translate("SettingsWindow", u"Parent Settings", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingsWindow", u"Uninstall", None))
        self.resetButton.setText(QCoreApplication.translate("SettingsWindow", u"Reset application and remove from autorun", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SettingsWindow", u"Data Management", None))
        self.openAppDataButton.setText(QCoreApplication.translate("SettingsWindow", u"Open App Data Folder", None))
        self.clearAppDbButton.setText(QCoreApplication.translate("SettingsWindow", u"Regenerate App Database", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("SettingsWindow", u"About", None))
        self.label.setText(QCoreApplication.translate("SettingsWindow", u"Author:", None))
        self.label_2.setText(QCoreApplication.translate("SettingsWindow", u"Rafa\u0142 Zarajczyk, <a href=\"https://zarajczyk.pl\">https://zarajczyk.pl</a>", None))
        self.closeButton.setText(QCoreApplication.translate("SettingsWindow", u"Close", None))
    # retranslateUi

