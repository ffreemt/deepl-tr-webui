"""Gen html from templates using jinja2."""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from set_loglevel import set_loglevel


t_dir = "templates"
h_dir = "html"

def main():
    """Gen html from templates using jinja2."""
    file_list = ["tab1.html", "tab2.html", "tab3.html",]

    for file in file_list:
        logger.debug(f" {file}: {Path(t_dir, file).exists()}")

if __name__ == "__main__":
    main()
