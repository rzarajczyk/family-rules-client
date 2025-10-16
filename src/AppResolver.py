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
        """Extract icon from Windows executable and save as PNG."""
        try:
            import win32gui
            import win32con
            import win32api
            import struct
            import os
            
            # Get the icon from the executable
            large_icon, small_icon = win32gui.ExtractIconEx(exe_path, 0)
            
            if not large_icon and not small_icon:
                return None
            
            # Use the large icon if available, otherwise use small icon
            icon_handle = large_icon[0] if large_icon else small_icon[0]
            
            # Get icon info
            icon_info = win32gui.GetIconInfo(icon_handle)
            hbm = icon_info[3]  # hbmColor
            
            if not hbm:
                # Try to create a simple colored icon as fallback
                return self._create_simple_icon(output_path)
            
            # Get bitmap info
            bmp_info = win32gui.GetObject(hbm)
            width = bmp_info.bmWidth
            height = bmp_info.bmHeight
            
            # Create a device context and bitmap
            hdc = win32gui.CreateCompatibleDC(0)
            hdc_mem = win32gui.CreateCompatibleDC(hdc)
            hbm_mem = win32gui.CreateCompatibleBitmap(hdc, 64, 64)
            win32gui.SelectObject(hdc_mem, hbm_mem)
            
            # Draw the icon to the bitmap, scaled to 64x64
            win32gui.DrawIconEx(hdc_mem, 0, 0, icon_handle, 64, 64, 0, 0, win32con.DI_NORMAL)
            
            # Save as BMP first, then convert to PNG if PIL is available
            bmp_path = str(output_path).replace('.png', '.bmp')
            self._save_bitmap_as_bmp(hdc_mem, hbm_mem, bmp_path)
            
            # Try to convert to PNG if PIL is available
            from PIL import Image
            img = Image.open(bmp_path)
            img.save(output_path, 'PNG')
            os.remove(bmp_path)  # Remove the temporary BMP file

            
            # Clean up
            win32gui.DeleteObject(hbm_mem)
            win32gui.DeleteObject(hbm)
            win32gui.DeleteDC(hdc_mem)
            win32gui.DeleteDC(hdc)
            win32gui.DestroyIcon(icon_handle)
            
            return str(output_path)
            
        except Exception:
            # Fallback: create a simple colored icon
            try:
                return self._create_simple_icon(output_path)
            except Exception:
                return None
    
    def _save_bitmap_as_bmp(self, hdc, hbm, bmp_path: str) -> None:
        """Save a bitmap to BMP file."""
        try:
            import win32gui
            import win32con
            import win32api
            import struct
            
            # Get bitmap info
            bmp_info = win32gui.GetObject(hbm)
            
            # Create BMP file header
            bmp_header = struct.pack('<2sIHHI', b'BM', 0, 0, 0, 54)  # File header
            dib_header = struct.pack('<IIIHHIIIIII', 40, 64, 64, 1, 32, 0, 0, 0, 0, 0, 0)  # DIB header
            
            # Get bitmap bits
            bmp_data = win32gui.GetBitmapBits(hbm, bmp_info.bmWidthBytes * bmp_info.bmHeight)
            
            # Write BMP file
            with open(bmp_path, 'wb') as f:
                f.write(bmp_header)
                f.write(dib_header)
                f.write(bmp_data)
                
        except Exception:
            pass
    
    def _create_simple_icon(self, output_path: str) -> str:
        """Create a simple colored icon as fallback."""
        try:
            # Try to use PIL if available
            try:
                from PIL import Image, ImageDraw
                
                # Create a simple 64x64 icon with a colored background
                img = Image.new('RGBA', (64, 64), (100, 150, 200, 255))
                draw = ImageDraw.Draw(img)
                
                # Draw a simple pattern
                draw.rectangle([8, 8, 56, 56], fill=(255, 255, 255, 255))
                draw.rectangle([16, 16, 48, 48], fill=(50, 100, 150, 255))
                
                img.save(output_path, 'PNG')
                return str(output_path)
                
            except ImportError:
                # If PIL is not available, create a simple BMP file
                return self._create_simple_bmp_icon(output_path)
                
        except Exception:
            return None
    
    def _create_simple_bmp_icon(self, output_path: str) -> str:
        """Create a simple BMP icon without PIL."""
        try:
            import struct
            
            # Create a simple 64x64 BMP with a blue background
            width, height = 64, 64
            bmp_data = b''
            
            # Create pixel data (BGR format for BMP)
            for y in range(height):
                row = b''
                for x in range(width):
                    # Simple pattern: blue background with white square
                    if 8 <= x < 56 and 8 <= y < 56:
                        if 16 <= x < 48 and 16 <= y < 48:
                            row += struct.pack('<BBB', 150, 100, 50)  # Brown square
                        else:
                            row += struct.pack('<BBB', 255, 255, 255)  # White
                    else:
                        row += struct.pack('<BBB', 200, 150, 100)  # Blue background
                bmp_data += row
            
            # BMP file header
            file_size = 54 + len(bmp_data)
            bmp_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
            
            # DIB header
            dib_header = struct.pack('<IIIHHIIIIII', 40, width, height, 1, 24, 0, len(bmp_data), 0, 0, 0, 0)
            
            # Write BMP file
            with open(output_path, 'wb') as f:
                f.write(bmp_header)
                f.write(dib_header)
                f.write(bmp_data)
            
            return str(output_path)
            
        except Exception:
            return None

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