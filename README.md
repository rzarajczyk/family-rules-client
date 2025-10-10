# Family Rules Client

A parental control application that provides screen time management and device locking capabilities across macOS and Windows platforms.

## Features

- **Screen Time Tracking**: Monitor application usage and screen time
- **Device Locking**: Secure screen locking with countdown timers
- **Multi-State Management**: Active, Locked, Logged Out, and Disabled states
- **Cross-Platform**: Works on macOS and Windows
- **System Integration**: Deep OS-level integration for maximum security

## Installation

### Prerequisites

- Python 3.8 or higher
- macOS 10.14+ or Windows 10+
- Administrator/root privileges for system-level features

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python src/main.py`

## Required Permissions

### macOS Permissions

The application requires the following permission to function properly as a parental control tool:

#### 1. Accessibility Permission
**Required for**: Screen blocking and input blocking
**How to grant**:
1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Accessibility** from the left sidebar
3. Click the lock icon and enter your password
4. Click the **+** button and add the Family Rules application
5. Ensure the checkbox next to the application is checked

### Windows Permissions

#### 1. Administrator Privileges
**Required for**: System-level screen blocking and process monitoring
**How to grant**:
1. Right-click on Command Prompt or PowerShell
2. Select **"Run as administrator"**
3. Navigate to the application directory
4. Run the application from the elevated command prompt

#### 2. UAC (User Account Control) Settings
**Recommended**: Set UAC to "Always notify" for maximum security
**How to configure**:
1. Press `Win + R`, type `msconfig`, and press Enter
2. Go to the **Tools** tab
3. Select **"Change UAC settings"** and click **Launch**
4. Move the slider to **"Always notify"**
5. Click **OK** and restart if prompted

#### 3. Windows Defender Exclusions
**Recommended**: Add application to Windows Defender exclusions
**How to configure**:
1. Open **Windows Security** → **Virus & threat protection**
2. Click **"Manage settings"** under Virus & threat protection settings
3. Click **"Add or remove exclusions"**
4. Click **"Add an exclusion"** → **"Folder"**
5. Select the Family Rules application folder

## Security Features

### Enhanced Screen Locking

The application now includes advanced screen locking capabilities:

- **Frameless Fullscreen Overlay**: Blocks all underlying windows including fullscreen applications
- **System-Level Integration**: Uses OS APIs for maximum security
- **Input Blocking**: Prevents keyboard and mouse input during lock
- **Always-On-Top Enforcement**: Continuous monitoring to ensure lock screen stays visible
- **Cross-Desktop Support**: Works across all virtual desktops and spaces

### State Management

The application supports six distinct states:

1. **ACTIVE**: Normal operation, no restrictions
2. **LOCKED**: Blocks screen access with countdown timer
3. **LOCKED_WITH_COUNTDOWN**: 60-second countdown before locking
4. **LOGGED_OUT**: Logs out the user with countdown timer
5. **LOGGED_OUT_WITH_COUNTDOWN**: 60-second countdown before logout
6. **APP_DISABLED**: Uninstalls autorun and exits application

## Troubleshooting

### Permission Issues

If the application doesn't work properly:

1. **Check accessibility permission** is granted (macOS) or **administrator privileges** (Windows)
2. **Restart the application** after granting permissions
3. **Restart the system** if permissions still don't take effect
4. **Check system logs** for permission-related errors

### Screen Locking Issues

If the screen lock doesn't work properly:

1. **Verify accessibility permission** is granted (macOS)
2. **Ensure the application is running as administrator** (Windows)
3. **Check if other security software** is interfering
4. **Try running the application as administrator/root**

### Performance Issues

If the application causes performance problems:

1. **Check system resources** (CPU, memory usage)
2. **Disable unnecessary features** in settings
3. **Update to the latest version**
4. **Check for conflicting applications**

## Development

### Building from Source

1. Install build dependencies: `pip install -r requirements.txt`
2. Generate UI files: `./generate-gui.sh`
3. Build application: `./build-mac-app.sh` (macOS) or `./build-windows-app.bat` (Windows)

### Testing

Run tests with: `python -m pytest tests/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and bug reports, please open an issue on the project repository.

## Security Notice

This application is designed for parental control purposes and requires appropriate permissions to function. The enhanced screen locking features use system-level APIs that may trigger security warnings. Always ensure you have proper authorization before installing and using this software.