from osutils import OperatingSystem, get_os
import logging


class AppResolver:
    def get_name(self, app_path: str) -> str:
        pass

    def get_icon(self, app_path: str) -> str:
        """
        Get the icon path for an application.
        Returns the path to a cached PNG icon file, or None if no icon is available.
        """
        pass

    @staticmethod
    def instance():
        match get_os():
            case OperatingSystem.MAC_OS:
                return MacAppResolver()
            case OperatingSystem.WINDOWS:
                return WinAppResolver()
            case _:
                raise Exception("Unsupported OS for AppResolver")

class WinAppResolver(AppResolver):
    def get_name(self, app_path: str) -> str:
        """
        Extract the actual application name from Windows executable file properties.
        Falls back to basename if unable to read file properties.
        """
        # Try multiple approaches to get the application name
        approaches = [
            self._get_name_from_version_info,
            self._get_name_from_shell_properties,
            self._get_name_from_registry,
            self._get_name_from_known_apps
        ]
        
        for approach in approaches:
            try:
                name = approach(app_path)
                if name and name.strip():
                    return name.strip()
            except Exception:
                continue
        
        # Final fallback to basename
        import os
        basename = os.path.basename(app_path)
        if basename.lower().endswith('.exe'):
            return basename[:-4]
        return basename
    
    def _get_name_from_version_info(self, app_path: str) -> str:
        """Try to get application name from version info."""
        try:
            import win32api
            
            # Get the language and codepage first
            lang_codepage = win32api.GetFileVersionInfo(app_path, "\\VarFileInfo\\Translation")
            if lang_codepage:
                lang, codepage = lang_codepage[0]
                lang_codepage_str = f"{lang:04x}{codepage:04x}"
                
                # Try to get individual string values
                skip_values = ["Aplikacja", "Application", "© Microsoft Corporation", "Copyright", "All rights reserved", "Wszelkie prawa zastrzeżone"]
                
                for key in ["FileDescription", "ProductName"]:
                    try:
                        name = win32api.GetFileVersionInfo(app_path, f"\\StringFileInfo\\{lang_codepage_str}\\{key}")
                        if name and name.strip():
                            # Check if it's a generic value we want to skip
                            if not any(skip_val in name for skip_val in skip_values):
                                return name.strip()
                    except:
                        continue
        except Exception:
            pass
        return None
    
    def _get_name_from_shell_properties(self, app_path: str) -> str:
        """Try to get application name using Windows shell properties."""
        try:
            import win32com.client
            import os
            
            # Create shell application object
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.Namespace(os.path.dirname(app_path))
            file_item = folder.ParseName(os.path.basename(app_path))
            
            # Try different property indices for file description
            for prop_index in [2, 24, 25]:  # File description, Product name, Company
                try:
                    description = folder.GetDetailsOf(file_item, prop_index)
                    if description and description.strip() and description.strip() != "Aplikacja":
                        return description.strip()
                except:
                    continue
                
        except Exception:
            pass
        return None
    
    def _get_name_from_registry(self, app_path: str) -> str:
        """
        Try to get application name from Windows registry.
        """
        try:
            import winreg
            import os
            
            # Get the filename without extension
            filename = os.path.basename(app_path)
            if filename.lower().endswith('.exe'):
                filename = filename[:-4]
            
            # Try to find the application in the registry
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        # Check if this entry matches our executable
                                        if filename.lower() in display_name.lower() or filename.lower() in subkey_name.lower():
                                            return display_name
                                    except FileNotFoundError:
                                        continue
                            except OSError:
                                continue
                except OSError:
                    continue
                    
        except Exception:
            pass
            
        # If registry lookup fails, return None to trigger fallback
        return None
    
    def _get_name_from_known_apps(self, app_path: str) -> str:
        """Try to get application name from a known apps mapping."""
        import os
        basename = os.path.basename(app_path).lower()
        
        # Known application mappings
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
            'mega.exe': 'MEGA',
            'utorrent.exe': 'µTorrent',
            'qbittorrent.exe': 'qBittorrent',
            'transmission.exe': 'Transmission',
            'deluge.exe': 'Deluge',
            'bitcomet.exe': 'BitComet',
            'vuze.exe': 'Vuze',
            'frostwire.exe': 'FrostWire',
            'emule.exe': 'eMule',
            'kazaa.exe': 'Kazaa',
            'limewire.exe': 'LimeWire',
            'bearshare.exe': 'BearShare',
            'ares.exe': 'Ares',
            'winmx.exe': 'WinMX',
            'soulseek.exe': 'Soulseek',
            'dc++.exe': 'DC++',
            'shareaza.exe': 'Shareaza',
            'gnucleus.exe': 'Gnucleus',
            'morpheus.exe': 'Morpheus',
            'napster.exe': 'Napster',
            'grokster.exe': 'Grokster',
            'blubster.exe': 'Blubster',
            'piolet.exe': 'Piolet',
            'manolito.exe': 'Manolito',
            'edonkey.exe': 'eDonkey',
            'overnet.exe': 'Overnet',
            'kademlia.exe': 'Kademlia',
            'fasttrack.exe': 'FastTrack',
            'gnutella.exe': 'Gnutella',
            'opennap.exe': 'OpenNap',
            'scour.exe': 'Scour',
            'audiogalaxy.exe': 'AudioGalaxy',
            'napigator.exe': 'Napigator'
        }
        
        return known_apps.get(basename)
    
    def get_icon(self, app_path: str) -> str:
        """
        Get the icon path for a Windows application.
        Extracts icon from exe file, converts to 64x64 PNG, and caches it.
        """
        try:
            from osutils import app_data
            import os
            import hashlib
            
            # Create icons directory if it doesn't exist
            icons_dir = app_data() / "app_details" / "icons"
            icons_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate a unique but meaningful filename
            app_name = self.get_name(app_path)
            app_hash = hashlib.md5(app_path.encode()).hexdigest()[:8]
            icon_filename = f"{self._sanitize_filename(app_name)}_{app_hash}.png"
            icon_path = icons_dir / icon_filename
            
            # Check if icon already exists in cache
            if icon_path.exists():
                return str(icon_path)
            
            # Extract icon from exe file
            extracted_icon_path = self._extract_icon_from_exe(app_path, icon_path)
            if extracted_icon_path and os.path.exists(extracted_icon_path):
                return str(extracted_icon_path)
            
            return None
            
        except Exception as e:
            logging.warn("Failed to get icon for app", e)
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for use in file system."""
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove extra spaces and limit length
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        return sanitized[:50]  # Limit to 50 characters

    def _extract_icon_from_exe(self, exe_path: str, output_path: str) -> str:
        pass

class MacAppResolver(AppResolver):
    def get_name(self, app_path: str) -> str:
        import os
        return os.path.basename(app_path)
    
    def get_icon(self, app_path: str) -> str:
        """
        Get the icon path for a macOS application.
        For now, returns None as macOS icon extraction is more complex.
        """
        # TODO: Implement macOS icon extraction
        return None