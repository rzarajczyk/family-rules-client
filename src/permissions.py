import logging
import os
import platform
import subprocess
import sys
from enum import Enum, auto
from typing import Tuple

try:
    from .osutils import get_os, OperatingSystem
except ImportError:
    from osutils import get_os, OperatingSystem


class PermissionType(Enum):
    MACOS_ACCESSIBILITY = auto()
    WINDOWS_ADMINISTRATOR = auto()


class PermissionStatus(Enum):
    GRANTED = auto()
    NOT_GRANTED = auto()
    UNKNOWN = auto()


def check_accessibility_permission() -> PermissionStatus:
    """
    Check if the application has accessibility permission on macOS.
    Returns PermissionStatus.GRANTED if permission is granted, NOT_GRANTED otherwise.
    """
    if get_os() != OperatingSystem.MAC_OS:
        return PermissionStatus.UNKNOWN
    
    try:
        # Try to access accessibility APIs to test if permission is granted
        import ctypes

        app_services = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
        if app_services.AXIsProcessTrusted():
            return PermissionStatus.GRANTED
        else:
            return PermissionStatus.NOT_GRANTED
            
    except Exception as e:
        logging.error(f"Failed to check accessibility permission: {e}")
        return PermissionStatus.UNKNOWN


def check_administrator_privileges() -> PermissionStatus:
    """
    Check if the application is running with administrator privileges on Windows.
    Returns PermissionStatus.GRANTED if running as admin, NOT_GRANTED otherwise.
    """
    if get_os() != OperatingSystem.WINDOWS:
        return PermissionStatus.UNKNOWN
    
    try:
        import ctypes
        return PermissionStatus.GRANTED if ctypes.windll.shell32.IsUserAnAdmin() else PermissionStatus.NOT_GRANTED
    except Exception as e:
        logging.error(f"Failed to check administrator privileges: {e}")
        return PermissionStatus.UNKNOWN


def get_required_permissions() -> list[PermissionType]:
    """ Get the list of permissions required for the current operating system. """
    match get_os():
        case OperatingSystem.MAC_OS:
            return []
        case OperatingSystem.WINDOWS:
            return [PermissionType.WINDOWS_ADMINISTRATOR]
        case _:
            return []


def check_permission_status(permission_type: PermissionType) -> PermissionStatus:
    """ Check the status of a specific permission type. """
    match permission_type:
        case PermissionType.MACOS_ACCESSIBILITY:
            return check_accessibility_permission()
        case PermissionType.WINDOWS_ADMINISTRATOR:
            return check_administrator_privileges()
        case _:
            return PermissionStatus.UNKNOWN


def get_permission_name(permission_type: PermissionType) -> str:
    """
    Get a human-readable name for a permission type.
    """
    match permission_type:
        case PermissionType.MACOS_ACCESSIBILITY:
            return "Accessibility Permission"
        case PermissionType.WINDOWS_ADMINISTRATOR:
            return "Administrator Privileges"
        case _:
            return "Unknown Permission"


def get_permission_description(permission_type: PermissionType) -> str:
    """
    Get a description of what a permission is used for.
    """
    match permission_type:
        case PermissionType.MACOS_ACCESSIBILITY:
            return "Required for screen blocking and input blocking functionality"
        case PermissionType.WINDOWS_ADMINISTRATOR:
            return "Required for system-level screen blocking and process monitoring"
        case _:
            return "Unknown permission"


def open_permission_settings(permission_type: PermissionType) -> bool:
    """
    Open the system settings to grant a specific permission.
    Returns True if the settings were opened successfully, False otherwise.
    """
    try:
        match permission_type:
            case PermissionType.MACOS_ACCESSIBILITY:
                if get_os() == OperatingSystem.MAC_OS:
                    # Open System Preferences to Accessibility settings
                    subprocess.run([
                        "open", 
                        "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
                    ])
                    return True
                    
            case PermissionType.WINDOWS_ADMINISTRATOR:
                if get_os() == OperatingSystem.WINDOWS:
                    # For Windows, we can't directly grant admin privileges through settings
                    # The user needs to restart the application as administrator
                    return False
                    
        return False
    except Exception as e:
        logging.error(f"Failed to open permission settings: {e}")
        return False


def get_permission_instructions(permission_type: PermissionType) -> str:
    """
    Get instructions for manually granting a permission.
    """
    match permission_type:
        case PermissionType.MACOS_ACCESSIBILITY:
            return (
                "To grant Accessibility permission:\n"
                "1. Open System Preferences → Security & Privacy → Privacy\n"
                "2. Select Accessibility from the left sidebar\n"
                "3. Click the lock icon and enter your password\n"
                "4. Click the + button and add the Family Rules application\n"
                "5. Ensure the checkbox next to the application is checked"
            )
        case PermissionType.WINDOWS_ADMINISTRATOR:
            return (
                "To run with Administrator privileges:\n"
                "1. Right-click on Command Prompt or PowerShell\n"
                "2. Select 'Run as administrator'\n"
                "3. Navigate to the application directory\n"
                "4. Run the application from the elevated command prompt"
            )
        case _:
            return "Unknown permission type"


def check_all_permissions() -> dict[PermissionType, PermissionStatus]:
    """
    Check the status of all required permissions for the current system.
    Returns a dictionary mapping permission types to their status.
    """
    permissions = {}
    required_permissions = get_required_permissions()
    
    for permission_type in required_permissions:
        permissions[permission_type] = check_permission_status(permission_type)
    
    return permissions


def are_all_permissions_granted() -> bool:
    """
    Check if all required permissions are granted.
    Returns True if all permissions are granted, False otherwise.
    """
    permissions = check_all_permissions()
    return all(status == PermissionStatus.GRANTED for status in permissions.values())
