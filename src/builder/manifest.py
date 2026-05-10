class Manifest:
    def __init__(self):
        self.pack: Package = Package()
        self.description: str = "app description"
        self.app: App | None = None
        self.desk: Desktop | None = None
        self.include: dict[str, str] | None = None
        self.build_base_dir: str = "path/to/build/dir"

    def __check_type(self, val, hint):
        if not isinstance(val, hint):
            raise TypeError(
                f"Invalid type detected. Expected {hint}, found {type(val)}."
            )

    def compile(self):
        self.__check_type(self.build_base_dir, str)
        self.__check_type(self.description, str)

        self.__check_type(self.pack, Package)
        self.__check_type(self.pack.name, str)
        self.__check_type(self.pack.package_name, str)
        self.__check_type(self.pack.version, str)
        if not self.pack.authors is None:
            self.__check_type(self.pack.authors, list)
            for item in self.pack.authors:
                self.__check_type(item, str)

        if not self.app is None:
            self.__check_type(self.app, App)
            self.__check_type(self.app.binary, str)
            self.__check_type(self.app.entry, str)

        if not self.desk is None:
            self.__check_type(self.desk, Desktop)
            self.__check_type(self.desk.exec, str)
            self.__check_type(self.desk.icon, str)
            self.__check_type(self.desk.name, str)

        if not self.include is None:
            self.__check_type(self.include, dict)
            for key in self.include.keys():
                self.__check_type(key, str)
                self.__check_type(self.include[key], str)

    @staticmethod
    def example_json() -> str:
        return


"""{
    "build_path": "path/to/build/dir", // REQUIRED

    "package": {                    // REQUIRED
        "name": "app-name",        // For information only
        "package": "example.app", // For unique identification
        "version": "1.0.0",      //
        "authors": []           // OPTIONAL
    },

    "app": {                          // OPTIONAL (But NEEDED to make app available in PATH)
        "binary": "path/to/binary",  // Relative path towards the binary (during building)
        "entry": "app"              // What command to run to run the app
    },

    "desktop": {                   // OPTIONAL
        "name": "App",            //
        "icon": "path/to/icon",  // Relative path towards icon
        "exec": "app --gui"     // What command to run to start desktop app
    },

    "include": {                            // OPTIONAL
        "path/to/include": "path/to/paste" // Relative paths to file or folder.
    }
}"""


class Package:
    def __init__(self):
        self.name: str = "app-name"
        self.package_name: str = "example.app"
        self.version: str = "1.0.0"
        self.authors: list[str] | None = None


class App:
    def __init__(self):
        self.binary: str = "path/to/app"
        self.entry: str = "app"


class Desktop:
    def __init__(self):
        self.name: str = "app"
        self.icon: str = "path/to/icon"
        self.exec: str = "app --gui"
