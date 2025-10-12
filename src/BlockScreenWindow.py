import logging

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QApplication

from gen.BlockScreen import Ui_BlockScreen
from guiutils import show_on_all_desktops, block_system_input
from osutils import get_os, SupportedOs

from guiutils import set_window_above_fullscreen



class BlockScreenWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_BlockScreen()
        self.ui.setupUi(self)

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
        
        match get_os():
            case SupportedOs.MAC_OS:
                self._setup_macos_blocking()
            case SupportedOs.WINDOWS:
                self._setup_windows_blocking()
            case _:
                raise Exception("Unsupported operating system")
        
        show_on_all_desktops(self)
        
        set_window_above_fullscreen(self)
        
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
            block_system_input(False)
        except Exception as e:
            logging.error(f"Error during BlockScreenWindow cleanup: {e}")

    def _setup_macos_blocking(self):
        """Setup macOS-specific blocking mechanisms with enhanced fullscreen support"""
        try:
            import ctypes
            from ctypes import c_void_p, c_uint, c_int
            
            # Get the window ID
            window_id = self.winId()
            
            # Load Cocoa and Core Graphics frameworks
            objc = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Cocoa.framework/Cocoa')
            core_graphics = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
            
            objc.objc_getClass.restype = c_void_p
            objc.sel_registerName.restype = c_void_p
            objc.objc_msgSend.restype = c_void_p
            objc.objc_msgSend.argtypes = [c_void_p, c_void_p]
            
            # Get NSView from window ID
            NSView = c_void_p(window_id)
            sel_window = objc.sel_registerName(b"window")
            NSWindow = objc.objc_msgSend(NSView, sel_window)
            
            # Enhanced collection behavior for fullscreen support
            sel_setCollectionBehavior = objc.sel_registerName(b"setCollectionBehavior:")
            NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
            NSWindowCollectionBehaviorStationary = 1 << 4
            NSWindowCollectionBehaviorFullScreenAuxiliary = 1 << 8  # Key for fullscreen support
            NSWindowCollectionBehaviorIgnoresCycle = 1 << 2  # Prevent cycling
            
            behavior = (NSWindowCollectionBehaviorCanJoinAllSpaces | 
                       NSWindowCollectionBehaviorStationary | 
                       NSWindowCollectionBehaviorFullScreenAuxiliary |
                       NSWindowCollectionBehaviorIgnoresCycle)
            objc.objc_msgSend(NSWindow, sel_setCollectionBehavior, c_uint(behavior))
            
            # Use multiple window level strategies for maximum compatibility
            sel_setLevel = objc.sel_registerName(b"setLevel:")
            
            # Try multiple window levels for maximum compatibility with fullscreen apps
            try:
                # Method 1: Try CGShieldingWindowLevel (designed for parental controls)
                shielding_level = core_graphics.CGShieldingWindowLevel()
                # Use shielding level + 2 to be well above system shield windows
                window_level = c_int(shielding_level + 2)
                objc.objc_msgSend(NSWindow, sel_setLevel, window_level)
                logging.debug(f"Window level set to CGShieldingWindowLevel + 2: {shielding_level + 2} (highest priority)")
            except Exception as e:
                logging.warning(f"⚠️  CGShieldingWindowLevel failed: {e}")
                try:
                    # Method 2: Try CGMaximumWindowLevel (highest possible)
                    max_level = core_graphics.CGMaximumWindowLevel()
                    objc.objc_msgSend(NSWindow, sel_setLevel, c_int(max_level))
                    logging.debug(f"Window level set to CGMaximumWindowLevel: {max_level} (fallback)")
                except Exception as e2:
                    logging.warning(f"⚠️  CGMaximumWindowLevel failed: {e2}")
                    # Method 3: Fallback to screen saver level (also very high)
                    kCGScreenSaverWindowLevel = 1000
                    objc.objc_msgSend(NSWindow, sel_setLevel, c_int(kCGScreenSaverWindowLevel))
                    logging.debug(f"Window level set to kCGScreenSaverWindowLevel: 1000 (final fallback)")
            
            # Disable window resizing and moving
            sel_setStyleMask = objc.sel_registerName(b"setStyleMask:")
            NSBorderlessWindowMask = 0
            objc.objc_msgSend(NSWindow, sel_setStyleMask, c_uint(NSBorderlessWindowMask))
            
            # Set window to ignore mouse events (additional security)
            sel_setIgnoresMouseEvents = objc.sel_registerName(b"setIgnoresMouseEvents:")
            objc.objc_msgSend(NSWindow, sel_setIgnoresMouseEvents, c_uint(0))  # 0 = false, don't ignore
            
            # Make window appear above fullscreen applications
            sel_setHidesOnDeactivate = objc.sel_registerName(b"setHidesOnDeactivate:")
            objc.objc_msgSend(NSWindow, sel_setHidesOnDeactivate, c_uint(0))  # Don't hide on deactivate
            
            logging.info("Enhanced macOS blocking setup completed with fullscreen support")
            
        except Exception as e:
            logging.error(f"Failed to setup macOS blocking: {e}")
    
    def _request_accessibility_permissions(self):
        """Request accessibility permissions for enhanced window control"""
        try:
            import ctypes
            from ctypes import c_void_p, c_uint
            
            # Load Application Services framework
            app_services = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
            
            # Check if accessibility is enabled
            accessibility_enabled = app_services.AXIsProcessTrusted()
            if not accessibility_enabled:
                logging.warning("Accessibility permissions not granted. Some fullscreen blocking features may not work.")
                # Request accessibility permissions
                app_services.AXIsProcessTrustedWithOptions(None)
                return False
            else:
                logging.info("Accessibility permissions are available")
                return True
                
        except Exception as e:
            logging.error(f"Failed to check accessibility permissions: {e}")
            return False
    
    def _force_switch_to_first_desktop(self):
        try:
            import subprocess
            
            # AppleScript to send Ctrl+Arrow Left 10 times
            applescript = '''
            tell application "System Events"
                repeat 10 times
                    key code 123 using {control down} -- Ctrl+Arrow Left
                    delay 0.1
                end repeat
            end tell
            '''
            
            logging.info("📤 Sending Ctrl+Arrow Left 10 times to switch to first desktop...")
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True, timeout=3)
            
            if result.returncode != 0:
                if result.stderr:
                    logging.warning(f"⚠️  Desktop switching failed: {result.stderr}")
                else:
                    logging.warning("⚠️  Desktop switching failed with unknown error")
                
        except subprocess.TimeoutExpired:
            logging.warning("⏰ Desktop switching timed out after 3 seconds")
        except Exception as e:
            logging.error(f"❌ Failed to switch to first desktop: {e}")
    
    
    def _is_window_actually_visible(self):
        """Check if our blocking window is actually visible and on top"""
        try:
            # Simple check: if our window is visible and has focus or is on top
            return self.isVisible() and (self.isActiveWindow() or self.isTopLevel())
        except Exception as e:
            logging.debug(f"Failed to check window visibility: {e}")
            return True  # Assume visible if we can't check
    
    def _setup_windows_blocking(self):
        """Setup Windows-specific blocking mechanisms"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get window handle
            hwnd = int(self.winId())
            
            # Set window to be always on top with highest priority
            HWND_TOPMOST = -1
            HWND_NOTOPMOST = -2
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_SHOWWINDOW = 0x0040
            
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
            )
            
            # Disable Alt+Tab and other system shortcuts
            # This requires additional system-level hooks (would need more complex implementation)
            
            logging.info("Windows blocking setup completed")
            
        except Exception as e:
            logging.error(f"Failed to setup Windows blocking: {e}")
    
    def _ensure_stay_on_top(self):
        """Ensure window stays on top of all other windows including fullscreen apps"""
        if not self.isVisible():
            return
            
        try:
            match get_os():
                case SupportedOs.MAC_OS:
                    # Only check for fullscreen apps occasionally to avoid performance issues
                    # Use a simple counter to reduce frequency of expensive operations
                    if not hasattr(self, '_fullscreen_check_counter'):
                        self._fullscreen_check_counter = 0
                    
                    self._fullscreen_check_counter += 1
                    
                    # Desktop switching every 2 seconds (20 calls at 100ms intervals)
                    desktop_switch_interval = 20  # 2 seconds
                    
                    if self._fullscreen_check_counter % desktop_switch_interval == 0:
                        check_number = self._fullscreen_check_counter // desktop_switch_interval
                        logging.info(f"🔄 Periodic desktop switch #{check_number} (every 5 seconds)")
                        
                        # Force switch to first desktop
                        self._force_switch_to_first_desktop()
                    
                    # Force window to front on macOS without activating (since it doesn't accept focus)
                    self.raise_()
                    # Use lower-level macOS API to bring window to front without activation
                    import ctypes
                    from ctypes import c_void_p, c_uint, c_int
                    
                    window_id = self.winId()
                    objc = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Cocoa.framework/Cocoa')
                    core_graphics = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
                    
                    objc.objc_getClass.restype = c_void_p
                    objc.sel_registerName.restype = c_void_p
                    objc.objc_msgSend.restype = c_void_p
                    objc.objc_msgSend.argtypes = [c_void_p, c_void_p]
                    
                    NSView = c_void_p(window_id)
                    sel_window = objc.sel_registerName(b"window")
                    NSWindow = objc.objc_msgSend(NSView, sel_window)
                    
                    # Re-apply window level to ensure it stays above fullscreen apps
                    sel_setLevel = objc.sel_registerName(b"setLevel:")
                    try:
                        # Try CGShieldingWindowLevel + 2 for maximum compatibility
                        shielding_level = core_graphics.CGShieldingWindowLevel()
                        window_level = c_int(shielding_level + 2)
                        objc.objc_msgSend(NSWindow, sel_setLevel, window_level)
                        logging.debug(f"🔄 Re-applied window level: CGShieldingWindowLevel + 2 = {shielding_level + 2}")
                    except Exception as e:
                        logging.debug(f"⚠️  Re-applying CGShieldingWindowLevel failed: {e}")
                        try:
                            # Try CGMaximumWindowLevel as fallback
                            max_level = core_graphics.CGMaximumWindowLevel()
                            objc.objc_msgSend(NSWindow, sel_setLevel, c_int(max_level))
                            logging.debug(f"🔄 Re-applied window level: CGMaximumWindowLevel = {max_level}")
                        except Exception as e2:
                            logging.debug(f"⚠️  Re-applying CGMaximumWindowLevel failed: {e2}")
                            # Final fallback to screen saver level
                            kCGScreenSaverWindowLevel = 1000
                            objc.objc_msgSend(NSWindow, sel_setLevel, c_int(kCGScreenSaverWindowLevel))
                            logging.debug(f"🔄 Re-applied window level: kCGScreenSaverWindowLevel = 1000")
                    
                    # Order window to front without making it key
                    sel_orderFront = objc.sel_registerName(b"orderFront:")
                    objc.objc_msgSend(NSWindow, sel_orderFront, c_void_p(0))
                    
                    # Force window to be visible even over fullscreen apps
                    sel_makeKeyAndOrderFront = objc.sel_registerName(b"makeKeyAndOrderFront:")
                    objc.objc_msgSend(NSWindow, sel_makeKeyAndOrderFront, c_void_p(0))
                    
                case SupportedOs.WINDOWS:
                    # Force window to front on Windows
                    hwnd = int(self.winId())
                    HWND_TOPMOST = -1
                    SWP_NOMOVE = 0x0002
                    SWP_NOSIZE = 0x0001
                    SWP_NOACTIVATE = 0x0010
                    
                    import ctypes
                    ctypes.windll.user32.SetWindowPos(
                        hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
                    )
        except Exception as e:
            logging.error(f"Failed to ensure stay on top: {e}")
    
    def show(self):
        """Override show to ensure proper blocking when displayed"""
        # Check accessibility permissions first
        if get_os() == SupportedOs.MAC_OS:
            self._request_accessibility_permissions()
        
        super().show()
        self.raise_()
        # Don't call activateWindow() since this window doesn't accept focus
        self._ensure_stay_on_top()
        
        # Enable system-level blocking
        block_system_input(True)
        
        # Start the stay-on-top timer with optimized frequency for desktop switching
        if hasattr(self, 'stay_on_top_timer'):
            self.stay_on_top_timer.start(100)  # Check every 100ms (desktop switching every 5 seconds)
    
    def hide(self):
        """Override hide to stop the stay-on-top timer and restore system"""
        if hasattr(self, 'stay_on_top_timer'):
            self.stay_on_top_timer.stop()
        
        # Disable system-level blocking
        block_system_input(False)
        
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
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_height = screen_geometry.height()
        screen_width = screen_geometry.width()
        self.setFixedSize(screen_width, screen_height)
        event.ignore()
