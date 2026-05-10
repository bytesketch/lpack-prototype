class InstallPackage:
    def __init__(self):
        self.name: str = ""
        self.package: str = ""
        self.version: str = ""
        self.description: str = ""


class InstallApp:
    def __init__(self):
        self.entry: str = ""
        self.executable: str = ""


class InstallDesktop:
    def __init__(self):
        self.name: str = ""
        self.icon: str = ""
        self.exec: str = ""


class InstallManifest:
    def __init__(self):
        self.info: InstallPackage = InstallPackage()
        self.app: InstallApp | None = None
        self.desktop: InstallDesktop | None = None

    def compile(self):
        if not isinstance(self.info, InstallPackage):
            raise TypeError("Invalid package info.")
        for item in (
            self.info.name,
            self.info.package,
            self.info.version,
            self.info.description,
        ):
            if not isinstance(item, str):
                raise TypeError("Manifest info fields must be strings.")
        if self.app is not None:
            if not isinstance(self.app, InstallApp):
                raise TypeError("Invalid app object.")
            if not isinstance(self.app.entry, str):
                raise TypeError("Invalid app entry.")
            if not isinstance(self.app.executable, str):
                raise TypeError("Invalid executable.")
        if self.desktop is not None:
            if not isinstance(self.desktop, InstallDesktop):
                raise TypeError("Invalid desktop object.")
            for item in (self.desktop.name, self.desktop.icon, self.desktop.exec):
                if not isinstance(item, str):
                    raise TypeError("Desktop fields must be strings.")
