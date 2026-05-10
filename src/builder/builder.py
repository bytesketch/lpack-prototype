from pathlib import Path
from shutil import rmtree, copy2
from .manifest import Manifest, App, Desktop
from zipfile import ZipFile, ZIP_DEFLATED
from .callback import Callback
import json

"""
def deobfuscate(all_bytes: bytes) -> bytes:
    return bytes((((((b >> 3) | (b << 5)) & 0xFF) - 17) & 0xFF) ^ 0x5A
        for b in all_bytes
    )
"""

def obfuscate(all_bytes: bytes) -> bytes:
    return bytes(((((b ^ 0x5A) + 17) & 0xFF) << 3 | ((((b ^ 0x5A) + 17) & 0xFF) >> 5)) & 0xFF for b in all_bytes)

def compress(target_file, dir, call: Callback):
    dir = Path(dir)
    target_file = Path(target_file)
    call.on_some_info(f"Compressing '{dir}' -> '{target_file.name}'")
    try:
        with ZipFile(target_file, "w", compression=ZIP_DEFLATED, compresslevel=9) as zipf:
            for file in dir.rglob("*"):
                if file.is_file():
                    zipf.write(file, file.relative_to(dir))
                    call.on_some_success(f"Compressed: {file.relative_to(dir)}")
        call.on_some_success(f"Archive created successfully: {target_file}")
    except Exception as err:
        call.on_some_error(f"Failed to compress archive: {err}")

class NotDictionary(Exception):
    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def check_dict(item):
        if not isinstance(item, dict):
            raise NotDictionary("Expected dictionary object.")

def get_field_of_manifest(manifest, key: str) -> object:
    if key in manifest.keys():
        return manifest[key]
    return None

def parse_manifest(manifest) -> Manifest:
    NotDictionary.check_dict(manifest)
    for key in ("package", "build_path", "description"):
        if key not in manifest.keys():
            raise ValueError(f"Required field '{key}' not found.")
    package = get_field_of_manifest(manifest, "package")
    NotDictionary.check_dict(package)
    for key in ("name", "package", "version"):
        if key not in package.keys():
            raise ValueError(f"Required field '{key}' not found in package.")
    base: Manifest = Manifest()
    base.build_base_dir = get_field_of_manifest(manifest, "build_path")
    base.pack.name = get_field_of_manifest(package, "name")
    base.pack.package_name = get_field_of_manifest(package, "package")
    base.pack.version = get_field_of_manifest(package, "version")
    base.pack.authors = get_field_of_manifest(package, "authors")
    base.description = get_field_of_manifest(manifest, "description")
    if "app" in manifest.keys():
        app = get_field_of_manifest(manifest, "app")
        NotDictionary.check_dict(app)
        for key in ("binary", "entry"):
            if key not in app.keys():
                raise ValueError(f"Required field '{key}' not found in app.")
        base_app: App = App()
        base_app.binary = get_field_of_manifest(app, "binary")
        base_app.entry = get_field_of_manifest(app, "entry")
        base.app = base_app
    if "desktop" in manifest.keys():
        desk = get_field_of_manifest(manifest, "desktop")
        NotDictionary.check_dict(desk)
        for key in ("name", "icon", "exec"):
            if key not in desk.keys():
                raise ValueError(f"Required field '{key}' not found in desktop.")
        base_desk: Desktop = Desktop()
        base_desk.name = get_field_of_manifest(desk, "name")
        base_desk.exec = get_field_of_manifest(desk, "exec")
        base_desk.icon = get_field_of_manifest(desk, "icon")
        base.desk = base_desk
    if "include" in manifest.keys():
        base.include = get_field_of_manifest(manifest, "include")
        NotDictionary.check_dict(base.include)
    base.compile()
    return base

def build_lpack(root_dir: Path, call: Callback) -> None:
    try:
        call.on_some_info(f"Starting build in '{root_dir}'")
        if not root_dir.is_dir():
            raise FileNotFoundError(f"{root_dir.resolve()} is not a directory.")
        manifest_file: Path = root_dir / "manifest.lpack"
        if not manifest_file.is_file():
            raise FileNotFoundError("manifest.lpack not found.")
        call.on_some_success("Manifest file found.")
        with open(manifest_file) as conf:
            manifest: Manifest = parse_manifest(json.load(conf))
        call.on_some_success("Manifest parsed successfully.")
        temp: Path = root_dir / "lpack" / "temp"
        if temp.is_dir():
            call.on_some_warn("Previous temp directory exists. Removing.")
            rmtree(temp)
        elif temp.exists():
            call.on_some_warn("Temp path exists as file. Removing.")
            temp.unlink()
        temp.mkdir(parents=True)
        call.on_some_success(f"Created temp directory: {temp}")
        temp_app: Path = temp / "app"
        temp_app.mkdir()
        call.on_some_success(f"Created app directory: {temp_app}")
        build_dir = root_dir / manifest.build_base_dir
        if not build_dir.exists():
            raise FileNotFoundError(f"Build path '{build_dir}' does not exist.")
        call.on_some_info(f"Copying build files from '{build_dir}'")
        for file in build_dir.iterdir():
            try:
                target = temp_app / file.name
                if file.is_file():
                    copy2(file, target)
                    call.on_some_success(f"Copied: {file.name}")
            except Exception as err:
                call.on_some_error(f"Failed to copy '{file}': {err}")
        if manifest.include is not None:
            call.on_some_info("Processing include files.")
            for main_file in manifest.include.keys():
                try:
                    src = root_dir / main_file
                    dst = temp_app / manifest.include[main_file]
                    if not src.exists():
                        call.on_some_error(f"Include file not found: {src}")
                        continue
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    copy2(src, dst)
                    call.on_some_success(f"Included: {src} -> {dst}")
                except Exception as err:
                    call.on_some_error(f"Failed including '{main_file}': {err}")
        final_manifest = {
            "info": {
                "package": manifest.pack.package_name,
                "name": manifest.pack.name,
                "description": manifest.description,
                "version": manifest.pack.version
            }
        }
        if manifest.app is not None:
            final_manifest["app"] = {
                "entry": manifest.app.entry,
                "executable": manifest.app.binary
            }
        if manifest.desk is not None:
            final_manifest["desktop"] = {
                "name": manifest.desk.name,
                "icon": manifest.desk.icon,
                "exec": manifest.desk.exec
            }
        call.on_some_info("Generating obfuscated manifest.")
        data: bytes = obfuscate(json.dumps(final_manifest).encode("utf-8"))
        with open(temp / "manifest", "wb") as f:
            f.write(data)
        call.on_some_success("Manifest generated successfully.")
        build_out: Path = temp.parent / "build"
        build_out.mkdir(exist_ok=True)
        output_file = build_out / f"{final_manifest['info']['name']}-{final_manifest['info']['version']}.lpk"
        compress(output_file, temp, call)
    except Exception as err:
        call.on_unknow_error(str(err))
        call.errored = True
