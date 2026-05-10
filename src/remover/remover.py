from pathlib import Path
from shutil import rmtree
from .callback import Callback
import json
import os


def remove_lpk(pack_id: str, system_wide: bool, call: Callback):
    try:
        if not isinstance(pack_id, str):
            raise TypeError("Package id must be string.")
        if not pack_id.strip():
            raise ValueError("Invalid package id.")
        if system_wide and os.geteuid() != 0:
            raise PermissionError("Root permissions required.")
        if system_wide:
            install_base = Path("/var/lib/lpack/installed")
            bin_dir = Path("/usr/local/bin")
            desk_dir = Path("/usr/share/applications")
        else:
            home = Path.home()
            install_base = home / ".lpack" / "installed"
            bin_dir = home / ".local" / "bin"
            desk_dir = home / ".local" / "share" / "applications"
        install_dir = install_base / pack_id
        if not install_dir.exists():
            raise FileNotFoundError(f"Package '{pack_id}' is not installed.")
        manifest_file = install_dir / ".manifest.json"
        manifest = {}
        if manifest_file.is_file():
            try:
                with open(manifest_file) as f:
                    manifest = json.load(f)
            except Exception as err:
                call.on_some_warn(f"Failed reading manifest: {err}")
        pkg_name = manifest.get("name", pack_id)
        pkg_ver = manifest.get("version", "unknown")
        if not call.prompt_confirm(f"Remove '{pkg_name}' ({pkg_ver})?", False):
            call.on_some_warn("Removal cancelled.")
            return
        if bin_dir.exists():
            for item in bin_dir.iterdir():
                try:
                    if item.is_symlink():
                        target = item.resolve()
                        if str(target).startswith(str(install_dir.resolve())):
                            if call.prompt_confirm(
                                f"Remove symlink '{item.name}'?", True
                            ):
                                item.unlink()
                                call.on_some_success(f"Removed symlink '{item.name}'")
                except Exception as err:
                    call.on_some_error(f"Failed removing symlink '{item.name}': {err}")
        desktop_file = desk_dir / f"{pack_id}.desktop"
        if desktop_file.exists():
            try:
                if call.prompt_confirm(
                    f"Remove desktop entry '{desktop_file.name}'?", True
                ):
                    desktop_file.unlink()
                    call.on_some_success(f"Removed desktop entry '{desktop_file.name}'")
            except Exception as err:
                call.on_some_error(f"Failed removing desktop entry: {err}")
        try:
            rmtree(install_dir)
            call.on_some_success(f"Removed installation '{install_dir}'")
        except Exception as err:
            raise RuntimeError(f"Failed removing installation directory: {err}")
        try:
            if install_base.exists() and not any(install_base.iterdir()):
                install_base.rmdir()
        except:
            pass
        if not system_wide:
            try:
                if bin_dir.exists() and not any(bin_dir.iterdir()):
                    bin_dir.rmdir()
            except:
                pass
            try:
                if desk_dir.exists() and not any(desk_dir.iterdir()):
                    desk_dir.rmdir()
            except:
                pass
        call.on_some_success(f"Package '{pack_id}' removed successfully.")
    except Exception as err:
        call.on_unknow_error(str(err))
        call.errored = True
