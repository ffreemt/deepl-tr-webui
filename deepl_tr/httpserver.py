"""Start http.server using socketserver.TCPServer."""
# pylint: disable=invalid-name, broad-except
import os
import http.server
import socketserver
import threading

from pathlib import Path
from loguru import logger

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_my_headers()

        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def send_my_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")  # cors header


def do_GET(self):
    # self.send_response(200)
    self.send_header("Access-Control-Allow-Origin", "*")
    self.end_headers()


# Handler = http.server.SimpleHTTPRequestHandler
# Handler.do_GET = do_GET

Handler = MyHTTPRequestHandler

PORT = 4301


def httpserver(port: int = 8909):
    """Start http.server using socketserver.TCPServer.

    Args:
        port: inital port to try
    """
    cwd = Path.cwd()
    os.chdir(Path(__file__).parent)

    logger.debug(f" cwd: {Path.cwd()}")

    del cwd
    # try 5 times:
    for attempt in range(5):
        try:
            # local busy port [elm.laddr.port for elm in psutil.net_connections()]
            # probe the port and gc
            _ = socketserver.TCPServer(("", port + attempt), Handler)
            del _
            httpserver.port = port + attempt
            break
        except Exception as exc:
            logger.warning(f"\n\tattempt {attempt + 1} failed: {exc}")
    else:
        logger.warning(" Something is probobaly wrong...")
        raise SystemExit(1)

    with socketserver.TCPServer(("", httpserver.port), Handler) as httpd:
        logger.debug(f" cwd: {Path.cwd()}")
        logger.info(f" Running at port: {httpserver.port}")
        httpd.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=httpserver, args=(PORT,), daemon=True).start()

    while True:
        x = input("Enter a number ")
        logger.info(f"You entered {x}")

        try:
            n = int(x)
        except Exception:
            n = 0
        if n > 100:
            break

    if hasattr(httpserver, "port"):
        logger.info(f"port used: {httpserver.port}")

    logger.info("Bye")
