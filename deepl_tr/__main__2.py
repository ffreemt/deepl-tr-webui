import os
import sys
from time import sleep
from pathlib import Path
from webui import webui
from types import SimpleNamespace
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from set_loglevel import set_loglevel

# from deepl_tr import __version__

row_data1 = [
    {"text": ""},
]
row_data2 = [{"text": "", "texttr": ""}]

# URL = f"http://localhost:{HTTPSERVER_PORT}/ag-grid-community.js"
ns = SimpleNamespace(
    # httpserver_port=HTTPSERVER_PORT,
    # deepl_port=DEEPL_PORT,
    # rowData=rowData,
    # version=__version__,
    active_tab=1,
    filename="",
    cwd=[Path("~").expanduser() / "Documents"],
    text="",
    text2="",
    list1=[["text"], [""]],
    list2=[["text", "texttr"], ["", ""]],
    row_data1=row_data1,
    row_data2=row_data2,
    to_lang="zh",
    debug=False,
    timestamp=0.0,
    logmsg="",
)
if set_loglevel() <= 10:
    ns.debug = True

logger.debug(f" ns.debug: {ns.debug}")

pdir = Path(__file__).parent
env = Environment(loader=FileSystemLoader(f"{pdir}/tmpl"))

import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)
print('Press Ctrl+C to quit\n')


def tab1_html() -> str:
    """Prep html for tab1 (file tab)."""
    _ = env.get_template("tab1.html")
    return _.render(ns=ns)


def tab2_html() -> str:
    """Prep html for tab2 (edit tab)."""
    _ = env.get_template("tab2.html")
    return _.render(ns=ns)

def slot_tab1(evt: webui.event):
    """Reveive signal tab1."""
    print(" tab1 clicked...")
    logger.debug(" tab1 clicked...")

def slot_tab3(evt: webui.event):
    """Reveive signal tab1."""
    print(" tab3 clicked...")
    logger.debug(" tab3 clicked...")

def slot_dummy(evt: webui.event):
    """Reveive signal dummy."""
    print(" dummy clicked...")
    logger.debug(" dummy clicked...")

def slot_dummy1(evt: webui.event):
    """Reveive signal dummy1."""
    print(" dummy1 clicked...")
    logger.debug(" dummy1 clicked...")

def slot_tab2(evt: webui.event):
    """Reveive signal tab2."""
    print(" tab2 clicked...")
    logger.debug(" tab2 clicked...")

    logger.debug(f" ns.list2: {ns.list2[:2]}")
    logger.debug(f" ns.row_data2: {row_data2[:2]}")

    # cond_delay()

    if ns.active_tab == 2:
        # tab2 alreay active, do nothing
        row_data = evt.window.run_js(
            f"""console.log("__main__.py l.181");"""
            f"""const _ = document.querySelector('#myGrid2'); console.log(_); return _;"""
        )
        return

    # logger.debug(f"\t Update display V to tab2, ns: {ns} ")
    logger.debug(f"\t Update display V to tab2 ")

    try:
        _ = tab2_html()
        Path(f"{pdir}/html/tab2.html").write_text(_, encoding="utf8")

        # evt.window.show(_)
        evt.window.open(f"{ns.s_root}/html/tab2.html", webui.browser.chrome)

        ns.active_tab = 2
    except Exception as exc:
        # logger.error(exc)
        logger.exception(exc)


def switch_to_second_page(e : webui.event):
    # This function get called every time
    # the user click on "SwitchToSecondPage" button
    e.window.open("second.html", webui.browser.any)

def close_the_application(e : webui.event):
    print("tab4 alicked")
    # webui.exit()

def main():
    if os.environ.get("LOGURU_LEVEL") is None:
        logger.remove()
        logger.add(sys.stderr, level=set_loglevel())

    logger.debug(f"Now in {os.getcwd()}")

    # Create a window object
    MyWindow = webui.window()

    # Bind am HTML element ID with a python function
    MyWindow.bind('SwitchToSecondPage', switch_to_second_page)
    # MyWindow.bind('Exit', close_the_application)

    MyWindow.bind('tab4', close_the_application)

    MyWindow.bind("tab1", slot_tab1)
    MyWindow.bind("tab2", slot_tab2)
    MyWindow.bind("tab3", slot_tab3)
    MyWindow.bind("dummy", slot_dummy)
    MyWindow.bind("dummy1", slot_dummy1)

    MyWindow.multi_access(True)

    # The root path. Leave it empty to let the WebUI
    # automatically select the current working folder
    root_path = ""
    root_path = "deepl_tr/html"
    root_path = "deepl_tr"
    root_path = Path(__file__).parent.as_posix()

    # Create a new web server using WebUI

    s_root = MyWindow.new_server(root_path)
    ns.s_root = s_root  # need this in daisyui tailwind ag-grid setup

    logger.info(f" s_root: {s_root}")

    # Show a window using the generated URL
    # MyWindow.open(f"{url}/html")
    # MyWindow.open("https://www.google.com")

    # MyWindow.open(f"{s_root}/html", webui.browser.firefox)
    # MyWindow.open(f"{s_root}/html", webui.browser.chrome)
    # MyWindow.open(f"{s_root}/templates/tab1.html", webui.browser.chrome)

    Path(f"{pdir}/html/tab1.html").write_text(tab1_html(), encoding="utf8")
    MyWindow.open(f"{s_root}/html/tab1.html", webui.browser.chrome)

    # MyWindow.show(f"{tab1_html()}")

    # sleep(3)
    # MyWindow.show(tab1_html())

    # Wait until all windows are closed
    webui.wait()

    # --[ Note ]-----------------
    # Add this script to all your .html files:
    # <script src="webui.js"></script>
    # ---------------------------

    print('Bye.')

if __name__ == "__main__":
    main()