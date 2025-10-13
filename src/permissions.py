import logging
import os
import platform
import subprocess
import sys
from enum import Enum, auto
from typing import Tuple

from osutils import get_os, OperatingSystem

class Permission:
    @property
    def name(self) -> str:
        return ""
    def grant(self):
        pass

class Permissions:
    def all_granted(self) -> bool:
        pass
    def get_missing_permissions(self) -> list[Permission]:
        pass
    @staticmethod
    def instance():
        match get_os():
            case OperatingSystem.MAC_OS:
                return MacOsPermissions()
            case OperatingSystem.WINDOWS:
                return WinPermissions()
            case _:
                raise Exception("Unsupported operating system")

class MacOsPermissions(Permissions):
    def all_granted(self) -> bool:
        return True
    def get_missing_permissions(self) -> list:
        return []

class WinPermissions(Permissions):
    def all_granted(self) -> bool:
        return True
    def get_missing_permissions(self) -> list:
        return []


# def check_administrator_privileges() -> PermissionStatus:
#     """
#     Check if the application is running with administrator privileges on Windows.
#     Returns PermissionStatus.GRANTED if running as admin, NOT_GRANTED otherwise.
#     """
#     if get_os() != OperatingSystem.WINDOWS:
#         return PermissionStatus.UNKNOWN
#
#     try:
#         import ctypes
#         return PermissionStatus.GRANTED if ctypes.windll.shell32.IsUserAnAdmin() else PermissionStatus.NOT_GRANTED
#     except Exception as e:
#         logging.error(f"Failed to check administrator privileges: {e}")
#         return PermissionStatus.UNKNOWN
#
#
# def open_permission_settings(permission_type: PermissionType) -> bool:
#     """
#     Open the system settings to grant a specific permission.
#     Returns True if the settings were opened successfully, False otherwise.
#     """
#     try:
#         match permission_type:
#             case PermissionType.MACOS_ACCESSIBILITY:
#                 if get_os() == OperatingSystem.MAC_OS:
#                     # Open System Preferences to Accessibility settings
#                     subprocess.run([
#                         "open",
#                         "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
#                     ])
#                     return True
#
#             case PermissionType.WINDOWS_ADMINISTRATOR:
#                 if get_os() == OperatingSystem.WINDOWS:
#                     # For Windows, we can't directly grant admin privileges through settings
#                     # The user needs to restart the application as administrator
#                     return False
#
#         return False
#     except Exception as e:
#         logging.error(f"Failed to open permission settings: {e}")
#         return False
#
#
# def get_permission_instructions(permission_type: PermissionType) -> str:
#     """
#     Get instructions for manually granting a permission.
#     """
#     match permission_type:
#         case PermissionType.MACOS_ACCESSIBILITY:
#             return (
#                 "To grant Accessibility permission:\n"
#                 "1. Open System Preferences → Security & Privacy → Privacy\n"
#                 "2. Select Accessibility from the left sidebar\n"
#                 "3. Click the lock icon and enter your password\n"
#                 "4. Click the + button and add the Family Rules application\n"
#                 "5. Ensure the checkbox next to the application is checked"
#             )
#         case PermissionType.WINDOWS_ADMINISTRATOR:
#             return (
#                 "To run with Administrator privileges:\n"
#                 "1. Right-click on Command Prompt or PowerShell\n"
#                 "2. Select 'Run as administrator'\n"
#                 "3. Navigate to the application directory\n"
#                 "4. Run the application from the elevated command prompt"
#             )
#         case _:
#             return "Unknown permission type"