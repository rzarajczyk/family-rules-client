import logging
import subprocess
from osutils import get_os, OperatingSystem


class GuiHelper:
    def set_borderless(self, window):
        pass

    def show_on_all_desktops(self, window):
        pass

    def set_window_above_fullscreen(self, window):
        pass

    def block_system_input(self, block: bool):
        pass

    def push_to_top_tick(self, window):
        """ This function should be called in a timer every 100ms! """
        pass

    @staticmethod
    def instance():
        match get_os():
            case OperatingSystem.MAC_OS:
                return MacOsGuiHelper()
            case OperatingSystem.WINDOWS:
                return WinGuiHelper()
            case _:
                raise Exception("Unsupported operating system")

class MacOsGraphicLibs:
    def __init__(self):
        import ctypes
        self.CoreGraphics = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
        self.Cocoa = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Cocoa.framework/Cocoa')


class MacOsGuiHelper(GuiHelper):
    _system_input_blocked = False
    def __init__(self):
        self.libs = MacOsGraphicLibs()

    def set_borderless(self, window):
        from ctypes import c_uint
        objc = self.libs.CoreGraphics
        NSWindow = self._get_NSWindow(window)

        sel_setStyleMask = objc.sel_registerName(b"setStyleMask:")
        NSBorderlessWindowMask = 0
        objc.objc_msgSend(NSWindow, sel_setStyleMask, c_uint(NSBorderlessWindowMask))

    def _get_NSWindow(self, window):
        from ctypes import c_void_p, c_int
        window_id = window.winId()
        objc = self.libs.CoreGraphics

        objc.objc_getClass.restype = c_void_p
        objc.sel_registerName.restype = c_void_p
        objc.objc_msgSend.restype = c_void_p
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p]

        NSView = c_void_p(window_id)
        sel_window = objc.sel_registerName(b"window")
        NSWindow = objc.objc_msgSend(NSView, sel_window)
        return NSWindow

    def _set_shielding_window_level(self, NSWindow, level):
        # Use lower-level macOS API to bring window to front without activation
        from ctypes import c_int

        objc = self.libs.CoreGraphics
        sel_setLevel = objc.sel_registerName(b"setLevel:")

        window_level = c_int(level)
        objc.objc_msgSend(NSWindow, sel_setLevel, window_level)
        logging.debug(f"Shielding window level set to {level}")

    def show_on_all_desktops(self, window):
        from ctypes import c_void_p, c_uint

        view_id = window.winId()

        # Load the necessary macOS frameworks
        objc = self.libs.Cocoa
        objc.objc_getClass.restype = c_void_p
        objc.sel_registerName.restype = c_void_p
        objc.objc_msgSend.restype = c_void_p
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p]

        # Get the NSView
        NSView = c_void_p(view_id)

        # Get the NSWindow from the NSView
        sel_window = objc.sel_registerName(b"window")
        NSWindow = objc.objc_msgSend(NSView, sel_window)

        # Modify the CollectionBehavior of the NSWindow to make it appear on all desktops
        sel_setCollectionBehavior = objc.sel_registerName(b"setCollectionBehavior:")
        # Define the desired collection behavior
        NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
        objc.objc_msgSend(NSWindow, sel_setCollectionBehavior,
                          c_uint(NSWindowCollectionBehaviorCanJoinAllSpaces))

    def set_window_above_fullscreen(self, window):
        try:
            import ctypes
            from ctypes import c_void_p, c_uint, c_int

            objc = self.libs.CoreGraphics
            core_graphics = self.libs.CoreGraphics
            NSWindow = self._get_NSWindow(window)

            try:
                # Try CGShieldingWindowLevel + 2 for maximum compatibility
                shielding_level = core_graphics.CGShieldingWindowLevel()
                self._set_shielding_window_level(NSWindow, shielding_level + 2)
            except Exception as e:
                logging.debug(f"⚠️  Shielding window level setting (primary method) failed - trying fallback method...", e)
                try:
                    # Try CGMaximumWindowLevel as fallback
                    max_level = core_graphics.CGMaximumWindowLevel()
                    self._set_shielding_window_level(NSWindow, max_level)
                except Exception as e2:
                    logging.debug(f"⚠️  Shielding window level setting (fallback method) failed - trying final fallback method...", e2)
                    # Final fallback to screen saver level
                    kCGScreenSaverWindowLevel = 1000
                    self._set_shielding_window_level(NSWindow, kCGScreenSaverWindowLevel)

            # Order window to front without making it key
            sel_orderFront = objc.sel_registerName(b"orderFront:")
            objc.objc_msgSend(NSWindow, sel_orderFront, c_void_p(0))

            # Force window to be visible even over fullscreen apps
            sel_makeKeyAndOrderFront = objc.sel_registerName(b"makeKeyAndOrderFront:")
            objc.objc_msgSend(NSWindow, sel_makeKeyAndOrderFront, c_void_p(0))

            # Set collection behavior to appear above fullscreen windows
            sel_setCollectionBehavior = objc.sel_registerName(b"setCollectionBehavior:")

            NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
            NSWindowCollectionBehaviorStationary = 1 << 4
            NSWindowCollectionBehaviorFullScreenAuxiliary = 1 << 8  # Key for fullscreen support
            NSWindowCollectionBehaviorIgnoresCycle = 1 << 2  # Prevent cycling

            collection_behavior = c_uint(NSWindowCollectionBehaviorCanJoinAllSpaces |
                        NSWindowCollectionBehaviorStationary |
                        NSWindowCollectionBehaviorFullScreenAuxiliary |
                        NSWindowCollectionBehaviorIgnoresCycle)
            objc.objc_msgSend(NSWindow, sel_setCollectionBehavior, collection_behavior)

            # Make window appear above fullscreen applications
            sel_setHidesOnDeactivate = objc.sel_registerName(b"setHidesOnDeactivate:")
            objc.objc_msgSend(NSWindow, sel_setHidesOnDeactivate, c_uint(0))  # Don't hide on deactivate

        except Exception as e:
            logging.error(f"Failed to set macOS window level above fullscreen", e)

    def block_system_input(self, block: bool):
        if MacOsGuiHelper._system_input_blocked == block:
            return

        MacOsGuiHelper._system_input_blocked = block
        try:
            from ctypes import c_int, c_double

            # Load Core Graphics framework
            cg = self.libs.CoreGraphics

            # Define the function signature
            cg.CGEventSourceSetLocalEventsSuppressionInterval.argtypes = [c_int, c_double]
            cg.CGEventSourceSetLocalEventsSuppressionInterval.restype = None

            if block:
                # Block all input events - use a large suppression interval
                cg.CGEventSourceSetLocalEventsSuppressionInterval(c_int(0), c_double(3600.0))  # 1 hour
                logging.info("System input blocked on macOS")
            else:
                # Restore input events - set suppression interval to 0
                cg.CGEventSourceSetLocalEventsSuppressionInterval(c_int(0), c_double(0.0))
                logging.debug("System input restored on macOS")

        except Exception as e:
            logging.error(f"Failed to block system input on macOS: {e}")

    def push_to_top_tick(self, window, counter):
        """ This function should be called in a timer every 100ms! """
        if not window.isVisible():
            return

        try:
            # Desktop switching every 2 seconds (20 calls at 100ms intervals)
            desktop_switch_interval = 20  # 2 seconds

            if counter % desktop_switch_interval == 0:
                check_number = counter // desktop_switch_interval
                logging.info(f"🔄 Periodic desktop switch #{check_number}")

                # Force switch to first desktop
                self._force_switch_to_first_desktop()

            # Force window to front on macOS without activating (since it doesn't accept focus)
            window.raise_()
            self.set_window_above_fullscreen(window)
        except Exception as e:
            logging.error(f"Failed to ensure stay on top", e)

    def _force_switch_to_first_desktop(self):
        try:
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

class WinGuiHelper(GuiHelper):
    _system_input_blocked = False

    def show_on_all_desktops(self, window):
        try:
            import ctypes
            from ctypes import wintypes

            # Get window handle
            hwnd = int(window.winId())

            # Set window to appear on all virtual desktops
            # This uses the Windows 10+ virtual desktop API
            try:
                # Try to use the modern virtual desktop API
                ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0)

                # Set window to be always on top
                HWND_TOPMOST = -1
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_SHOWWINDOW = 0x0040

                ctypes.windll.user32.SetWindowPos(
                    hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
                )

                logging.debug("Windows show on all desktops setup completed")

            except Exception as e:
                logging.warning(f"Modern Windows virtual desktop API failed: {e}")
                # Fallback to basic always-on-top
                HWND_TOPMOST = -1
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_SHOWWINDOW = 0x0040

                ctypes.windll.user32.SetWindowPos(
                    hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
                )

        except Exception as e:
            logging.error(f"Failed to setup Windows show on all desktops: {e}")

    def set_window_above_fullscreen(self, window):
        try:
            import ctypes
            from ctypes import wintypes

            # Get window handle
            hwnd = int(window.winId())

            # Set window to be above fullscreen applications
            # Use HWND_TOPMOST with additional flags for maximum visibility
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_SHOWWINDOW = 0x0040
            SWP_NOACTIVATE = 0x0010

            # Set window position to topmost
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW | SWP_NOACTIVATE
            )

            # Try to set window to appear above fullscreen applications
            # This uses the Windows 10+ virtual desktop API
            try:
                # Set window to appear on all virtual desktops and above fullscreen
                ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0)
                logging.info("Windows window set above fullscreen applications")
            except Exception as e:
                logging.warning(f"Windows fullscreen override failed: {e}")

        except Exception as e:
            logging.error(f"Failed to set Windows window above fullscreen: {e}")

    def block_system_input(self, block: bool):
        global _system_input_blocked
        if WinGuiHelper._system_input_blocked == block:
            return

        WinGuiHelper._system_input_blocked = block

        try:
            import ctypes
            from ctypes import wintypes

            if block:
                # Block input using Windows API
                # This is a simplified version - full implementation would require hooks
                logging.info("System input blocking requested on Windows")
            else:
                # Restore input
                logging.debug("System input restored on Windows")

        except Exception as e:
            logging.error(f"Failed to block system input on Windows: {e}")

    def push_to_top_tick(self, window):
        self.set_window_above_fullscreen(window)
        # try:
        #     # Force window to front on Windows
        #     hwnd = int(window.winId())
        #     HWND_TOPMOST = -1
        #     SWP_NOMOVE = 0x0002
        #     SWP_NOSIZE = 0x0001
        #     SWP_NOACTIVATE = 0x0010
        #
        #     import ctypes
        #     ctypes.windll.user32.SetWindowPos(
        #         hwnd, HWND_TOPMOST, 0, 0, 0, 0,
        #         SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
        #     )
        # except Exception as e:
        #     logging.error(f"Failed to ensure stay on top: {e}")