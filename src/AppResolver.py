from osutils import OperatingSystem, get_os
import logging
from PilLite import Image


class AppResolver:
    def get_name(self, app_path: str) -> str:
        pass

    def get_icon(self, app_path: str) -> str:
        """
        Get the icon path for an application.
        Returns the path to a cached png icon file, or None if no icon is available.
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
        Extracts icon from exe file, converts to 64x64 png, and caches it.
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
        from icoextract import IconExtractor, IconExtractorError
        import os
        try:
            extractor = IconExtractor(exe_path)
            data = extractor.get_icon(num=0)
            img = Image.open(data)
            img = img.resize((64, 64))
            img.save(output_path, 'png')

            # Verify the file was created
            if not os.path.exists(output_path):
                raise Exception(f"Failed to save icon to {output_path}")

            return output_path
        except IconExtractorError as e:
            logging.warn(f"Icon extraction failed for {exe_path}", e)
            return None

class MacAppResolver(AppResolver):
    def get_name(self, app_path: str) -> str:
        """
        Extract the actual application name from macOS application bundle.
        app_path is the path to the executable, not the .app bundle.
        Falls back to basename if unable to read bundle properties.
        """
        # First, try to find the app bundle from the executable path
        app_bundle_path = self._find_app_bundle_from_executable(app_path)
        
        # Try multiple approaches to get the application name
        approaches = [
            lambda path: self._get_name_from_info_plist(app_bundle_path) if app_bundle_path else None,
            lambda path: self._get_name_from_bundle_display_name(app_bundle_path) if app_bundle_path else None,
            lambda path: self._get_name_from_known_apps(app_path),
            lambda path: self._get_name_from_basename(app_path)
        ]
        
        for approach in approaches:
            try:
                name = approach(app_path)
                if name and name.strip():
                    return name.strip()
            except Exception:
                continue

        return None
    
    def _find_app_bundle_from_executable(self, executable_path: str) -> str:
        """
        Find the .app bundle path from the executable path.
        Returns None if not found or if the executable is not in an app bundle.
        """
        try:
            import os
            
            # Start from the executable path and walk up the directory tree
            current_path = os.path.abspath(executable_path)
            
            while current_path != os.path.dirname(current_path):  # Not at root
                # Check if current directory is an app bundle
                if current_path.endswith('.app'):
                    # Verify it's actually an app bundle by checking for Contents/Info.plist
                    info_plist_path = os.path.join(current_path, 'Contents', 'Info.plist')
                    if os.path.exists(info_plist_path):
                        return current_path
                
                # Move up one directory
                current_path = os.path.dirname(current_path)
            
            return None
            
        except Exception:
            return None
    
    def _get_name_from_info_plist(self, app_bundle_path: str) -> str:
        """Try to get application name from Info.plist."""
        try:
            import plistlib
            import os
            
            # Check if we have a valid app bundle path
            if not app_bundle_path or not app_bundle_path.endswith('.app'):
                return None
                
            info_plist_path = os.path.join(app_bundle_path, 'Contents', 'Info.plist')
            if not os.path.exists(info_plist_path):
                return None
                
            with open(info_plist_path, 'rb') as f:
                plist = plistlib.load(f)
                
            # Try different keys in order of preference
            name_keys = ['CFBundleDisplayName', 'CFBundleName', 'CFBundleExecutable']
            
            for key in name_keys:
                if key in plist and plist[key]:
                    name = plist[key]
                    if isinstance(name, str) and name.strip():
                        return name.strip()
                        
        except Exception:
            pass
        return None
    
    def _get_name_from_bundle_display_name(self, app_bundle_path: str) -> str:
        """Try to get application name using NSBundle."""
        try:
            from Foundation import NSBundle
            import os
            
            if not app_bundle_path or not app_bundle_path.endswith('.app'):
                return None
                
            bundle = NSBundle.bundleWithPath_(app_bundle_path)
            if bundle:
                # Try to get localized display name
                display_name = bundle.localizedInfoDictionary()
                if display_name and 'CFBundleDisplayName' in display_name:
                    return display_name['CFBundleDisplayName']
                    
                # Fallback to bundle name
                bundle_name = bundle.infoDictionary()
                if bundle_name and 'CFBundleName' in bundle_name:
                    return bundle_name['CFBundleName']
                    
        except Exception:
            pass
        return None
    
    def _get_name_from_known_apps(self, app_path: str) -> str:
        """Try to get application name from a known apps mapping."""
        import os
        basename = os.path.basename(app_path).lower()
        
        # Known macOS application mappings
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
            'deluge.app': 'Deluge',
            'bitcomet.app': 'BitComet',
            'vuze.app': 'Vuze',
            'frostwire.app': 'FrostWire',
            'emule.app': 'eMule',
            'kazaa.app': 'Kazaa',
            'limewire.app': 'LimeWire',
            'bearshare.app': 'BearShare',
            'ares.app': 'Ares',
            'winmx.app': 'WinMX',
            'soulseek.app': 'Soulseek',
            'dc++.app': 'DC++',
            'shareaza.app': 'Shareaza',
            'gnucleus.app': 'Gnucleus',
            'morpheus.app': 'Morpheus',
            'napster.app': 'Napster',
            'grokster.app': 'Grokster',
            'blubster.app': 'Blubster',
            'piolet.app': 'Piolet',
            'manolito.app': 'Manolito',
            'edonkey.app': 'eDonkey',
            'overnet.app': 'Overnet',
            'kademlia.app': 'Kademlia',
            'fasttrack.app': 'FastTrack',
            'gnutella.app': 'Gnutella',
            'opennap.app': 'OpenNap',
            'scour.app': 'Scour',
            'audiogalaxy.app': 'AudioGalaxy',
            'napigator.app': 'Napigator'
        }
        
        return known_apps.get(basename)
    
    def _get_name_from_basename(self, app_path: str) -> str:
        """Get name from basename as fallback."""
        import os
        basename = os.path.basename(app_path)
        if basename.endswith('.app'):
            return basename[:-4]
        return basename
    
    def get_icon(self, app_path: str) -> str:
        """
        Get the icon path for a macOS application.
        app_path is the path to the executable, not the .app bundle.
        Extracts icon from app bundle, converts to 64x64 png, and caches it.
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
            
            # Find the app bundle from the executable path
            app_bundle_path = self._find_app_bundle_from_executable(app_path)
            if not app_bundle_path:
                return None
            
            # Extract icon from app bundle
            extracted_icon_path = self._extract_icon_from_app_bundle(app_bundle_path, icon_path)
            if extracted_icon_path and os.path.exists(extracted_icon_path):
                return str(extracted_icon_path)
            
            return None
            
        except Exception as e:
            logging.warning(f"Failed to get icon for app {app_path}: {e}")
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for use in file system."""
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove extra spaces and limit length
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        return sanitized[:50]  # Limit to 50 characters

    def _extract_icon_from_app_bundle(self, app_bundle_path: str, output_path: str) -> str:
        """Extract icon from macOS app bundle and save as png."""
        try:
            import os
            
            # Check if it's an app bundle
            if not app_bundle_path or not app_bundle_path.endswith('.app'):
                return None
                
            # Try to find icon files in the app bundle
            icon_paths = [
                os.path.join(app_bundle_path, 'Contents', 'Resources', 'AppIcon.icns'),
                os.path.join(app_bundle_path, 'Contents', 'Resources', 'app.icns'),
                os.path.join(app_bundle_path, 'Contents', 'Resources', 'icon.icns'),
                os.path.join(app_bundle_path, 'Contents', 'Resources', 'AppIcon.png'),
                os.path.join(app_bundle_path, 'Contents', 'Resources', 'app.png'),
                os.path.join(app_bundle_path, 'Contents', 'Resources', 'icon.png')
            ]
            
            # Also try to get icon from Info.plist
            try:
                import plistlib
                info_plist_path = os.path.join(app_bundle_path, 'Contents', 'Info.plist')
                if os.path.exists(info_plist_path):
                    with open(info_plist_path, 'rb') as f:
                        plist = plistlib.load(f)
                        
                    # Check for icon file in plist
                    if 'CFBundleIconFile' in plist:
                        icon_file = plist['CFBundleIconFile']
                        if not icon_file.endswith('.icns'):
                            icon_file += '.icns'
                        icon_paths.insert(0, os.path.join(app_bundle_path, 'Contents', 'Resources', icon_file))
                        
                    # Check for icon files array
                    if 'CFBundleIconFiles' in plist:
                        for icon_file in plist['CFBundleIconFiles']:
                            if not icon_file.endswith('.icns'):
                                icon_file += '.icns'
                            icon_paths.insert(0, os.path.join(app_bundle_path, 'Contents', 'Resources', icon_file))
                            
            except Exception:
                pass
            
            # Try to find and convert the first available icon
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        img = Image.open(icon_path)
                        img = img.resize((64, 64))
                        img.save(output_path, 'png')
                        
                        # Verify the file was created
                        if os.path.exists(output_path):
                            return output_path
                            
                    except Exception as e:
                        logging.warning(f"Failed to convert icon {icon_path}: {e}")
                        continue
            
            # If no icon found, try to use system icon
            return self._get_system_icon(app_bundle_path, output_path)
            
        except Exception as e:
            logging.warning(f"Icon extraction failed for {app_bundle_path}: {e}")
            return None
    
    def _get_system_icon(self, app_bundle_path: str, output_path: str) -> str:
        """Get system icon for the application."""
        try:
            from AppKit import NSWorkspace, NSImage
            import os
            
            # Get the app bundle identifier
            bundle_id = self._get_bundle_identifier(app_bundle_path)
            if not bundle_id:
                return None
                
            # Get system icon for the bundle
            workspace = NSWorkspace.sharedWorkspace()
            icon = workspace.iconForFile_(app_bundle_path)
            
            if icon:
                # Convert NSImage to PIL Image
                import io
                
                # Get image data
                tiff_data = icon.TIFFRepresentation()
                if tiff_data:
                    # Convert to PIL Image
                    img = Image.open(io.BytesIO(tiff_data))
                    
                    # Resize to 64x64
                    img = img.resize((64, 64))
                    
                    # Save as png
                    img.save(output_path, 'png')
                    
                    return output_path
                    
        except Exception as e:
            logging.warning(f"Failed to get system icon for {app_bundle_path}: {e}")
            return None
    
    def _get_bundle_identifier(self, app_bundle_path: str) -> str:
        """Get bundle identifier from app bundle."""
        try:
            import plistlib
            import os
            
            if not app_bundle_path or not app_bundle_path.endswith('.app'):
                return None
                
            info_plist_path = os.path.join(app_bundle_path, 'Contents', 'Info.plist')
            if not os.path.exists(info_plist_path):
                return None
                
            with open(info_plist_path, 'rb') as f:
                plist = plistlib.load(f)
                
            return plist.get('CFBundleIdentifier')
            
        except Exception:
            return None