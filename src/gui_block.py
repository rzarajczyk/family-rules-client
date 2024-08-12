import ctypes
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QApplication

from gen.BlockScreen import Ui_BlockScreen
from osutils import get_os, SupportedOs


class BlockScreenWindow(QWidget):
    def __init__(self, basedir):
        super().__init__()
        self.ui = Ui_BlockScreen()
        self.ui.setupUi(self)
        self.basedir = basedir

        self.ui.label.setPixmap(QPixmap(os.path.join(self.basedir, "resources", "lockscreen.png")))

        self.move(0, 0)
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.setFixedSize(screen_width, screen_height)
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint)

        match get_os():
            case SupportedOs.MAC_OS:
                view_id = self.winId()

                # Load the necessary macOS frameworks
                objc = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Cocoa.framework/Cocoa')
                objc.objc_getClass.restype = ctypes.c_void_p
                objc.sel_registerName.restype = ctypes.c_void_p
                objc.objc_msgSend.restype = ctypes.c_void_p
                objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

                # Get the NSView
                NSView = ctypes.c_void_p(view_id)

                # Get the NSWindow from the NSView
                sel_window = objc.sel_registerName(b"window")
                NSWindow = objc.objc_msgSend(NSView, sel_window)

                # Modify the CollectionBehavior of the NSWindow to make it appear on all desktops
                sel_setCollectionBehavior = objc.sel_registerName(b"setCollectionBehavior:")
                # Define the desired collection behavior
                NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
                objc.objc_msgSend(NSWindow, sel_setCollectionBehavior,
                                  ctypes.c_uint(NSWindowCollectionBehaviorCanJoinAllSpaces))

            case _:
                raise Exception("Unsupported OS")

    def moveEvent(self, event):
        self.move(0, 0)
        event.ignore()

    def resizeEvent(self, event):
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_height = screen_geometry.height()
        screen_width = screen_geometry.width()
        self.setFixedSize(screen_width, screen_height)
        event.ignore()
