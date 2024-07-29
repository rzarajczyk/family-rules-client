# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ParentConfirm.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QGroupBox, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_ParentConfirm(object):
    def setupUi(self, ParentConfirm):
        if not ParentConfirm.objectName():
            ParentConfirm.setObjectName(u"ParentConfirm")
        ParentConfirm.resize(397, 165)
        self.verticalLayout = QVBoxLayout(ParentConfirm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(ParentConfirm)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.password = QLineEdit(self.groupBox)
        self.password.setObjectName(u"password")

        self.gridLayout.addWidget(self.password, 0, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.username = QLineEdit(self.groupBox)
        self.username.setObjectName(u"username")
        self.username.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.username, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.buttonBox = QDialogButtonBox(ParentConfirm)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ParentConfirm)
        self.buttonBox.accepted.connect(ParentConfirm.accept)
        self.buttonBox.rejected.connect(ParentConfirm.reject)

        QMetaObject.connectSlotsByName(ParentConfirm)
    # setupUi

    def retranslateUi(self, ParentConfirm):
        ParentConfirm.setWindowTitle(QCoreApplication.translate("ParentConfirm", u"Confirm", None))
        self.groupBox.setTitle(QCoreApplication.translate("ParentConfirm", u"Enter your credentials to continue", None))
        self.label.setText(QCoreApplication.translate("ParentConfirm", u"Username", None))
        self.label_2.setText(QCoreApplication.translate("ParentConfirm", u"Password", None))
    # retranslateUi

