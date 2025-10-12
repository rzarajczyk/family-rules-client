import logging

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QApplication

from gen.BlockScreen import Ui_BlockScreen
from GuiHelper import GuiHelper
from osutils import get_os, OperatingSystem


class BlockScreenWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_BlockScreen()
        self.ui.setupUi(self)
        self.guihelper = GuiHelper.instance()
        self._fullscreen_check_counter = 0


        # Remove pixmap to allow text styling - we want text instead of image
        # self.ui.label.setPixmap(QPixmap(os.path.join(Basedir.get_str(), "resources", "lockscreen.png")))
        
        # Retranslate UI after setup to apply translations
        self.ui.retranslateUi(self)

        self.move(0, 0)
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.setFixedSize(screen_width, screen_height)
        
        # Enhanced window flags for maximum security
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.WindowDoesNotAcceptFocus |
            Qt.Tool
        )
        
        # Set window attributes for better blocking
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_X11DoNotAcceptFocus, True)
        # Remove WA_NoSystemBackground to allow background styling
        # self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        # Make window modal and always on top
        self.setWindowModality(Qt.ApplicationModal)
        
        # Ensure the entire window has a black background
        self.setStyleSheet("background-color: black;")

        self.guihelper.show_on_all_desktops(self)
        self.guihelper.set_borderless(self)
        self.guihelper.set_window_above_fullscreen(self)
        
        # Timer to ensure window stays on top
        self.stay_on_top_timer = QTimer()
        self.stay_on_top_timer.timeout.connect(self._ensure_stay_on_top)
        self.stay_on_top_timer.start(100)  # Check every 100ms
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'stay_on_top_timer'):
                self.stay_on_top_timer.stop()
            # Ensure system blocking is disabled
            self.guihelper.block_system_input(False)
        except Exception as e:
            logging.error(f"Error during BlockScreenWindow cleanup: {e}")
    
    
    def _is_window_actually_visible(self):
        """Check if our blocking window is actually visible and on top"""
        try:
            # Simple check: if our window is visible and has focus or is on top
            return self.isVisible() and (self.isActiveWindow() or self.isTopLevel())
        except Exception as e:
            logging.debug(f"Failed to check window visibility: {e}")
            return True  # Assume visible if we can't check
    
    def _ensure_stay_on_top(self):
        """Ensure window stays on top of all other windows including fullscreen apps"""
        self._fullscreen_check_counter += 1
        self.guihelper.push_to_top_tick(self, self._fullscreen_check_counter)
    
    def show(self):
        """Override show to ensure proper blocking when displayed"""
        super().show()
        self.raise_()
        # Don't call activateWindow() since this window doesn't accept focus
        self._ensure_stay_on_top()
        
        # Enable system-level blocking
        self.guihelper.block_system_input(True)
        
        # Start the stay-on-top timer with optimized frequency for desktop switching
        if hasattr(self, 'stay_on_top_timer'):
            self.stay_on_top_timer.start(100)  # Check every 100ms (desktop switching every 5 seconds)
    
    def hide(self):
        """Override hide to stop the stay-on-top timer and restore system"""
        if hasattr(self, 'stay_on_top_timer'):
            self.stay_on_top_timer.stop()
        
        # Disable system-level blocking
        self.guihelper.block_system_input(False)
        
        super().hide()
    
    def closeEvent(self, event):
        """Prevent window from being closed"""
        event.ignore()
        logging.warning("Attempted to close BlockScreenWindow - ignored for security")
    
    def keyPressEvent(self, event):
        """Block all keyboard input"""
        event.ignore()
    
    def retranslate_ui(self):
        """Refresh the UI with current translations"""
        self.ui.retranslateUi(self)
    
    def mousePressEvent(self, event):
        """Block all mouse input"""
        event.ignore()
        logging.debug("Blocked mouse input on BlockScreenWindow")

    def moveEvent(self, event):
        self.move(0, 0)
        event.ignore()

    def resizeEvent(self, event):
        """ proactively prevent resizing window """
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_height = screen_geometry.height()
        screen_width = screen_geometry.width()
        self.setFixedSize(screen_width, screen_height)
        event.ignore()
