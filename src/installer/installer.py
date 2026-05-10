from pathlib import Path
from shutil import rmtree, copytree
from tempfile import mkdtemp
from zipfile import ZipFile

from .callback import Callback
from .manifest import InstallManifest, InstallDesktop, InstallApp

import json
import os


def deobfuscate(all_bytes: bytes) -> bytes:
    return bytes(
        (((((b >> 3) | (b << 5)) & 0xFF) - 17) & 0xFF) ^ 0x5A for b in all_bytes
    )


def parse_version(ver: str) -> tuple:
    out = []
    for item in ver.split("."):
        try:
            out.append(int(item))
        except:
            out.append(item)
    return tuple(out)


def load_manifest(data: dict) -> InstallManifest:
    if not isinstance(data, dict):
        raise TypeError("Manifest must be dictionary.")
    if "info" not in data:
        raise ValueError("Missing info section.")
    info = data["info"]
    if not isinstance(info, dict):
        raise TypeError("Info must be dictionary.")
    for key in ("package", "name", "version", "description"):
        if key not in info:
            raise ValueError(f"Missing '{key}' in info.")
    man = InstallManifest()
    man.info.package = info["package"]
    man.info.name = info["name"]
    man.info.version = info["version"]
    man.info.description = info["description"]
    if "app" in data:
        app = data["app"]
        if not isinstance(app, dict):
            raise TypeError("App must be dictionary.")
        for key in ("entry", "executable"):
            if key not in app:
                raise ValueError(f"Missing '{key}' in app.")
        base = InstallApp()
        base.entry = app["entry"]
        base.executable = app["executable"]
        man.app = base
    if "desktop" in data:
        desk = data["desktop"]
        if not isinstance(desk, dict):
            raise TypeError("Desktop must be dictionary.")
        for key in ("name", "icon", "exec"):
            if key not in desk:
                raise ValueError(f"Missing '{key}' in desktop.")
        base = InstallDesktop()
        base.name = desk["name"]
        base.icon = desk["icon"]
        base.exec = desk["exec"]
        man.desktop = base
    man.compile()
    return man


def install_lpack(pack: Path, system_wide: bool, call: Callback):
    temp = None
    try:
        pack = Path(pack)
        if not pack.is_file():
            raise FileNotFoundError(f"{pack} not found.")
        if system_wide and os.geteuid() != 0:
            raise PermissionError("Root permissions required.")
        call.on_some_info(f"Installing '{pack.name}'")
        temp = Path(mkdtemp(prefix="lpack_"))
        extract_dir = temp / "extract"
        extract_dir.mkdir(parents=True)
        call.on_some_info(f"Extracting into '{extract_dir}'")
        with ZipFile(pack, "r") as zipf:
            zipf.extractall(extract_dir)
        manifest_file = extract_dir / "manifest"
        if not manifest_file.is_file():
            raise FileNotFoundError("Package manifest missing.")
        with open(manifest_file, "rb") as f:
            raw = f.read()
        manifest = load_manifest(json.loads(deobfuscate(raw).decode("utf-8")))
        call.on_some_success("Manifest loaded.")
        if system_wide:
            base_dir = Path("/var/lib/lpack/installed")
            bin_dir = Path("/usr/local/bin")
            desk_dir = Path("/usr/share/applications")
        else:
            home = Path.home()
            base_dir = home / ".lpack" / "installed"
            bin_dir = home / ".local" / "bin"
            desk_dir = home / ".local" / "share" / "applications"
        install_dir = base_dir / manifest.info.package
        if install_dir.exists():
            info_file = install_dir / ".manifest.json"
            old_ver = None
            if info_file.is_file():
                try:
                    with open(info_file) as f:
                        old_ver = json.load(f)["version"]
                except:
                    pass
            if old_ver is not None:
                old_v = parse_version(old_ver)
                new_v = parse_version(manifest.info.version)
                if new_v < old_v:
                    if not call.prompt_confirm(
                        f"Downgrade {old_ver} -> {manifest.info.version}?", False
                    ):
                        return
                elif new_v == old_v:
                    if not call.prompt_confirm(f"Reinstall version {old_ver}?", True):
                        return
                else:
                    if not call.prompt_confirm(
                        f"Upgrade {old_ver} -> {manifest.info.version}?", True
                    ):
                        return
            else:
                if not call.prompt_confirm("Overwrite existing installation?", False):
                    return
            call.on_some_warn("Removing previous installation.")
            rmtree(install_dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        copytree(extract_dir / "app", install_dir)
        call.on_some_success(f"Installed into '{install_dir}'")
        with open(install_dir / ".manifest.json", "w") as f:
            json.dump(
                {
                    "name": manifest.info.name,
                    "package": manifest.info.package,
                    "version": manifest.info.version,
                    "description": manifest.info.description,
                },
                f,
            )
        if manifest.app is not None:
            bin_dir.mkdir(parents=True, exist_ok=True)
            target = install_dir / manifest.app.executable
            if not target.exists():
                raise FileNotFoundError(
                    f"Executable '{manifest.app.executable}' missing."
                )
            link = bin_dir / manifest.app.entry
            if link.exists() or link.is_symlink():
                link.unlink()
            os.symlink(target.resolve(), link)
            try:
                target.chmod(0o755)
            except:
                pass
            call.on_some_success(f"Linked '{link}'")
        if manifest.desktop is not None:
            desk_dir.mkdir(parents=True, exist_ok=True)
            desktop_file = desk_dir / f"{manifest.info.package}.desktop"
            icon_path = install_dir / manifest.desktop.icon
            with open(desktop_file, "w") as f:
                f.write(
                    "[Desktop Entry]\n"
                    "Version=1.0\n"
                    "Type=Application\n"
                    f"Name={manifest.desktop.name}\n"
                    f"Exec={manifest.desktop.exec}\n"
                    f"Icon={icon_path}\n"
                    "Terminal=false\n"
                    "Categories=Utility;\n"
                )
            call.on_some_success(f"Desktop entry created.")
        call.on_some_success(f"Installed '{manifest.info.name}' successfully.")
    except Exception as err:
        call.on_unknow_error(str(err))
        call.errored = True
    finally:
        if temp is not None and temp.exists():
            try:
                rmtree(temp)
            except:
                pass
