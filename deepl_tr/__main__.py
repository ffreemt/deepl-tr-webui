"""Wrap deepl-fastapi with webui2."""
# pylint: disable=invalid-name
# Install WebUI
# pip install --upgrade webui2
import os
import sys
from pathlib import Path
from threading import Thread
from time import sleep
from types import SimpleNamespace
from typing import Optional
from jinja2 import Environment, FileSystemLoader

import typer
from loguru import logger
from webui import webui
from set_loglevel import set_loglevel

from deepl_tr import __version__, deepl_tr
from .httpserver import httpserver  # default port 8909

HTTPSERVER_PORT = 8909
URL = f"http://localhost:{HTTPSERVER_PORT}/ag-grid-community.js"
ns = SimpleNamespace(httpserver_port=HTTPSERVER_PORT)
pdir = Path(__file__).parent
env = Environment(loader=FileSystemLoader(f"{pdir}/templates"))

app = typer.Typer(
    name="deepl-tr",
    add_completion=False,
    help=f"{__doc__}",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{app.info.name} v.{__version__}: {__doc__}")
        raise typer.Exit()


def login_html() -> str:
    """Prep html for login."""
    _ = env.get_template("login.html")
    return _.render(ns=ns)


def dashboard_html() -> str:
    """Prep html for dashboard."""
    _ = env.get_template("dashboard.html")
    return _.render(ns=ns)


def check_the_password(evt: webui.event):
    """Check password.

    This function get called every time the user click on "CheckPassword"
    MyWindow.bind('CheckPassword', check_the_password)
    """
    # Run JavaScript to get the password
    res = evt.window.run_js("""return document.getElementById("MyInput").value""")

    # Check for any error
    if res.error is True:
        print("JavaScript Error: " + res.data)
        return

    # Check the password
    # if res.data == "123456":
    if res.data == "123":
        print("Password is correct.")
        # evt.window.show(dashboard_html)
        # {ns.httpserver_port}
        # url = f"http://localhost:{ns.httpserver_port}/static/ag-grid-community.js"
        evt.window.show(dashboard_html())
    else:
        print("Wrong password: " + res.data)
        evt.window.run_js(
            " document.getElementById('err').innerHTML = 'Sorry. Wrong password'; "
        )


def close_the_application(evt: webui.event):
    """Close app."""
    del evt
    webui.exit()


@app.command()
def main(
    version: Optional[bool] = typer.Option(  # pylint: disable=(unused-argument
        None,
        "--version",
        "-v",
        "-V",
        help="Show version info and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
    host: str = typer.Option(  # pylint: disable=(unused-argument
        "127.0.0.1",
        help="Internal deepl server's IP.",
    ),
    port: int = typer.Option(  # pylint: disable=(unused-argument
        8909,
        "--port",
        "-p",
        help="Internal deepl server's port, change if the default it occupied.",
    ),
):
    """Wrap deepl-fastapi with webui2."""
    # if LOGURU_LEVEL is set use it
    # otherwise set accoding to set_loglevel, default "INFO"/20
    if os.environ.get("LOGURU_LEVEL") is None:
        logger.remove()
        logger.add(sys.stderr, level=set_loglevel())

    logger.debug(f"Now in {os.getcwd()}")

    Thread(target=httpserver, daemon=True).start()

    # restore
    # os.chdir(cwd)
    logger.debug(f"now in {Path.cwd()}")

    # wait for httpserver to be ready
    while True:
        if hasattr(httpserver, "port"):
            ns.httpserver_port = httpserver.port
            break
        sleep(0.1)

    # http://localhost:8909/ag-grid-community.js
    # loginhtml = login_html(f"http://localhost:{httpserver.port}/ag-grid-community.js")
    loginhtml = login_html()

    # Create a window object
    MyWindow = webui.window()

    # Bind am HTML element ID with a python function
    MyWindow.bind("CheckPassword", check_the_password)
    MyWindow.bind("Exit", close_the_application)

    # Show the window
    # MyWindow.show(login_html)
    MyWindow.show(loginhtml)

    # Wait until all windows are closed
    webui.wait()

    print("Bye.")


if __name__ == "__main__":
    # main()
    app()
