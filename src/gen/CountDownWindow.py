# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CountDownWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QSizePolicy,
    QWidget)

class Ui_CountDownWindow(object):
    def setupUi(self, CountDownWindow):
        if not CountDownWindow.objectName():
            CountDownWindow.setObjectName(u"CountDownWindow")
        CountDownWindow.resize(155, 83)
        self.gridLayout = QGridLayout(CountDownWindow)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(CountDownWindow)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(50)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.retranslateUi(CountDownWindow)

        QMetaObject.connectSlotsByName(CountDownWindow)
    # setupUi

    def retranslateUi(self, CountDownWindow):
        CountDownWindow.setWindowTitle(QCoreApplication.translate("CountDownWindow", u"Form", None))
        self.label.setText(QCoreApplication.translate("CountDownWindow", u"50", None))
    # retranslateUi

