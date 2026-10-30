import logging
import sys
from os import makedirs
from os.path import abspath, isdir, join
from shutil import rmtree

from matplotlib import use
from packaging.version import Version

from pyleecan.definitions import TEST_DIR

sys.path.append("..")

# check python version for import of pyside2 or pyside6
PYTHON_VERSION = Version(sys.version.split(" ")[0])
if PYTHON_VERSION <= Version("3.9"):
    try:
        from PySide2 import QtCore

        # Use Qt5/Qt6 backend depended on whats installed (PyQt5/PySide2 or PyQt6/PySide6)
        use("qtagg")
    except ImportError:
        use("agg")
elif PYTHON_VERSION > Version("3.9"):
    try:
        from PySide6 import QtCore

        # Use Qt5/Qt6 backend depended on whats installed (PyQt5/PySide2 or PyQt6/PySide6)
        use("qtagg")
    except ImportError:
        use("agg")
else:
    logging.error("Invalid python version %s", sys.version_info)


TEST_DATA_DIR = join(TEST_DIR, "Data")
LOG_DIR = join(TEST_DIR, "logtest.txt")
DOC_DIR = abspath(join(TEST_DIR, "..", "Doc"))

# Set logger for test
x = logging.getLogger("logtest")
x.setLevel(logging.DEBUG)
h = logging.FileHandler(LOG_DIR)
f = logging.Formatter("%(message)s")
h.setFormatter(f)
x.addHandler(h)

# Init the result folder for the test
save_path = join(TEST_DIR, "Results").replace("\\", "/")
if isdir(save_path):  # Delete previous test result
    rmtree(save_path)
# To save all the plot geometry results
save_plot_path = join(save_path, "Plot").replace("\\", "/")
if not isdir(save_plot_path):
    makedirs(save_plot_path)
# To save the validation results
save_validation_path = join(save_path, "Validation").replace("\\", "/")
if not isdir(save_validation_path):
    makedirs(save_validation_path)
# To save the Save/Load .json results
save_load_path = join(save_path, "Save_Load").replace("\\", "/")
if not isdir(save_load_path):
    makedirs(save_load_path)
# To save the GUI results
save_gui_path = join(save_path, "GUI").replace("\\", "/")
if not isdir(save_gui_path):
    makedirs(save_gui_path)
SCHEMATICS_PATH = join(save_plot_path, "Schematics").replace("\\", "/")
if not isdir(SCHEMATICS_PATH):
    makedirs(SCHEMATICS_PATH)
SCHEMATICS_POINT_PATH = join(SCHEMATICS_PATH, "Point").replace("\\", "/")
if not isdir(SCHEMATICS_POINT_PATH):
    makedirs(SCHEMATICS_POINT_PATH)
# To clean all the results at the end of the corresponding test
is_clean_result = False
