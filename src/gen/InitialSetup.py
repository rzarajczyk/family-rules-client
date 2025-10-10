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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QMainWindow, QProgressBar, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_InitialSetup(object):
    def setupUi(self, InitialSetup):
        if not InitialSetup.objectName():
            InitialSetup.setObjectName(u"InitialSetup")
        InitialSetup.resize(800, 322)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(InitialSetup.sizePolicy().hasHeightForWidth())
        InitialSetup.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(InitialSetup)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.serverInput = QLineEdit(self.groupBox)
        self.serverInput.setObjectName(u"serverInput")

        self.gridLayout.addWidget(self.serverInput, 0, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.usernameInput = QLineEdit(self.groupBox)
        self.usernameInput.setObjectName(u"usernameInput")

        self.gridLayout.addWidget(self.usernameInput, 1, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.passwordInput = QLineEdit(self.groupBox)
        self.passwordInput.setObjectName(u"passwordInput")
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.passwordInput, 2, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.instanceName = QLineEdit(self.groupBox_2)
        self.instanceName.setObjectName(u"instanceName")

        self.gridLayout_2.addWidget(self.instanceName, 0, 1, 1, 1)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_2.addWidget(self.label_7, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_2)

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
        self.label.setText(QCoreApplication.translate("InitialSetup", u"Family Rules Installation", None))
        self.groupBox.setTitle(QCoreApplication.translate("InitialSetup", u"Server Data", None))
        self.label_2.setText(QCoreApplication.translate("InitialSetup", u"Server URL:", None))
        self.serverInput.setText(QCoreApplication.translate("InitialSetup", u"https://familyrules.org", None))
        self.label_3.setText(QCoreApplication.translate("InitialSetup", u"Username:", None))
        self.label_4.setText(QCoreApplication.translate("InitialSetup", u"Password:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("InitialSetup", u"This Computer Data", None))
        self.label_7.setText(QCoreApplication.translate("InitialSetup", u"Name this computer:", None))
        self.installButton.setText(QCoreApplication.translate("InitialSetup", u"Install!", None))
    # retranslateUi

