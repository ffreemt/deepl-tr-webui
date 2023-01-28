"""Wrap deepl-fastapi with webui2.

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}
json_data = {
    'text': 'test string',
    # 'from_lang': 'string',
    'to_lang': 'zh',
    'description': 'string',
}
response = requests.post('http://localhost:9909/text/', headers=headers, json=json_data)
response.json()

{'q': {'text': 'test string',
  'from_lang': None,
  'to_lang': 'zh',
  'description': 'string'},
 'result': '测试字符串 测试串 测试线 检验串'}
"""
# pylint: disable=invalid-name
# Install WebUI
# pip install --upgrade webui2
import os
import sys
import webbrowser
from itertools import zip_longest
from multiprocessing import Process
from pathlib import Path
from threading import Thread
from time import sleep, time
from types import SimpleNamespace
from typing import Optional

import httpx
import typer

# from deepl_fastapi.run_uvicorn import run_uvicorn
from deepl_scraper_pp2.run_uvicorn import run_uvicorn

from jinja2 import Environment, FileSystemLoader
from loguru import logger
from set_loglevel import set_loglevel
from webui import webui
# from deepl_scraper_pw import deepl_tr

from deepl_tr import __version__

from .httpserver import httpserver  # default port 8909
from .lang_pairs import lang_pairs
from .list2csv import csv2list, list2csv, list2rowdata
from .loadtext import loadtext  # default port 8909

rowData = [
    {"text1": "Toyota", "text2": "Celica", "metric": ""},
    {"text1": "Ford", "text2": "Mondeo", "metric": ""},
    {"text1": "Porsche", "text2": "Boxter", "metric": ""},
]
row_data1 = [
    {"text": ""},
]
row_data2 = [{"text": "", "texttr": ""}]

HTTPSERVER_PORT = 8909
DEEPL_PORT = 9909

URL = f"http://localhost:{HTTPSERVER_PORT}/ag-grid-community.js"
ns = SimpleNamespace(
    httpserver_port=HTTPSERVER_PORT,
    deepl_port=DEEPL_PORT,
    # rowData=rowData,
    active_tab=1,
    version=__version__,
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
    return _.render(ns=ns)


def tablog_html() -> str:
    """Prep html for tablog (log tab)."""
    _ = env.get_template("tablog.html")
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


_ = '''
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
# '''


def close_the_application(evt: webui.event):
    """Close app."""
    del evt
    webui.exit()


def cond_delay(delay=2.5):
    """Delay conditionally for a few secs to prevent quick swap of html tab."""
    flag = False
    while time() - ns.timestamp < 2.5:
        sleep(1e-2)
        print("-", end="", flush=True)
        flag = True
    if flag:
        print("-", flush=True)
    ns.timestamp = time()


def slot_tab1(evt: webui.event):
    """Reveive signal tab1."""
    logger.debug(" tab1 clicked...")
    logger.debug(f" ns.list1: {ns.list1}")
    logger.debug(f" ns.row_data1: {ns.row_data1}")

    # will this prevent "access violation reading" crash?
    cond_delay()

    if ns.active_tab == 1:
        # already in tab1, do nothing
        return

    # save tab2 rg-grid data (if modified) to ns.row_data2

    logger.debug("\t Update display V to tab1 ")

    try:
        _ = tab1_html()
        # check timetamp to prevent 'access violation reading'?

        evt.window.show(_)
        ns.active_tab = 1
    except Exception as exc:
        logger.error(exc)
        logger.exception(exc)
        _ = '''  if Exception occurs, the following wont help
        try:
            evt.window.run_js(
                f"""document.getElementById('log').innerHTML = 'slot_tab1 exc: {exc}';"""
            )
        except Exception as exc:
            logger.error(f"log exc: {exc}")
        # '''


def slot_tab2(evt: webui.event):
    """Reveive signal tab1."""
    logger.debug(" tab2 clicked...")

    logger.debug(f" ns.list2: {ns.list2[:2]}")
    logger.debug(f" ns.row_data2: {row_data2[:2]}")

    cond_delay()

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
        evt.window.show(_)
        ns.active_tab = 2
    except Exception as exc:
        # logger.error(exc)
        logger.exception(exc)


def slot_tab3(evt: webui.event):
    """Reveive signal tab1."""
    logger.debug(" tab3 clicked...")

    cond_delay()

    if ns.active_tab == 3:
        return

    logger.debug("\t Update display V to tab3 ")

    try:
        _ = tab3_html()
        evt.window.show(_)
        ns.active_tab = 3
    except Exception as exc:
        logger.error(exc)

def slot_tablog(evt: webui.event):
    """Reveive signal tab1."""
    logger.debug(" tablog clicked...")

    cond_delay()

    if ns.active_tab == 5:
        return

    logger.debug("\t Update display V to tablog ")

    try:
        _ = tablog_html()
        evt.window.show(_)
        ns.active_tab = 5
    except Exception as exc:
        logger.error(exc)
        return 
    # empty logmsg, do nothing
    if not ns.logmsg.strip():
        return 
        
    # append ns.logmsg and clear ns.logmsg
    res = evt.window.run_js(f"""return document.getElementById("tablog").innerHTML += {ns.logmsg};""")
    # Check for any error
    if res.error is True:
        logger.error("JavaScript Error: " + res.data)
        return

    # success, clear ns.logmsg
    ns.logmsg = ""        


def slot_tab4(evt: webui.event):
    """Reveive signal tab4."""
    logger.debug(" tab4 clicked... exiting")

    cond_delay()

    del evt
    webui.exit()


def slot_repolink(evt: webui.event):
    """Handle id repolink."""
    logger.debug(" repolink in tab3.html clicked...")
    _ = "https://github.com/ffreemt/deepl-tr-webui"
    webbrowser.open(_)


def slot_qqgrlink(evt: webui.event):
    """Handle id repolink."""
    logger.debug(" qqgrlink in tab3.html clicked...")
    _ = "https://jq.qq.com/?_wv=1027&k=XRCplcfg"
    webbrowser.open(_)


def slot_deepl_docs_link(evt: webui.event):
    """Handle id deeplDocsLink."""
    logger.debug(" deeplDocsLink in tab3.html clicked...")
    _ = f"http://localhost:{ns.deepl_port}/docs"
    webbrowser.open(_)


def slot_loadfile(evt: webui.event):
    """Hanlde tab1.html <input type="file"> id loadfile."""
    logger.debug(" input file loadfile (LOAD) clicked...")

    res = evt.window.run_js("""return document.getElementById("filename").value""")
    # Check for any error
    if res.error is True:
        logger.error("JavaScript Error: " + res.data)
        return

    logger.debug(f" cwd: {Path.cwd()}")
    logger.debug(f" res: {res}")
    logger.debug(f" dir(res): {dir(res)}")

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

    lines = [elm for elm in ns.text.splitlines() if elm.strip()]

    # prep for #csvResult1
    ns.list1 = csv2list(list2csv(lines))
    ns.list1.insert(0, ["text"])

    logger.debug(f" ns.list1: {ns.list1[:2]}")
    logger.debug(f" ns.row_data1: {ns.row_data1[:2]}")

    # ns.row_data1 = [dict([elm]) for elm in zip_longest([], lines, fillvalue="text")]
    ns.row_data1 = [dict(zip(ns.list1[0], elm)) for elm in ns.list1[1:]]

    # update ns.list2 ns.row_data2
    ns.list2 = [elm + [""] for elm in ns.list1[1:]]  # remove list1's header
    ns.list2.insert(0, ["text", "texttr"])
    # ns.row_data2 = [dict(zip(['text', 'texttr'], elm0)) for elm0 in ns.list2[1:]]
    ns.row_data2 = [dict(zip(ns.list2[0], elm)) for elm in ns.list2[1:]]

    logger.debug(f" ns.list2: {ns.list2[:2]}")
    logger.debug(f" ns.row_data2: {ns.row_data2[:2]}")

    try:
        _ = tab1_html()
        evt.window.show(_)
    except Exception as exc:
        logger.exception(exc)
        return

    _ = ''' does not quite work
    evt.window.run_js(
        f"""document.querySelector('#csvResult1').value = {list2csv(ns.list1)}"""
    )
    # '''

    try:
        evt.window.run_js(
            f"""document.getElementById('log').innerHTML = 'ns.text[:180]: {ns.text[:180]}';"""
        )
    except Exception as exc:
        logger.exception(exc)

    return

    # code below not executed
    # const path = (window.URL || window.webkitURL).createObjectURL(file);
    res = evt.window.run_js(
        """const file = document.getElementById("filename").value; console.log("file: ", file); return (window.URL || window.webkitURL).createObjectURL(file)"""
    )
    if res.error is True:
        logger.error("JavaScript Error: " + res.data)
        return
    filepath = res.data
    logger.debug(f"filepath: {filepath}")


def slot_saveedit1(evt: webui.event):
    """Handle id:saveEdit1 SaveEdit button in tab1.html.

    Update ns.list1 with gridOptions.api.getDataAsCsv().
        ns.row_data1
        ns.list2
        ns.row_data2
    """
    # save tab1 rg-grid data (if modified) to ns.row_data1/ns.list1 #csvResult1
    #       possible alternative if can be done: save to localstorage?
    #  https://www.ag-grid.com/javascript-data-grid/csv-export/
    #  document.querySelector('#csvResult').value = gridOptions.api.getDataAsCsv();
    # assumc SAVE button presssed, ag-grid table1 save to #csvResult1

    # gridOptions.api.getDataAsCsv(): '"text"\r\n"a"'
    as_csv = evt.window.run_js(f"""return gridOptions.api.getDataAsCsv();""")
    if as_csv.error is True:
        logger.error(f" as_csv.error: {as_csv.data}")
        return
    logger.debug(as_csv.data)

    # update ns.row_data1/ns.list1
    ns.list1 = csv2list(as_csv.data)

    logger.debug(f"ns.list1: {ns.list1}")

    # _ = zip_longest([], [elm[0] for elm in ns.list1], fillvalue="text")
    # ns.row_data1 = [dict([elm]) for elm in _]
    ns.row_data1 = [dict(zip(ns.list1[0], elm)) for elm in ns.list1[1:]]

    ns.list2 = [elm + [""] for elm in ns.list1[1:]]  # remove list1's header
    ns.list2.insert(0, ["text", "texttr"])
    # ns.row_data2 = [dict(zip(['text', 'texttr'], elm0)) for elm0 in ns.list2[1:]]
    ns.row_data2 = [dict(zip(ns.list2[0], elm)) for elm in ns.list2[1:]]


def slot_saveedit2(evt: webui.event):
    """Handle id:saveEdit2 SaveEdit button in tab2.html.

    Update
        ns.list2 with gridOptions.api.getDataAsCsv().
        ns.row_data2

        ns.list1
        ns.row_data1
    """
    logger.debug("saveEdit clicked in tab2.html")

    as_csv = evt.window.run_js(f"""return gridOptions.api.getDataAsCsv();""")
    if as_csv.error is True:
        logger.error(f" as_csv.error: {as_csv.data}")
        return
    logger.debug(as_csv.data)
    ns.list2 = csv2list(as_csv.data)
    ns.row_data2 = list2rowdata(ns.list2)

    # update ns.list1 with ([['text'] + ns.list2[1:][:, 0]) , ns.rowdata1
    # take col0 of ns.list2[1:]: rotate ns.list2[1:] and wrap in [],
    # and add header [["text"]]
    ns.list1 = [['text']] + [[elm] for elm in [*zip(*ns.list2[1:])][0]]
    ns.row_data1 = list2rowdata(ns.list1)

    logger.debug(f" ns.list1[:3]: {ns.list1[:3]}")
    logger.debug(f" ns.row_data1[:3]: {ns.row_data1[:3]}")


def slot_translate(evt: webui.event) -> str:
    """Handle #translate click.

    Update ns.list1, ns.row_data1, ns.list2, ns.row_data2
    """
    logger.debug(" translate btn in tab2.html clicked ")
    try:
        res = evt.window.run_js(f"""return document.querySelector("#tgtLang").value;""")
        if res.error is True:
            logger.error("JavaScript Error: " + res.data)
            return

        to_lang = lang_pairs.get(res.data)
    except Exception as exc:
        logger.error(exc)
        to_lang = "zh"
    logger.debug(f" to_lang: {to_lang}")

    # rotate ns.list2[:1]
    list2_r = [*zip(*ns.list2[1:])]

    _ = "\n".join(list2_r[0])
    logger.debug(_[:120])

    try:
        res = deepl_tr(_, to_lang=to_lang)
    except Exception as exc:
        # logger.error(exc)
        logger.exception(exc)
        res = str(exc)

    if len(list2_r[0]) != len(res.splitlines()):
        logger.debug(f" some problem (lengths not equal): {len(list2_r[0])}, {len(res.splitlines())}")
    logger.debug(f"translated: {res[:120]}")

    # replace the second col with text_tr
    ns.list2 = [["text", "texttr"]] + [*zip_longest(list2_r[0], res.splitlines(), fillvalue="")]
    ns.row_data2 = list2rowdata(ns.list2)

    logger.debug(f" ns.list2[:10]: {ns.list2[:3]}")
    logger.debug(f" ns.row_data2[:10]: {ns.row_data2[:3]}")

    _ = '''
    try:
        evt.window.run_js(
            f"""document.getElementById('log').innerHTML = 'res[:120]: {res[:120]}';"""
        )
    except Exception as exc:
        logger.exception(exc)
    # '''

    # update tab2 with translated text
    _ = """
    try:
        _ = tab2_html()
        evt.window.show(_)
        ns.active_tab = 2
    except Exception as exc:
        # logger.error(exc)
        logger.exception(exc)
    # """


def deepl_tr(
    text: str,
    from_lang: Optional[str] = "auto",
    to_lang: Optional[str] = "zh",
    timeout: float = 300.,   # for 5000 chars
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> str:
    """Translate using deepl server at port."""
    if from_lang is None:
        from_lang = "auto"
    if to_lang is None:
        to_lang = "zh"
    if port is None:
        port = ns.deepl_port
    if host is None:
        host = "127.0.0.1"
    url = f"http://{host}:{port}/text"
    jdata = {
        "text": text,
        "from_lang": from_lang,
        "to_lang": to_lang,
    }
    try:
        # headers = {'accept': 'application/json', 'Content-Type': 'application/json',}
        res = httpx.post(url, json=jdata, timeout=timeout, follow_redirects=True)
        res.raise_for_status()
    except Exception as exc:
        logger.exception(exc)
        res = {"result": str(exc)}

    return res.json().get("result")


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
):
    """Wrap deepl-fastapi with webui2."""
    # if LOGURU_LEVEL is set use it
    # otherwise set accoding to set_loglevel, default "INFO"/20
    if os.environ.get("LOGURU_LEVEL") is None:
        logger.remove()
        logger.add(sys.stderr, level=set_loglevel())

    logger.debug(f"Now in {os.getcwd()}")

    # start httpserver for tailwindcss/daisyui/ag-grid/fontawesome etc
    Thread(target=httpserver, daemon=True).start()
    # wait for httpserver to be ready
    while True:
        if hasattr(httpserver, "port"):
            ns.httpserver_port = httpserver.port
            ns.cwd.insert(0, Path(httpserver.cwd))
            logger.debug(f" cwd paths: {ns.cwd}")
            logger.debug(f"cwd paths exist: {[elm.exists() for elm in ns.cwd]}")
            ns.logmsg += f"<br />cwd paths exist: {[elm.exists() for elm in ns.cwd]}"
            break
        sleep(0.1)

    # sync deepl-scraper-pw not working
    # switch to
    # _ = """
    # start deepl server, starting port: ns.deepl_port
    start_port = ns.deepl_port
    for offset in range(5):
        port = start_port + offset
        logger.debug(f"attempt {offset + 1} to start deepl-server at port {port}")
        kwargs = dict(port=port)
        proc_deepl = Process(target=run_uvicorn, kwargs=kwargs)
        try:
            proc_deepl.start()  # enable deepl-fastapi
            # update ns
            ns.deepl_port = port
            break
        except Exception as exc:
            logger.error(f"Faild: {exc}")
            continue
    else:
        raise SystemError("Tried 5 times, something is probably wrong...")
    # """

    # http://localhost:8909/ag-grid-community.js
    # loginhtml = login_html(f"http://localhost:{httpserver.port}/ag-grid-community.js")
    loginhtml = login_html()

    # Create a window object
    MyWindow = webui.window()

    # Bind am HTML element ID with a python function
    # MyWindow.bind("CheckPassword", check_the_password)
    MyWindow.bind("Exit", close_the_application)

    MyWindow.bind("tab1", slot_tab1)
    MyWindow.bind("tab2", slot_tab2)
    MyWindow.bind("tab3", slot_tab3)
    MyWindow.bind("tablog", slot_tablog)
    MyWindow.bind("tab4", slot_tab4)

    MyWindow.bind("repolink", slot_repolink)
    MyWindow.bind("qqgrlink", slot_qqgrlink)
    MyWindow.bind("deeplDocsLink", slot_deepl_docs_link)

    MyWindow.bind("loadFile", slot_loadfile)
    MyWindow.bind("saveEdit1", slot_saveedit1)

    MyWindow.bind("saveEdit2", slot_saveedit2)
    MyWindow.bind("translate", slot_translate)

    # Show the window
    # MyWindow.show(login_html)

    # MyWindow.show(loginhtml)
    MyWindow.show(tab1_html())

    # Wait until all windows are closed
    try:
        webui.wait()
    finally:
        if proc_deepl.is_alive():
            proc_deepl.kill()  # not necessary
        typer.echo("Bye.")


if __name__ == "__main__":
    # main()
    app()
