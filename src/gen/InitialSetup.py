# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'InitialSetup.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QMainWindow, QProgressBar,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_InitialSetup(object):
    def setupUi(self, InitialSetup):
        if not InitialSetup.objectName():
            InitialSetup.setObjectName(u"InitialSetup")
        InitialSetup.resize(798, 274)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(InitialSetup.sizePolicy().hasHeightForWidth())
        InitialSetup.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(InitialSetup)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mainGroupBox = QGroupBox(self.centralwidget)
        self.mainGroupBox.setObjectName(u"mainGroupBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mainGroupBox.sizePolicy().hasHeightForWidth())
        self.mainGroupBox.setSizePolicy(sizePolicy1)
        self.mainGridLayout = QGridLayout(self.mainGroupBox)
        self.mainGridLayout.setObjectName(u"mainGridLayout")
        self.languageLabel = QLabel(self.mainGroupBox)
        self.languageLabel.setObjectName(u"languageLabel")
        self.languageLabel.setMinimumSize(QSize(120, 0))
        self.languageLabel.setMaximumSize(QSize(120, 16777215))

        self.mainGridLayout.addWidget(self.languageLabel, 0, 0, 1, 1)

        self.languageComboBox = QComboBox(self.mainGroupBox)
        self.languageComboBox.addItem("")
        self.languageComboBox.addItem("")
        self.languageComboBox.setObjectName(u"languageComboBox")
        self.languageComboBox.setMinimumSize(QSize(0, 0))

        self.mainGridLayout.addWidget(self.languageComboBox, 0, 1, 1, 1)

        self.label_2 = QLabel(self.mainGroupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(120, 0))
        self.label_2.setMaximumSize(QSize(120, 16777215))

        self.mainGridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.serverInput = QLineEdit(self.mainGroupBox)
        self.serverInput.setObjectName(u"serverInput")
        self.serverInput.setMinimumSize(QSize(0, 0))

        self.mainGridLayout.addWidget(self.serverInput, 1, 1, 1, 1)

        self.label_3 = QLabel(self.mainGroupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(120, 0))
        self.label_3.setMaximumSize(QSize(120, 16777215))

        self.mainGridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.usernameInput = QLineEdit(self.mainGroupBox)
        self.usernameInput.setObjectName(u"usernameInput")
        self.usernameInput.setMinimumSize(QSize(0, 0))

        self.mainGridLayout.addWidget(self.usernameInput, 2, 1, 1, 1)

        self.label_4 = QLabel(self.mainGroupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(120, 0))
        self.label_4.setMaximumSize(QSize(120, 16777215))

        self.mainGridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.passwordInput = QLineEdit(self.mainGroupBox)
        self.passwordInput.setObjectName(u"passwordInput")
        self.passwordInput.setMinimumSize(QSize(0, 0))
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        self.mainGridLayout.addWidget(self.passwordInput, 3, 1, 1, 1)

        self.label_7 = QLabel(self.mainGroupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(120, 0))
        self.label_7.setMaximumSize(QSize(120, 16777215))

        self.mainGridLayout.addWidget(self.label_7, 4, 0, 1, 1)

        self.instanceName = QLineEdit(self.mainGroupBox)
        self.instanceName.setObjectName(u"instanceName")
        self.instanceName.setMinimumSize(QSize(0, 0))

        self.mainGridLayout.addWidget(self.instanceName, 4, 1, 1, 1)


        self.verticalLayout.addWidget(self.mainGroupBox)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.verticalLayout.addWidget(self.progressBar)

        self.installButton = QPushButton(self.centralwidget)
        self.installButton.setObjectName(u"installButton")

        self.verticalLayout.addWidget(self.installButton)

        InitialSetup.setCentralWidget(self.centralwidget)

        self.retranslateUi(InitialSetup)

        QMetaObject.connectSlotsByName(InitialSetup)
    # setupUi

    def retranslateUi(self, InitialSetup):
        InitialSetup.setWindowTitle(QCoreApplication.translate("InitialSetup", u"Family Rules Installation", None))
        self.mainGroupBox.setTitle(QCoreApplication.translate("InitialSetup", u"Installation Settings", None))
        self.languageLabel.setText(QCoreApplication.translate("InitialSetup", u"Language:", None))
        self.languageComboBox.setItemText(0, QCoreApplication.translate("InitialSetup", u"English", None))
        self.languageComboBox.setItemText(1, QCoreApplication.translate("InitialSetup", u"Polski", None))

        self.label_2.setText(QCoreApplication.translate("InitialSetup", u"Server URL:", None))
        self.serverInput.setText(QCoreApplication.translate("InitialSetup", u"https://familyrules.org", None))
        self.label_3.setText(QCoreApplication.translate("InitialSetup", u"Username:", None))
        self.label_4.setText(QCoreApplication.translate("InitialSetup", u"Password:", None))
        self.label_7.setText(QCoreApplication.translate("InitialSetup", u"Computer Name:", None))
        self.installButton.setText(QCoreApplication.translate("InitialSetup", u"Install!", None))
    # retranslateUi

