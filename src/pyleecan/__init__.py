import os
import platform

from .loggers import init_default_log

PACKAGE_NAME = "pyleecan"
# User folder (to store machine/materials/config)
if platform.system() == "Windows":
    USER_DIR = os.path.join(os.environ["APPDATA"], PACKAGE_NAME)
    USER_DIR = USER_DIR.replace("\\", "/")
else:
    USER_DIR = os.environ["HOME"] + "/.local/share/" + PACKAGE_NAME

__version__ = "1.5.2"

init_default_log()


def main():
    from sys import argv

    from .run_GUI import run_GUI

    run_GUI(argv)
