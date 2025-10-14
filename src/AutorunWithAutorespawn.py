from pathlib import Path

from pathutils import path_to_str
from osutils import get_os, dist_path, app_data

import logging

from osutils import OperatingSystem


class AutorunWithAutorespawn:
    def install(self):
        pass
    def uninstall(self):
        pass
    @staticmethod
    def instance():
        match get_os():
            case OperatingSystem.MAC_OS:
                return MacOSAutorunWithAutorespawn()
            case OperatingSystem.WINDOWS:
                return WindowsAutorunWithAutorespawn()
            case _ as os:
                raise Exception(f"Unsupported OS: {os}")

class MacOSAutorunWithAutorespawn(AutorunWithAutorespawn):
    def install(self):
        import plistlib
        import subprocess
        path = path_to_str(dist_path() / "Contents" / "MacOS" / "FamilyRules")
        expected_plist_content = {
            "Label": "pl.zarajczyk.family-rules-client",
            "ProgramArguments": [path],
            "RunAtLoad": True,
            "KeepAlive": True,
            "StandardErrorPath": path_to_str(app_data() / "family-rules-client-stderr.log"),
            "StandardOutPath": path_to_str(app_data() / "family-rules-client-stdout.log"),
        }
        launch_agent = Path.home() / "Library" / "LaunchAgents" / "pl.zarajczyk.family-rules-client.plist"

        existing_plist_contents = {}
        if launch_agent.is_file():
            with launch_agent.open("rb") as f:
                existing_plist_contents = plistlib.load(f)

        if existing_plist_contents != expected_plist_content:
            logging.info(f"Installing LaunchAgent {path}")
            with launch_agent.open("wb") as f:
                plistlib.dump(expected_plist_content, f)
            process = subprocess.Popen(
                ["launchctl", "load", launch_agent],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            stdout = process.communicate()
            if process.returncode != 0 or not stdout:
                logging.error(f"'launchctl load' exited with code {process.returncode}, output: {stdout}")

    def uninstall(self):
        import subprocess
        import os
        path = Path.home() / "Library" / "LaunchAgents" / "pl.zarajczyk.family-rules-client.plist"
        process = subprocess.Popen(
            ["launchctl", "unload", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        stdout = process.communicate()
        os.remove(path)
        if process.returncode != 0 or not stdout:
            logging.error(
                f"'launchctl unload' exited with code {process.returncode}, output: {stdout}")

class WindowsAutorunWithAutorespawn(AutorunWithAutorespawn):
    def install(self):
        import datetime
        import os

        app_path = str(dist_path().absolute())
        
        # Create a wrapper script that checks if FamilyRules is already running
        wrapper_script = self._create_wrapper_script(app_path)

        near_future = datetime.datetime.now() + datetime.timedelta(minutes=2)
        near_future_time_str = near_future.strftime("%H:%M")
        near_future_date_str = near_future.strftime("%d/%m/%Y")

        self.__windows_schtasks([
            "schtasks",
            "/create",
            "/tn", f"FamilyRules_{os.getenv('USERNAME')}",
            "/tr", f'wscript.exe "{wrapper_script}"',
            "/sc", "MINUTE",
            "/mo", "1",
            "/st", near_future_time_str,
            "/sd", near_future_date_str,
            "/rl", "LIMITED",
            "/f"
        ])

    def _create_wrapper_script(self, app_path):
        import tempfile
        import os
        from pathutils import path_to_str
        from osutils import app_data
        
        log_file = path_to_str(app_data() / "checker.log")
        
        # Create a VBScript that handles everything - checking and starting FamilyRules
        vbscript_content = f'''Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Log function
Sub WriteLog(message)
    Dim timestamp
    timestamp = Now()
    Dim logEntry
    logEntry = FormatDateTime(timestamp, 2) & " " & FormatDateTime(timestamp, 3) & " - " & message
    
    ' Open log file for appending
    Dim logFile
    Set logFile = objFSO.OpenTextFile("{log_file}", 8, True)
    logFile.WriteLine logEntry
    logFile.Close
End Sub

' Check if FamilyRules is already running
WriteLog "Checking if FamilyRules is running..."

' Use WMI to check for running processes
Set objWMIService = GetObject("winmgmts:\\\\.\\root\\cimv2")
Set colProcesses = objWMIService.ExecQuery("SELECT * FROM Win32_Process WHERE Name = 'FamilyRules.exe'")

If colProcesses.Count > 0 Then
    WriteLog "FamilyRules is already running, skipping start"
Else
    WriteLog "FamilyRules not running, starting application..."
    
    ' Start FamilyRules invisibly
    On Error Resume Next
    objShell.Run """{app_path}""", 0, False
    If Err.Number = 0 Then
        WriteLog "Successfully started FamilyRules"
    Else
        WriteLog "Failed to start FamilyRules: " & Err.Description
    End If
    On Error GoTo 0
End If
'''
        
        # Create VBScript file in app data directory for persistence
        vbscript_file = path_to_str(app_data() / "FamilyRulesWatchdog.vbs")
        
        with open(vbscript_file, 'w') as f:
            f.write(vbscript_content)
        
        return vbscript_file


    def __windows_schtasks(self, cmd):
        import subprocess
        try:
            import locale
            logging.info("Installing scheduled task... " + " ".join(cmd))

            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=False)
            system_encoding = locale.getpreferredencoding()

            if result.returncode == 0:
                logging.info(f"Executed schtasks successfully!")
            else:
                error_output = result.stderr.decode(system_encoding, errors='replace')
                logging.error(f"Error executing schtasks: {error_output}")
        except Exception as e:
            logging.error(f"Error executing schtasks: {e}")


    def uninstall(self):
        import subprocess
        import os
        
        # Delete the scheduled task
        task_name = f"FamilyRules_{os.getenv('USERNAME')}"
        result = subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logging.info(f"Task '{task_name}' deleted successfully.")
        else:
            logging.error(f"Failed to delete task '{task_name}'. Error: {result.stderr}")
        
        # Clean up the wrapper script
        from pathutils import path_to_str
        from osutils import app_data
        vbscript_file = path_to_str(app_data() / "FamilyRulesWatchdog.vbs")
        
        try:
            if os.path.exists(vbscript_file):
                os.remove(vbscript_file)
                logging.info("VBScript wrapper removed successfully.")
        except Exception as e:
            logging.error(f"Failed to remove wrapper script: {e}")