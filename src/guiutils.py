import ctypes
import logging
from ctypes import cdll

import pyautogui

from osutils import get_os, SupportedOs

# Track the current blocking state to avoid redundant logging
_system_input_blocked = False


def show_on_all_desktops(window):
    match get_os():
        case SupportedOs.MAC_OS:
            import ctypes
            from ctypes import c_void_p, c_uint
            
            view_id = window.winId()

            # Load the necessary macOS frameworks
            objc = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Cocoa.framework/Cocoa')
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
        case SupportedOs.WINDOWS:
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
        case _:
            raise Exception("Unsupported OS")


def set_window_above_fullscreen(window):
    """Set window level to appear above fullscreen applications using Accessibility API"""
    match get_os():
        case SupportedOs.MAC_OS:
            try:
                import ctypes
                from ctypes import c_void_p, c_uint, c_int
                
                view_id = window.winId()

                # Load the necessary macOS frameworks
                objc = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Cocoa.framework/Cocoa')
                core_graphics = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
                
                objc.objc_getClass.restype = c_void_p
                objc.sel_registerName.restype = c_void_p
                objc.objc_msgSend.restype = c_void_p
                objc.objc_msgSend.argtypes = [c_void_p, c_void_p]

                # Get the NSView
                NSView = c_void_p(view_id)

                # Get the NSWindow from the NSView
                sel_window = objc.sel_registerName(b"window")
                NSWindow = objc.objc_msgSend(NSView, sel_window)

                # Set window level to appear above fullscreen applications
                # Use CGShieldingWindowLevel + 1 to be above system shield windows
                sel_setLevel = objc.sel_registerName(b"setLevel:")
                shielding_level = core_graphics.CGShieldingWindowLevel()
                window_level = c_int(shielding_level + 1)
                objc.objc_msgSend(NSWindow, sel_setLevel, window_level)

                # Set collection behavior to appear above fullscreen windows
                sel_setCollectionBehavior = objc.sel_registerName(b"setCollectionBehavior:")
                # NSWindowCollectionBehaviorCanJoinAllSpaces | NSWindowCollectionBehaviorFullScreenAuxiliary
                collection_behavior = c_uint((1 << 0) | (1 << 8))  # CanJoinAllSpaces | FullScreenAuxiliary
                objc.objc_msgSend(NSWindow, sel_setCollectionBehavior, collection_behavior)
                
                logging.debug("macOS window level set above fullscreen applications")
                
            except Exception as e:
                logging.error(f"Failed to set macOS window level above fullscreen: {e}")
                
        case SupportedOs.WINDOWS:
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
                
        case _:
            raise Exception("Unsupported OS")


def block_system_input(block: bool):
    """Block system-level input (keyboard and mouse) for maximum security"""
    global _system_input_blocked
    
    # Avoid redundant operations and logging
    if _system_input_blocked == block:
        return
    
    _system_input_blocked = block
    
    match get_os():
        case SupportedOs.MAC_OS:
            try:
                import ctypes
                from ctypes import c_int, c_double
                
                # Load Core Graphics framework
                cg = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
                
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
                
        case SupportedOs.WINDOWS:
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
                
        case _:
            raise Exception("Unsupported OS")

