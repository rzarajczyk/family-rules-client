# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingsWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QMainWindow, QProgressBar,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow):
        if not SettingsWindow.objectName():
            SettingsWindow.setObjectName(u"SettingsWindow")
        SettingsWindow.resize(526, 146)
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
        self.closeButton.setText(QCoreApplication.translate("SettingsWindow", u"Close", None))
    # retranslateUi

