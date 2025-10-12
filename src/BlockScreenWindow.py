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

    # def _setup_macos_blocking(self):
    #     """Setup macOS-specific blocking mechanisms with enhanced fullscreen support"""
    #     try:
    #         import ctypes
    #         from ctypes import c_void_p, c_uint, c_int
    #
    #         # Get the window ID
    #         window_id = self.winId()
    #
    #         # Load Cocoa and Core Graphics frameworks
    #         objc = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Cocoa.framework/Cocoa')
    #         core_graphics = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
    #
    #         objc.objc_getClass.restype = c_void_p
    #         objc.sel_registerName.restype = c_void_p
    #         objc.objc_msgSend.restype = c_void_p
    #         objc.objc_msgSend.argtypes = [c_void_p, c_void_p]
    #
    #         # Get NSView from window ID
    #         NSView = c_void_p(window_id)
    #         sel_window = objc.sel_registerName(b"window")
    #         NSWindow = objc.objc_msgSend(NSView, sel_window)
    #
    #         # Enhanced collection behavior for fullscreen support
    #         sel_setCollectionBehavior = objc.sel_registerName(b"setCollectionBehavior:")
    #         NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
    #         NSWindowCollectionBehaviorStationary = 1 << 4
    #         NSWindowCollectionBehaviorFullScreenAuxiliary = 1 << 8  # Key for fullscreen support
    #         NSWindowCollectionBehaviorIgnoresCycle = 1 << 2  # Prevent cycling
    #
    #         behavior = (NSWindowCollectionBehaviorCanJoinAllSpaces |
    #                    NSWindowCollectionBehaviorStationary |
    #                    NSWindowCollectionBehaviorFullScreenAuxiliary |
    #                    NSWindowCollectionBehaviorIgnoresCycle)
    #         objc.objc_msgSend(NSWindow, sel_setCollectionBehavior, c_uint(behavior))
    #
    #         # Use multiple window level strategies for maximum compatibility
    #         sel_setLevel = objc.sel_registerName(b"setLevel:")
    #
    #         # Try multiple window levels for maximum compatibility with fullscreen apps
    #         try:
    #             # Method 1: Try CGShieldingWindowLevel (designed for parental controls)
    #             shielding_level = core_graphics.CGShieldingWindowLevel()
    #             # Use shielding level + 2 to be well above system shield windows
    #             window_level = c_int(shielding_level + 2)
    #             objc.objc_msgSend(NSWindow, sel_setLevel, window_level)
    #             logging.debug(f"Window level set to CGShieldingWindowLevel + 2: {shielding_level + 2} (highest priority)")
    #         except Exception as e:
    #             logging.warning(f"⚠️  CGShieldingWindowLevel failed: {e}")
    #             try:
    #                 # Method 2: Try CGMaximumWindowLevel (highest possible)
    #                 max_level = core_graphics.CGMaximumWindowLevel()
    #                 objc.objc_msgSend(NSWindow, sel_setLevel, c_int(max_level))
    #                 logging.debug(f"Window level set to CGMaximumWindowLevel: {max_level} (fallback)")
    #             except Exception as e2:
    #                 logging.warning(f"⚠️  CGMaximumWindowLevel failed: {e2}")
    #                 # Method 3: Fallback to screen saver level (also very high)
    #                 kCGScreenSaverWindowLevel = 1000
    #                 objc.objc_msgSend(NSWindow, sel_setLevel, c_int(kCGScreenSaverWindowLevel))
    #                 logging.debug(f"Window level set to kCGScreenSaverWindowLevel: 1000 (final fallback)")
    #
    #         # Disable window resizing and moving
    #         sel_setStyleMask = objc.sel_registerName(b"setStyleMask:")
    #         NSBorderlessWindowMask = 0
    #         objc.objc_msgSend(NSWindow, sel_setStyleMask, c_uint(NSBorderlessWindowMask))
    #
    #         # Set window to ignore mouse events (additional security)
    #         sel_setIgnoresMouseEvents = objc.sel_registerName(b"setIgnoresMouseEvents:")
    #         objc.objc_msgSend(NSWindow, sel_setIgnoresMouseEvents, c_uint(0))  # 0 = false, don't ignore
    #
    #         # Make window appear above fullscreen applications
    #         sel_setHidesOnDeactivate = objc.sel_registerName(b"setHidesOnDeactivate:")
    #         objc.objc_msgSend(NSWindow, sel_setHidesOnDeactivate, c_uint(0))  # Don't hide on deactivate
    #
    #         logging.info("Enhanced macOS blocking setup completed with fullscreen support")
    #
    #     except Exception as e:
    #         logging.error(f"Failed to setup macOS blocking: {e}")
    #
    # def _request_accessibility_permissions(self):
    #     """Request accessibility permissions for enhanced window control"""
    #     try:
    #         import ctypes
    #         from ctypes import c_void_p, c_uint
    #
    #         # Load Application Services framework
    #         app_services = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
    #
    #         # Check if accessibility is enabled
    #         accessibility_enabled = app_services.AXIsProcessTrusted()
    #         if not accessibility_enabled:
    #             logging.warning("Accessibility permissions not granted. Some fullscreen blocking features may not work.")
    #             # Request accessibility permissions
    #             app_services.AXIsProcessTrustedWithOptions(None)
    #             return False
    #         else:
    #             logging.info("Accessibility permissions are available")
    #             return True
    #
    #     except Exception as e:
    #         logging.error(f"Failed to check accessibility permissions: {e}")
    #         return False
    #
    # def _force_switch_to_first_desktop(self):
    #     try:
    #         import subprocess
    #
    #         # AppleScript to send Ctrl+Arrow Left 10 times
    #         applescript = '''
    #         tell application "System Events"
    #             repeat 10 times
    #                 key code 123 using {control down} -- Ctrl+Arrow Left
    #                 delay 0.1
    #             end repeat
    #         end tell
    #         '''
    #
    #         logging.info("📤 Sending Ctrl+Arrow Left 10 times to switch to first desktop...")
    #         result = subprocess.run(['osascript', '-e', applescript],
    #                               capture_output=True, text=True, timeout=3)
    #
    #         if result.returncode != 0:
    #             if result.stderr:
    #                 logging.warning(f"⚠️  Desktop switching failed: {result.stderr}")
    #             else:
    #                 logging.warning("⚠️  Desktop switching failed with unknown error")
    #
    #     except subprocess.TimeoutExpired:
    #         logging.warning("⏰ Desktop switching timed out after 3 seconds")
    #     except Exception as e:
    #         logging.error(f"❌ Failed to switch to first desktop: {e}")
    
    
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
        # Check accessibility permissions first


        # if get_os() == OperatingSystem.MAC_OS:
        #     self._request_accessibility_permissions()
        
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
