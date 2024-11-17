import ctypes
import logging
from ctypes import cdll

import pyautogui

from osutils import get_os, SupportedOs


def show_on_all_desktops(window):
    match get_os():
        case SupportedOs.MAC_OS:
            view_id = window.winId()

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
        case SupportedOs.WINDOWS:
            # FIXME UNSUPPORTED_WINDOWS
            logging.debug("Show on all desktops - not implemented for Windows")
        case _:
            raise Exception("Unsupported OS")


def set_grayscale(on: bool):
    match get_os():
        case SupportedOs.MAC_OS:
            lib = cdll.LoadLibrary("/System/Library/PrivateFrameworks/UniversalAccess.framework/UniversalAccess")
            lib.UAGrayscaleSetEnabled(on)
        case SupportedOs.WINDOWS:
            if is_windows_grayscale_enabled() != on:
                pyautogui.hotkey('win', 'ctrl', 'c')
        case _:
            raise Exception("Unsupported OS")


def is_windows_grayscale_enabled():
    import winreg
    try:
        # Open the registry key for color filtering settings
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\ColorFiltering")

        # Read the 'Active' and 'FilterType' values
        active = winreg.QueryValueEx(key, "Active")[0]
        filter_type = winreg.QueryValueEx(key, "FilterType")[0]

        # Close the registry key
        winreg.CloseKey(key)

        # Check if grayscale is enabled
        if active == 1 and filter_type == 0:
            return True  # Grayscale is enabled
        else:
            return False  # Grayscale is not enabled

    except FileNotFoundError:
        return False