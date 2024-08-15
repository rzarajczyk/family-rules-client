import ctypes

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

        case _:
            raise Exception("Unsupported OS")