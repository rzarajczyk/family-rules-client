import sys
import subprocess
import platform
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog, QMainWindow, QMessageBox

from AppDb import AppDb
from Installer import Installer, UnregisterInstanceStatus
from gen.ParentConfirm import Ui_ParentConfirm
from gen.SettingsWindow import Ui_SettingsWindow
from osutils import app_data


class CheckPasswordWorker(QThread):
    result_ready = Signal(UnregisterInstanceStatus)

    def __init__(self, username, password):
        super().__init__()
        self.password = password
        self.username = username

    def run(self):
        response = Installer.uninstall(self.username, self.password)
        self.result_ready.emit(response)


class ParentConfirm(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ParentConfirm()
        self.ui.setupUi(self)


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        self.parent_confirm = ParentConfirm()
        self.ui.resetButton.clicked.connect(self.parent_confirm.show)
        self.parent_confirm.accepted.connect(self.check_password)
        self.ui.progressBar.setHidden(True)
        
        # Connect new buttons
        self.ui.openAppDataButton.clicked.connect(self.open_app_data_folder)
        self.ui.clearAppDbButton.clicked.connect(self.clear_app_db)
        
    def check_password(self):
        self.ui.progressBar.setHidden(False)
        username = self.parent_confirm.ui.username.text()
        password = self.parent_confirm.ui.password.text()
        self.worker = CheckPasswordWorker(username, password)
        self.worker.result_ready.connect(self.uninstall_finished)
        self.worker.start()

    def uninstall_finished(self, status):
        if status == UnregisterInstanceStatus.OK:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Uninstall finished")
            msg_box.setText("Uninstall finished.")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(lambda: sys.exit(0))
            msg_box.exec()
        else:
            self.ui.progressBar.setHidden(True)
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Uninstall failed")
            msg_box.setText(f"Uninstall failed\n\n{status}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            ok_button = msg_box.button(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(msg_box.close)
            msg_box.exec()
    
    def open_app_data_folder(self):
        """Open the app data folder in the system file explorer"""
        try:
            app_data_path = app_data()
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(app_data_path)], check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(app_data_path)], check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", str(app_data_path)], check=True)
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Failed to open app data folder\n\n{str(e)}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
    
    def clear_app_db(self):
        """Regenerate the AppDb database with all known applications"""
        try:
            # Create a confirmation dialog
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Confirm Regenerate Database")
            msg_box.setText("Are you sure you want to regenerate the application database? This will clear all cached application information and rebuild it with known applications.")
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                # Clear the AppDb
                app_db = AppDb()
                app_db.cache = {}
                app_db.file.write_text("{}")
                
                # Regenerate with known applications
                self._regenerate_app_db(app_db)
                
                # Show success message
                success_msg = QMessageBox()
                success_msg.setWindowTitle("Success")
                success_msg.setText("Application database regenerated successfully.")
                success_msg.setIcon(QMessageBox.Icon.Information)
                success_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_msg.exec()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Failed to regenerate application database\n\n{str(e)}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
    
    def _regenerate_app_db(self, app_db):
        """Regenerate the AppDb with known applications from AppResolver"""
        from AppResolver import AppResolver
        import os
        import platform
        
        resolver = AppResolver.instance()
        known_apps = {}
        
        # Get known applications based on the OS
        if platform.system() == "Windows":
            # Windows known applications
            known_apps = {
                'chrome.exe': 'Google Chrome',
                'firefox.exe': 'Mozilla Firefox',
                'notepad.exe': 'Notepad',
                'calc.exe': 'Calculator',
                'wmplayer.exe': 'Windows Media Player',
                'winword.exe': 'Microsoft Word',
                'excel.exe': 'Microsoft Excel',
                'powerpnt.exe': 'Microsoft PowerPoint',
                'outlook.exe': 'Microsoft Outlook',
                'explorer.exe': 'Windows Explorer',
                'taskmgr.exe': 'Task Manager',
                'mspaint.exe': 'Paint',
                'cmd.exe': 'Command Prompt',
                'powershell.exe': 'Windows PowerShell',
                'regedit.exe': 'Registry Editor',
                'msedge.exe': 'Microsoft Edge',
                'iexplore.exe': 'Internet Explorer',
                'devenv.exe': 'Visual Studio',
                'code.exe': 'Visual Studio Code',
                'discord.exe': 'Discord',
                'steam.exe': 'Steam',
                'spotify.exe': 'Spotify',
                'vlc.exe': 'VLC Media Player',
                'winrar.exe': 'WinRAR',
                '7zfm.exe': '7-Zip',
                'acrord32.exe': 'Adobe Acrobat Reader',
                'acrobat.exe': 'Adobe Acrobat',
                'photoshop.exe': 'Adobe Photoshop',
                'illustrator.exe': 'Adobe Illustrator',
                'premiere.exe': 'Adobe Premiere Pro',
                'afterfx.exe': 'Adobe After Effects',
                'skype.exe': 'Skype',
                'teams.exe': 'Microsoft Teams',
                'zoom.exe': 'Zoom',
                'slack.exe': 'Slack',
                'telegram.exe': 'Telegram',
                'whatsapp.exe': 'WhatsApp',
                'obs64.exe': 'OBS Studio',
                'obs32.exe': 'OBS Studio',
                'blender.exe': 'Blender',
                'unity.exe': 'Unity',
                'unreal.exe': 'Unreal Engine',
                'minecraft.exe': 'Minecraft',
                'epicgameslauncher.exe': 'Epic Games Launcher',
                'origin.exe': 'Origin',
                'uplay.exe': 'Ubisoft Connect',
                'battle.net.exe': 'Battle.net',
                'gog.exe': 'GOG Galaxy',
                'twitch.exe': 'Twitch',
                'obsidian.exe': 'Obsidian',
                'notion.exe': 'Notion',
                'evernote.exe': 'Evernote',
                'onenote.exe': 'OneNote',
                'dropbox.exe': 'Dropbox',
                'googledrivesync.exe': 'Google Drive',
                'onedrive.exe': 'OneDrive',
                'icloud.exe': 'iCloud',
                'mega.exe': 'MEGA'
            }
        elif platform.system() == "Darwin":  # macOS
            # macOS known applications
            known_apps = {
                'chrome.app': 'Google Chrome',
                'firefox.app': 'Mozilla Firefox',
                'safari.app': 'Safari',
                'textedit.app': 'TextEdit',
                'calculator.app': 'Calculator',
                'preview.app': 'Preview',
                'finder.app': 'Finder',
                'dock.app': 'Dock',
                'system preferences.app': 'System Preferences',
                'activity monitor.app': 'Activity Monitor',
                'terminal.app': 'Terminal',
                'disk utility.app': 'Disk Utility',
                'keychain access.app': 'Keychain Access',
                'system information.app': 'System Information',
                'console.app': 'Console',
                'font book.app': 'Font Book',
                'color sync utility.app': 'ColorSync Utility',
                'digital color meter.app': 'Digital Color Meter',
                'grapher.app': 'Grapher',
                'script editor.app': 'Script Editor',
                'sticky notes.app': 'Sticky Notes',
                'chess.app': 'Chess',
                'dvd player.app': 'DVD Player',
                'quicktime player.app': 'QuickTime Player',
                'photo booth.app': 'Photo Booth',
                'imovie.app': 'iMovie',
                'garageband.app': 'GarageBand',
                'pages.app': 'Pages',
                'numbers.app': 'Numbers',
                'keynote.app': 'Keynote',
                'mail.app': 'Mail',
                'contacts.app': 'Contacts',
                'calendar.app': 'Calendar',
                'reminders.app': 'Reminders',
                'notes.app': 'Notes',
                'messages.app': 'Messages',
                'facetime.app': 'FaceTime',
                'maps.app': 'Maps',
                'weather.app': 'Weather',
                'stocks.app': 'Stocks',
                'news.app': 'News',
                'home.app': 'Home',
                'shortcuts.app': 'Shortcuts',
                'voice memos.app': 'Voice Memos',
                'podcasts.app': 'Podcasts',
                'music.app': 'Music',
                'tv.app': 'TV',
                'books.app': 'Books',
                'app store.app': 'App Store',
                'xcode.app': 'Xcode',
                'visual studio code.app': 'Visual Studio Code',
                'discord.app': 'Discord',
                'steam.app': 'Steam',
                'spotify.app': 'Spotify',
                'vlc.app': 'VLC Media Player',
                'the unarchiver.app': 'The Unarchiver',
                'keka.app': 'Keka',
                'adobe acrobat reader dc.app': 'Adobe Acrobat Reader',
                'adobe acrobat dc.app': 'Adobe Acrobat',
                'adobe photoshop 2024.app': 'Adobe Photoshop',
                'adobe illustrator 2024.app': 'Adobe Illustrator',
                'adobe premiere pro 2024.app': 'Adobe Premiere Pro',
                'adobe after effects 2024.app': 'Adobe After Effects',
                'skype.app': 'Skype',
                'microsoft teams.app': 'Microsoft Teams',
                'zoom.us.app': 'Zoom',
                'slack.app': 'Slack',
                'telegram.app': 'Telegram',
                'whatsapp.app': 'WhatsApp',
                'obs.app': 'OBS Studio',
                'blender.app': 'Blender',
                'unity hub.app': 'Unity Hub',
                'minecraft.app': 'Minecraft',
                'epic games launcher.app': 'Epic Games Launcher',
                'origin.app': 'Origin',
                'ubisoft connect.app': 'Ubisoft Connect',
                'battle.net.app': 'Battle.net',
                'gog galaxy.app': 'GOG Galaxy',
                'twitch.app': 'Twitch',
                'obsidian.app': 'Obsidian',
                'notion.app': 'Notion',
                'evernote.app': 'Evernote',
                'onenote.app': 'OneNote',
                'dropbox.app': 'Dropbox',
                'google drive.app': 'Google Drive',
                'onedrive.app': 'OneDrive',
                'icloud.app': 'iCloud',
                'mega.app': 'MEGA',
                'transmission.app': 'Transmission',
                'qbittorrent.app': 'qBittorrent',
                'deluge.app': 'Deluge'
            }
        
        # Add known applications to the database
        for app_name, display_name in known_apps.items():
            # For Windows, we need to find the actual executable path
            if platform.system() == "Windows":
                # Try common installation paths
                common_paths = [
                    f"C:\\Program Files\\{display_name}\\{app_name}",
                    f"C:\\Program Files (x86)\\{display_name}\\{app_name}",
                    f"C:\\Program Files\\Microsoft\\{display_name}\\{app_name}",
                    f"C:\\Program Files (x86)\\Microsoft\\{display_name}\\{app_name}",
                    f"C:\\Program Files\\Google\\{display_name}\\{app_name}",
                    f"C:\\Program Files (x86)\\Google\\{display_name}\\{app_name}",
                    f"C:\\Program Files\\Mozilla\\{display_name}\\{app_name}",
                    f"C:\\Program Files (x86)\\Mozilla\\{display_name}\\{app_name}",
                    f"C:\\Program Files\\Adobe\\{display_name}\\{app_name}",
                    f"C:\\Program Files (x86)\\Adobe\\{display_name}\\{app_name}",
                    f"C:\\Windows\\System32\\{app_name}",
                    f"C:\\Windows\\{app_name}",
                    f"C:\\Program Files\\{app_name}",
                    f"C:\\Program Files (x86)\\{app_name}"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        # Add to database
                        app_db.cache[path] = {
                            "app_name": display_name,
                            "icon_path": resolver.get_icon(path)
                        }
                        break
            else:  # macOS
                # For macOS, try common application paths
                common_paths = [
                    f"/Applications/{display_name}.app/Contents/MacOS/{display_name}",
                    f"/Applications/{app_name}/Contents/MacOS/{app_name}",
                    f"/System/Applications/{display_name}.app/Contents/MacOS/{display_name}",
                    f"/System/Applications/{app_name}/Contents/MacOS/{app_name}",
                    f"/Applications/Utilities/{display_name}.app/Contents/MacOS/{display_name}",
                    f"/Applications/Utilities/{app_name}/Contents/MacOS/{app_name}"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        # Add to database
                        app_db.cache[path] = {
                            "app_name": display_name,
                            "icon_path": resolver.get_icon(path)
                        }
                        break
        
        # Save the updated database
        with app_db.file.open("w", encoding="utf-8") as f:
            import json
            json.dump(app_db.cache, f, indent=4)
    
