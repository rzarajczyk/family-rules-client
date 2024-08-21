@echo off
REM Clear previous builds
echo Clearing previous builds...
rmdir /s /q build
rmdir /s /q dist

REM Create application
echo Creating app...
pyinstaller --log-level=WARN "app-windows.spec"

REM Notify completion
echo Build complete. Check the "dist" folder for the executable.

REM Pause to view the output
pause