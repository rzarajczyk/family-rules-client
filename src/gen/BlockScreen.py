# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'BlockScreen.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QSizePolicy,
    QWidget)

class Ui_BlockScreen(object):
    def setupUi(self, BlockScreen):
        if not BlockScreen.objectName():
            BlockScreen.setObjectName(u"BlockScreen")
        BlockScreen.resize(701, 710)
        self.gridLayout = QGridLayout(BlockScreen)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(BlockScreen)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.retranslateUi(BlockScreen)

        QMetaObject.connectSlotsByName(BlockScreen)
    # setupUi

    def retranslateUi(self, BlockScreen):
        BlockScreen.setWindowTitle(QCoreApplication.translate("BlockScreen", u"Screen blocked", None))
        self.label.setText(QCoreApplication.translate("BlockScreen", u"<b>test</b>", None))
    # retranslateUi

