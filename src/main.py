from typer import Typer, Argument, Option, confirm

from time import time
from rich import print
from pathlib import Path

from builder.builder import build_lpack
from builder.callback import Callback as BuildCallback

from installer.callback import Callback as InstallCallback
from installer.installer import install_lpack

from remover.remover import remove_lpk
from remover.callback import Callback as RemoveCallback

try: from searcher import search_all, search_one
except ImportError: from .searcher import search_all, search_one


app: Typer = Typer(add_completion=False)


@app.callback()
def main():
    pass


@app.command(help="Build .lpk from manifest.lpack")
def build(
    base_path: str = Argument(
        ".", help="The path to the folder in which manifest.lpack exists."
    ),
    silent: bool = Option(False, "--silent", "-s", help="Do not print any output."),
):
    class Call(BuildCallback):
        def __init__(self):
            super().__init__()

        def on_some_info(self, msg):
            print(
                f"[bright_blue][INFO][/bright_blue] [bright_white]{msg}[/bright_white]"
            )

        def on_some_warn(self, msg):
            print(
                f"[bright_yellow][WARNING][/bright_yellow] [bright_white]{msg}[/bright_white]"
            )

        def on_some_success(self, msg):
            print(
                f"[bright_green][SUCCESS][/bright_green] [bright_white]{msg}[/bright_white]"
            )

        def on_some_error(self, msg):
            print(
                f"[bright_red][ERROR][/bright_red] [bright_white]{msg}[/bright_white]"
            )

        def on_unknow_error(self, msg):
            print(
                f"[bright_red][ERROR] [bright_white]{msg}[/bright_white][/bright_red]"
            )

    call: Call = BuildCallback() if silent else Call()
    start = time()
    call.on_some_info("Starting building...")
    build_lpack(Path(base_path), call)
    if not call.errored:
        call.on_some_success(
            f"Build was successfull in [bright_cyan]{round(time() - start, 2)}s[/bright_cyan]"
        )


@app.command(help="Installs .lpk cleanly.")
def install(
    pack_path: str = Argument(help="Path to the .lpk file."),
    system_wide: bool = Option(
        False,
        "--system-wide",
        help="Installs package system wide in /usr/bin.\n  NOTE: Elevation is needed.",
    ),
    silent: bool = Option(False, "--silent", "-s", help="Do not print any output."),
):
    class Call(RemoveCallback):
        def __init__(self):
            super().__init__()

        def on_some_info(self, msg):
            print(
                f"[bright_blue][INFO][/bright_blue] [bright_white]{msg}[/bright_white]"
            )

        def on_some_warn(self, msg):
            print(
                f"[bright_yellow][WARNING][/bright_yellow] [bright_white]{msg}[/bright_white]"
            )

        def on_some_success(self, msg):
            print(
                f"[bright_green][SUCCESS][/bright_green] [bright_white]{msg}[/bright_white]"
            )

        def on_some_error(self, msg):
            print(
                f"[bright_red][ERROR][/bright_red] [bright_white]{msg}[/bright_white]"
            )

        def on_unknow_error(self, msg):
            print(
                f"[bright_red][ERROR] [bright_white]{msg}[/bright_white][/bright_red]"
            )

        def prompt_string(self, msg) -> str:
            return input(f"{msg}: ")

        def prompt_confirm(self, msg, default: bool):
            return confirm(msg, default=default)

    call: Call = InstallCallback() if silent else Call()
    start = time()
    call.on_some_info("Installing...")
    install_lpack(Path(pack_path), system_wide, call)
    if not call.errored:
        call.on_some_success(
            f"Installation was successfull in [bright_cyan]{round(time() - start, 2)}s[/bright_cyan]"
        )


@app.command(help="Uninstall .lpk installed cleanly.")
def remove(
    pack: str = Argument(help="Package id to remove."),
    system_wide: bool = Option(
        False,
        "--system-wide",
        help="Installs package system wide in /usr/bin.\n  NOTE: Elevation is needed.",
    ),
    silent: bool = Option(False, "--silent", "-s", help="Do not print any output."),
):
    class Call(InstallCallback):
        def __init__(self):
            super().__init__()

        def on_some_info(self, msg):
            print(
                f"[bright_blue][INFO][/bright_blue] [bright_white]{msg}[/bright_white]"
            )

        def on_some_warn(self, msg):
            print(
                f"[bright_yellow][WARNING][/bright_yellow] [bright_white]{msg}[/bright_white]"
            )

        def on_some_success(self, msg):
            print(
                f"[bright_green][SUCCESS][/bright_green] [bright_white]{msg}[/bright_white]"
            )

        def on_some_error(self, msg):
            print(
                f"[bright_red][ERROR][/bright_red] [bright_white]{msg}[/bright_white]"
            )

        def on_unknow_error(self, msg):
            print(
                f"[bright_red][ERROR] [bright_white]{msg}[/bright_white][/bright_red]"
            )

        def prompt_string(self, msg) -> str:
            return input(f"{msg}: ")

        def prompt_confirm(self, msg, default: bool):
            return confirm(msg, default=default)

    call: Call = InstallCallback() if silent else Call()
    start = time()
    call.on_some_info("Removing...")
    remove_lpk(pack, system_wide, call)
    if not call.errored:
        call.on_some_success(
            f"Installation was successfull in [bright_cyan]{round(time() - start, 2)}s[/bright_cyan]"
        )

@app.command(help="Search installed packages.")
def search(
    package_name:str|None=Argument(
        None,
        help="Optional package id to inspect."
    ),
    system_wide:bool=Option(
        False,
        "--system-wide",
        help="Search in system wide installed packages."
    ),
):
    start=time()
    try:
        if package_name is None:
            packages=search_all(system_wide)
            if not packages:
                print("[bright_yellow]No packages found.[/bright_yellow]")
                return
            for package,version in packages:
                print(
                    f"[bright_cyan]{package}[/bright_cyan] "
                    f"[bright_white]{version}[/bright_white]"
                )
        else:
            data=search_one(package_name,system_wide)
            print(f"[bright_cyan]Package:[/bright_cyan] [bright_white]{package_name}[/bright_white]")
            print(f"[bright_cyan]Name:[/bright_cyan] [bright_white]{data['name']}[/bright_white]")
            print(f"[bright_cyan]Version:[/bright_cyan] [bright_white]{data['version']}[/bright_white]")
            print(f"[bright_cyan]Description:[/bright_cyan] [bright_white]{data['description']}[/bright_white]")
            print(f"[bright_cyan]Desktop:[/bright_cyan] [bright_white]{data['desktop']}[/bright_white]")
            print(f"[bright_cyan]Symlink:[/bright_cyan] [bright_white]{data['symlink']}[/bright_white]")
        print(
            f"[bright_green][SUCCESS][/bright_green] "
            f"[bright_white]Search completed in "
            f"[bright_cyan]{round(time()-start,2)}s[/bright_cyan][/bright_white]"
        )
    except Exception as err:
        print(f"[bright_red][ERROR][/bright_red] [bright_white]{err}[/bright_white]")


if __name__ == "__main__":
    app()
