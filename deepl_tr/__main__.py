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
from itertools import zip_longest

import typer
import webbrowser
from loguru import logger
from webui import webui
from set_loglevel import set_loglevel

from deepl_tr import __version__, deepl_tr
from .httpserver import httpserver  # default port 8909
from .loadtext import loadtext  # default port 8909

row_data1 = [
    {"text": ""},
]
rowData = [
    {"text1": 'Toyota', "text2": 'Celica', "metric": ""},
    {"text1": 'Ford', "text2": 'Mondeo', "metric": ""},
    {"text1": 'Porsche', "text2": 'Boxter', "metric": ""}
]

HTTPSERVER_PORT = 8909
URL = f"http://localhost:{HTTPSERVER_PORT}/ag-grid-community.js"
ns = SimpleNamespace(
    httpserver_port=HTTPSERVER_PORT,
    row_data1=row_data1,
    rowData=rowData,
    active_tab=1,
    version=__version__,
    filename="",
    cwd=[Path("~").expanduser() / "Documents"],
    text="",
)
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


def tab1_html() -> str:
    """Prep html for tab1 (file tab)."""
    _ = env.get_template("tab1.html")
    return _.render(ns=ns)


def tab2_html() -> str:
    """Prep html for tab2 (edit tab)."""
    _ = env.get_template("tab2.html")
    return _.render(ns=ns)


def tab3_html() -> str:
    """Prep html for tab3 (info tab)."""
    _ = env.get_template("tab3.html")
    # _ = env.get_template("tab3a.html")
    return _.render(ns=ns)


def tab3a_html() -> str:
    """Prep html for tab3 (info tab)."""
    # _ = env.get_template("tab3.html")
    _ = env.get_template("tab3a.html")
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


def slot_tab1(evt: webui.event):
    """Reveive signal tab1."""
    logger.debug(" tab1 clicked...")
    if ns.active_tab != 1:
        logger.debug("\t Update display V to tab1 ")
        ns.active_tab = 1
        evt.window.show(tab1_html())

def slot_tab2(evt: webui.event):
    """Reveive signal tab1."""
    logger.debug(" tab2 clicked...")
    if ns.active_tab != 2:
        logger.debug("\t Update display V to tab2 ")
        ns.active_tab = 2
        evt.window.show(tab2_html())


def slot_tab3(evt: webui.event):
    """Reveive signal tab1."""
    logger.debug(" tab3 clicked...")
    if ns.active_tab != 3:
        logger.debug("\t Update display V to tab3 ")
        ns.active_tab = 3
        evt.window.show(tab3_html())
        # evt.window.show(tab3a_html())


def slot_tab4(evt: webui.event):
    """Reveive signal tab1."""
    logger.debug(" tab4 clicked...")
    del evt
    webui.exit()


def slot_repolink(evt: webui.event):
    """Handle id repolink."""
    logger.debug(" repolink clicked...")
    _ = "https://github.com/ffreemt/deepl-tr-webui"
    webbrowser.open(_)


def slot_qqgrlink(evt: webui.event):
    """Handle id repolink."""
    logger.debug(" qqgrlink clicked...")
    _ = "https://jq.qq.com/?_wv=1027&k=XRCplcfg"
    webbrowser.open(_)


def slot_loadfile(evt: webui.event):
    """Hanlde tab1.html <input type="file"> id loadfile."""
    logger.debug(" input file loadfile (Submit) clicked...")

    res = evt.window.run_js("""return document.getElementById("filename").value""")
    # Check for any error
    if res.error is True:
        print("JavaScript Error: " + res.data)
        return

    logger.debug(f" cwd: {Path.cwd()}")

    filename = res.data
    logger.debug(f"filename: {filename}")

    if not filename:
        evt.window.run_js(
            f"""document.getElementById('log').innerHTML = 'No file loaded';"""
        )
        return

    # locate file in ns.cwd: cwd, ~/Documents
    filename = Path(filename).name
    for path_ in ns.cwd:
        filepath = path_ / filename
        if filepath.is_file():
            ns.filename = filepath
            break
    else:
        ns.filename = ""
        logger.info(f" file {filename} not found in {ns.cwd}")
        _ = " or ".join(elm.as_posix() for elm in ns.cwd)
        evt.window.run_js(
            f"""document.getElementById('log').innerHTML = 'File not found in {_}';"""
        )
        return

    ns.text = loadtext(filepath)
    logger.debug(f"ns.text[:80]: {ns.text[:180]}")

    _ = [elm for elm in ns.text.splitlines() if elm.strip()]
    ns.row_data1 = [dict([elm]) for elm in zip_longest([], _, fillvalue="text")]

    evt.window.show(tab1_html())

    evt.window.run_js(
        f"""document.getElementById('log').innerHTML = 'ns.text[:180]: {ns.text[:180]}';"""
    )

    return

    # const path = (window.URL || window.webkitURL).createObjectURL(file);
    res = evt.window.run_js("""const file = document.getElementById("filename").value; console.log("file: ", file); return (window.URL || window.webkitURL).createObjectURL(file)""")
    if res.error is True:
        logger.error("JavaScript Error: " + res.data)
        return
    filepath = res.data
    logger.debug(f"filepath: {filepath}")


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
            ns.cwd.insert(0, Path(httpserver.cwd))
            logger.debug(f" cwd paths: {ns.cwd}")
            logger.debug(f"cwd paths exist: {[elm.exists() for elm in ns.cwd]}")
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

    MyWindow.bind("tab1", slot_tab1)
    MyWindow.bind("tab2", slot_tab2)
    MyWindow.bind("tab3", slot_tab3)
    MyWindow.bind("tab4", slot_tab4)

    MyWindow.bind("repolink", slot_repolink)
    MyWindow.bind("qqgrlink", slot_qqgrlink)

    MyWindow.bind("loadfile", slot_loadfile)

    # Show the window
    # MyWindow.show(login_html)

    # MyWindow.show(loginhtml)
    MyWindow.show(tab1_html())

    # Wait until all windows are closed
    webui.wait()

    print("Bye.")


if __name__ == "__main__":
    # main()
    app()
