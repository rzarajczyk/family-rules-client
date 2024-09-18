from AppKit import NSWorkspace

active_app_name = NSWorkspace.sharedWorkspace().frontmostApplication()

print(active_app_name)