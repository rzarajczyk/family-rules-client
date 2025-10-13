import logging

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QApplication

from gen.BlockScreen import Ui_BlockScreen
from GuiHelper import GuiHelper


class MultiMonitorBlockScreenManager:
    """Manages blocking windows across all monitors"""
    
    def __init__(self):
        self.guihelper = GuiHelper.instance()
        self.blocking_windows = []
        self._fullscreen_check_counter = 0
        self.stay_on_top_timer = None
        
    def _create_blocking_windows(self):
        """Create blocking windows for all monitors"""
        # Clear existing windows
        self._cleanup_windows()
        
        # Create new windows for all monitors
        self.blocking_windows = self.guihelper.create_multi_monitor_blocking_windows(
            SingleMonitorBlockScreenWindow
        )
        
        # Setup timer for all windows
        self.stay_on_top_timer = QTimer()
        self.stay_on_top_timer.timeout.connect(self._ensure_stay_on_top)
        
        logging.info(f"Created {len(self.blocking_windows)} blocking windows for multi-monitor setup")
    
    def _cleanup_windows(self):
        """Clean up existing blocking windows"""
        for window in self.blocking_windows:
            try:
                if hasattr(window, 'stay_on_top_timer'):
                    window.stay_on_top_timer.stop()
                window.hide()
                window.close()
            except Exception as e:
                logging.error(f"Error cleaning up blocking window: {e}")
        self.blocking_windows.clear()
        
        if self.stay_on_top_timer:
            self.stay_on_top_timer.stop()
            self.stay_on_top_timer = None
    
    def _ensure_stay_on_top(self):
        """Ensure all windows stay on top of all other windows including fullscreen apps"""
        self._fullscreen_check_counter += 1
        for window in self.blocking_windows:
            if window.isVisible():
                self.guihelper.push_to_top_tick(window, self._fullscreen_check_counter)
    
    def show(self):
        """Show blocking windows on all monitors"""
        if not self.blocking_windows:
            self._create_blocking_windows()
        
        for window in self.blocking_windows:
            window.show()
            window.raise_()
        
        # Enable system-level blocking
        self.guihelper.block_system_input(True)
        
        # Start the stay-on-top timer
        if self.stay_on_top_timer:
            self.stay_on_top_timer.start(100)  # Check every 100ms
        
        logging.info("Multi-monitor blocking windows shown")
    
    def hide(self):
        """Hide all blocking windows"""
        # Stop the stay-on-top timer
        if self.stay_on_top_timer:
            self.stay_on_top_timer.stop()
        
        # Hide all windows
        for window in self.blocking_windows:
            window.hide()
        
        # Disable system-level blocking
        self.guihelper.block_system_input(False)
        
        logging.info("Multi-monitor blocking windows hidden")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self._cleanup_windows()
        except Exception as e:
            logging.error(f"Error during MultiMonitorBlockScreenManager cleanup: {e}")


class SingleMonitorBlockScreenWindow(QWidget):
    """A single blocking window for one monitor - simplified version of BlockScreenWindow"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_BlockScreen()
        self.ui.setupUi(self)
        self.guihelper = GuiHelper.instance()
        self._fullscreen_check_counter = 0

        # Retranslate UI after setup to apply translations
        self.ui.retranslateUi(self)

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
        
        # Make window modal and always on top
        self.setWindowModality(Qt.ApplicationModal)
        
        # Ensure the entire window has a black background
        self.setStyleSheet("background-color: black;")
        
        # Timer to ensure window stays on top
        self.stay_on_top_timer = QTimer()
        self.stay_on_top_timer.timeout.connect(self._ensure_stay_on_top)
        self.stay_on_top_timer.start(100)  # Check every 100ms
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'stay_on_top_timer'):
                self.stay_on_top_timer.stop()
        except Exception as e:
            logging.error(f"Error during SingleMonitorBlockScreenWindow cleanup: {e}")
    
    def _ensure_stay_on_top(self):
        """Ensure window stays on top of all other windows including fullscreen apps"""
        self._fullscreen_check_counter += 1
        self.guihelper.push_to_top_tick(self, self._fullscreen_check_counter)
    
    def show(self):
        """Override show to ensure proper blocking when displayed"""
        super().show()
        self.raise_()
        self._ensure_stay_on_top()
        
        # Start the stay-on-top timer
        if hasattr(self, 'stay_on_top_timer'):
            self.stay_on_top_timer.start(100)
    
    def hide(self):
        """Override hide to stop the stay-on-top timer"""
        if hasattr(self, 'stay_on_top_timer'):
            self.stay_on_top_timer.stop()
        super().hide()
    
    def closeEvent(self, event):
        """Prevent window from being closed"""
        event.ignore()
        logging.warning("Attempted to close SingleMonitorBlockScreenWindow - ignored for security")
    
    def keyPressEvent(self, event):
        """Block all keyboard input"""
        event.ignore()
    
    def retranslate_ui(self):
        """Refresh the UI with current translations"""
        self.ui.retranslateUi(self)
    
    def mousePressEvent(self, event):
        """Block all mouse input"""
        event.ignore()
        logging.debug("Blocked mouse input on SingleMonitorBlockScreenWindow")

    def moveEvent(self, event):
        """Prevent window from being moved"""
        event.ignore()

    def resizeEvent(self, event):
        """Prevent window from being resized"""
        event.ignore()