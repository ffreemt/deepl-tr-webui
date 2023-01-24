"""See https://raw.githubusercontent.com/alifcommunity/webui/main/examples/Python/hello_world/main.py."""
# pylint: disable=invalid-name
# Install WebUI
# pip install --upgrade webui2
import os
import sys
from pathlib import Path
from threading import Thread
from time import sleep
from types import SimpleNamespace

from loguru import logger
from set_loglevel import set_loglevel
from webui import webui

from .httpserver import httpserver  # default port 8909

PORT = 8909
URL = f"http://localhost:{PORT}/ag-grid-community.js"
ns = SimpleNamespace(port=PORT)

_ = """
        <script type="text/javascript" charset="utf-8">
            alert(`cwd: ${window.location.pathname}`)
        </script>
    <div id="myGrid" style="height: 100%; width:500px;" class="ag-theme-balham"></div>
"""

aggrid_table = """
    <div id="myGrid" style="height: 200px; width: 100%;" class="ag-theme-balham"></div>
    <script type="text/javascript" charset="utf-8">
const columnDefs = [
  {
    headerName: 'text1',
    field: "text1",
    editable: true,
    flex: 1,
    resizable: true,
    autoHeight: true,
    wrapText: true,
    //cellEditor: 'agLargeTextCellEditor',
    cellEditorPopup: true,
  },
  {
    headerName: 'text2',
    field: "text2",
    editable: true,
    flex: 1,
    resizable: true,
    autoHeight: true,
    wrapText: true,
    cellEditor: 'agLargeTextCellEditor',
  },
  {
    headerName: 'metric',
    field: "metric",
    editable: true,
    width: 59,
  },
]
        const rowData = [
            {text1: 'Toyota', text2: 'Celica', metric: ""},
            {text1: 'Ford', text2: 'Mondeo', metric: ""},
            {text1: 'Porsche', text2: 'Boxter', metric: ""}
        ];
        const gridOptions = {
            columnDefs: columnDefs,
            rowData: rowData
        };
        const eGridDiv = document.querySelector('#myGrid');
        new agGrid.Grid(eGridDiv, gridOptions);
    </script>
"""

# HTML
def login_html(url=URL) -> str:
    return (
        f"""
<!DOCTYPE html>
<html>
    <head>
        <title>deepl-tr-webui</title>

		<meta charSet="UTF-8"/>
		<meta name="viewport" content="width=device-width, initial-scale=1"/>

        <!--link rel="stylesheet" href="http://localhost:8909/static/fontawesome.css" />
        <link rel="stylesheet" href="http://localhost:8909/static/brands.css" />
        <link rel="stylesheet" href="http://localhost:8909/static/solid.css" /-->

        <link rel="stylesheet" href="http://localhost:8909/static/all.css" />
        <script defer src="http://localhost:8909/fontawesome/js/all.js"></script> <!--load all styles -->
		<style media="only screen">
            html, body {{
                height: 100%;
                width: 100%;
                margin: 0;
                box-sizing: border-box;
                -webkit-overflow-scrolling: touch;
            }}

            html {{
                position: absolute;
                top: 0;
                left: 0;
                padding: 0;
                overflow: auto;
            }}

            body {{
                padding: 1rem;
                overflow: auto;
            }}

.full-width-panel {{
  white-space: normal;
  height: 100%;
  width: 100%;
  border: 2px solid grey;
  border-style: ridge;
  box-sizing: border-box;
  padding: 5px;
  background-color: darkgray;
}}

.full-width-flag {{
  float: left;
  padding: 6px;
}}

.full-width-summary {{
  float: left;
  margin-right: 5px;
}}

.full-width-panel label {{
  padding-top: 3px;
  display: inline-block;
  font-size: 12px;
}}

.full-width-center {{
  overflow-y: scroll;
  border: 1px solid grey;
  padding: 2px;
  height: 100%;
  box-sizing: border-box;
  font-family: cursive;
  background-color: #fafafa;
}}

.full-width-center p {{
  margin-top: 0px;
}}
.full-width-title {{
  font-size: 20px;
}}

        </style>

    <!--script src="https://unpkg.com/ag-grid-community/dist/ag-grid-community.js"></script-->
    <!--script src="node_modules/ag-grid-community/dist/ag-grid-community.js"></script-->
    <!--script src="ag-grid-community.min.js"></script-->

    <!--link href="https://cdn.jsdelivr.net/npm/daisyui@2.47.0/dist/full.css" rel="stylesheet" type="text/css" /-->
    <link href="http://localhost:8909/static/daisyui2.47.0.css" rel="stylesheet" type="text/css" />
    <script src="http://localhost:8909/static/tailwind-plugins.css"></script>

    <script src="{url}"></script>
    </head>
    """
        f"""
    <body>
        <!--div class="pros p-2 mx-auto"-->
        <div class="container p-1 mx-auto flex flex-col">
        <!--h1 class="text-slate-500 font-medium">WebUI 2 - Python Example-</h1-->

    <div>
        <span style="font-size: 3em; color: Tomato;">
      <i class="fas fa-user"></i> <!-- uses solid style -->
        </span>
        <span style="font-size: 20px; color: Dodgerblue;">
  <i class="far fa-user"></i> <!-- uses regular style -->
        </span>
        </span>
        <span style="font-size: 20px; color: Dodgerblue;">
  <i class="far fa-search text-7xl text-rose-600 opacity-10 hover:opacity-100"></i> <!-- uses regular style -->
        </span>
        <span style="font-size: 20px; color: Mediumslateblue;">
  <i class="fab fa-github-square"></i> <!-- uses brands style -->
  <i class="fab fa-font-awesome"></i>
        </span>
    <br/>

           <i class="fa fa-fan text-7xl text-green-500"></i>
    <i class="fa fa-user text-[99px] text-indigo-600 hover:text-amber-400"></i>
    <i class="fa-solid fa-search text-9xl text-rose-600 opacity-60 hover:opacity-100"></i>

    <br />
    <i class="fa fa-fish"></i>
  <i class="fa fa-frog"></i>
  <i class="fa fa-user-ninja vanished"></i>
  <i class="fa-brands fa-facebook"></i>
  <i class="fa fa-fish"></i>

    </div>

        {aggrid_table}

       <div>
        <input type="password" id="MyInput" OnKeyUp="document.getElementById('err').innerHTML='&nbsp;';" autocomplete="off">

        <button id="CheckPassword" class="px-4 py-1 text-sm text-purple-600 font-semibold rounded-full border border-purple-200 hover:text-white hover:bg-purple-600 hover:border-transparent focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2">Check Password</button> <button id="Exit" class="px-4 py-1 text-sm text-purple-600 font-semibold rounded-full border border-purple-200 hover:text-white hover:bg-purple-600 hover:border-transparent focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2">Exit</button>

        </div>

        <!-- https://www.kindacode.com/article/using-tailwind-css-with-font-awesome-icons-a-deep-dive/#Font_Awesome -->
        <div class="pl-2 border border-slate-300 rounded-md">
            <label for="email"><i class="fa fa-lock text-gray-500"></i></label>
            <input type="password" id="password" name="password" placeholder="password"
                class="px-2 py-2 w-48 border-0 focus:outline-0" />
        </div>
        <div class="px-2">
    <button class="btn btn-accent btn-outline w-32 font-semibold rounded-full border border-purple-200 hover:text-white hover:text-white hover:bg-purple-600">Button</button>
        </div>

    <button class="btn btn-wide"> btn-wide </button>
    <button class="btn btn-circle"> btn-circle </button>
    <button class="btn btn-square btn-xs loading"> btn-square </button>

    <input type="file" class="file-input file-input-ghost w-full max-w-xs" />
    <input type="file" class="file-input w-full max-w-xs" />

<div class="form-control w-full max-w-xs">
  <label class="label">
    <span class="label-text">Pick a file</span>
    <!--span class="label-text-alt">Alt label</span-->
  </label>
  <input type="file" class="file-input file-input-ghost file-input-accent file-input-bordered w-full max-w-xs" />
  <label class="label">
    <span class="label-text-alt">Alt label</span>
    <span class="label-text-alt">Alt label</span>
  </label>
</div>

    <div id="err" style="color: #dbdd52">&nbsp;</div>

    </div>
    </body>
</html>
"""
    )


def dashboard_html(url=URL) -> str:
    return (
        f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Dashboard</title>
        <script src="{url}"></script>"""
        """<style>
            body {
                color: white;
                background: #0F2027;
                background: -webkit-linear-gradient(to right, #4e99bb, #2c91b5, #07587a);
                background: linear-gradient(to right, #4e99bb, #2c91b5, #07587a);
                text-align: center;
                font-size: 18px;
                font-family: sans-serif;
            }
        </style>
    </head>"""
        f"""<body>
        <h1>Welcome !</h1>
        <br>
         {aggrid_table}
        <br>
    <button id="Exit">Exit</button>
    </body>
</html>
"""
    )


# This function get called every time the user click on "CheckPassword"
# MyWindow.bind('CheckPassword', check_the_password)
def check_the_password(e: webui.event):
    # Run JavaScript to get the password
    res = e.window.run_js("""return document.getElementById("MyInput").value""")

    # Check for any error
    if res.error is True:
        print("JavaScript Error: " + res.data)
        return

    # Check the password
    # if res.data == "123456":
    if res.data == "123":
        print("Password is correct.")
        # e.window.show(dashboard_html)
        # {ns.port}
        url = f"http://localhost:{ns.port}/static/ag-grid-community.js"
        e.window.show(dashboard_html(url))
    else:
        print("Wrong password: " + res.data)
        e.window.run_js(
            " document.getElementById('err').innerHTML = 'Sorry. Wrong password'; "
        )


def close_the_application(e: webui.event):
    webui.exit()


def main():
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
            ns.port = httpserver.port
            break
        sleep(0.1)

    # port = httpserver.port
    # http://localhost:8909/ag-grid-community.js
    loginhtml = login_html(f"http://localhost:{httpserver.port}/ag-grid-community.js")

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
    main()
