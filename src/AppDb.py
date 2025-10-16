from AppResolver import AppResolver
from osutils import app_data


class App:
    def __init__(self, app_path: str, app_name: str, icon_path: str = None):
        self.app_path = app_path
        self.app_name = app_name
        self.icon_path = icon_path

class AppDb:
    def __init__(self):
        self.file = app_data() / "app_details" / "app_db.json"
        self.file.parent.mkdir(parents=True, exist_ok=True)
        if not self.file.exists():
            self.file.write_text("{}")
        self.cache = {}
        with self.file.open("r", encoding="utf-8") as f:
            import json
            self.cache = json.load(f)
        self.resolver = AppResolver.instance()

    def get(self, app_path: str) -> App:
        if app_path not in self.cache:
            app_name = self.resolver.get_name(app_path)
            icon_path = self.resolver.get_icon(app_path)
            self.cache[app_path] = {
                "app_name": app_name,
                "icon_path": icon_path
            }
            with self.file.open("w", encoding="utf-8") as f:
                import json
                json.dump(self.cache, f, indent=4)

        cache_entry = self.cache[app_path]
        return App(app_path, cache_entry["app_name"], cache_entry.get("icon_path"))

    def __getitem__(self, app_path: str) -> App:
        return self.get(app_path)

    def __iter__(self):
        """Iterator that yields App instances for all known apps"""
        for app_path, app_data in self.cache.items():
            app_name = app_data.get("app_name", "Unknown App")
            icon_path = app_data.get("icon_path")
            yield App(app_path, app_name, icon_path)