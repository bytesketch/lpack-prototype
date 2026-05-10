from pathlib import Path
import json
import os


def _get_paths(system_wide: bool):
    if system_wide:
        if os.geteuid() != 0:
            raise PermissionError("Root permissions required.")
        return (
            Path("/var/lib/lpack/installed"),
            Path("/usr/local/bin"),
            Path("/usr/share/applications"),
        )
    home = Path.home()
    return (
        home / ".lpack" / "installed",
        home / ".local" / "bin",
        home / ".local" / "share" / "applications",
    )


def search_all(system_wide: bool) -> list[tuple[str, str]]:
    install_dir, _, _ = _get_paths(system_wide)
    output = []
    found = set()
    if not install_dir.exists():
        return output
    if not install_dir.is_dir():
        raise NotADirectoryError(f"{install_dir} is not directory.")
    for item in install_dir.iterdir():
        if not item.is_dir():
            continue
        manifest = item / ".manifest.json"
        package = item.name
        version = "unknown"
        if manifest.is_file():
            try:
                with open(manifest) as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    package = data.get("package", package)
                    version = data.get("version", version)
            except:
                pass
        key = (package, version)
        if key in found:
            continue
        found.add(key)
        output.append((package, version))
    return output


def search_one(package: str, system_wide: bool) -> dict[str, str | None]:
    install_dir, bin_dir, desk_dir = _get_paths(system_wide)
    if not isinstance(package, str):
        raise TypeError("Package must be string.")
    if not package.strip():
        raise ValueError("Invalid package name.")
    target = install_dir / package
    if not target.exists():
        raise FileNotFoundError(f"Package '{package}' is not installed.")
    manifest_file = target / ".manifest.json"
    if not manifest_file.is_file():
        raise FileNotFoundError("Manifest missing.")
    with open(manifest_file) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise TypeError("Invalid manifest.")
    result = {
        "name": str(data.get("name", package)),
        "version": str(data.get("version", "unknown")),
        "description": str(data.get("description", "")),
        "desktop": None,
        "symlink": None,
    }
    desktop_file = desk_dir / f"{package}.desktop"
    if desktop_file.exists():
        result["desktop"] = str(desktop_file.resolve())
    if bin_dir.exists():
        for item in bin_dir.iterdir():
            try:
                if item.is_symlink():
                    resolved = item.resolve()
                    if str(resolved).startswith(str(target.resolve())):
                        result["symlink"] = str(item.resolve())
                        break
            except:
                pass
    return result
