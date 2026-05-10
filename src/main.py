from typer import (
    Typer,
    BadParameter,
    Argument,
    Option
)

from time import time
from rich import print
from pathlib import Path

from builder.builder import build_lpack
from builder.callback import Callback as BuildCallback

app: Typer = Typer(add_completion=False)

@app.callback()
def main():
    pass

@app.command()
def build(base_path: str = Argument("."), silent: bool = Option(False, "--silent")):
    class Call(BuildCallback):
        def __init__(self):
            super().__init__()

        def on_some_info(self, msg):
            print(f"[bright_blue][INFO][/bright_blue] [bright_white]{msg}[/bright_white]")
            
        def on_some_warn(self, msg):
            print(f"[bright_yellow][WARNING][/bright_yellow] [bright_white]{msg}[/bright_white]")
            
        def on_some_success(self, msg):
            print(f"[bright_green][SUCCESS][/bright_green] [bright_white]{msg}[/bright_white]")
            
        def on_some_error(self, msg):
            print(f"[bright_red][ERROR][/bright_red] [bright_white]{msg}[/bright_white]")

        def on_unknow_error(self, msg):
            print(f"[bright_red][ERROR] [bright_white]{msg}[/bright_white][/bright_red]")

    call: Call = BuildCallback() if silent else Call() 
    start = time()
    call.on_some_info("Starting building...")
    build_lpack(Path(base_path), call)
    if not call.errored:
        call.on_some_success(f"Build was successfull in [bright_cyan]{round(time() - start, 2)}s[/bright_cyan]")


if __name__ == "__main__":
    app()
