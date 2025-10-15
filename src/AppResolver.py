from osutils import OperatingSystem, get_os


class AppResolver:
    def get_name(self, app_path: str) -> str:
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
        import os
        return os.path.basename(app_path)

class MacAppResolver(AppResolver):
    def get_name(self, app_path: str) -> str:
        import os
        return os.path.basename(app_path)