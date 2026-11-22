"""Shared configuration of the tests of the new classes.

``pytest --backend=dataclass|pydantic`` selects the class implementation the
tests import through the ``backend_classes`` / ``backend_functions`` alias
packages (see _backend.py). The default is dataclass.
"""

import os
import shutil
from os.path import dirname, isfile, join
from pathlib import Path

import pytest

from pyleecan.definitions import MAIN_DIR
from pyleecan.Generator.ClassGenerator.New import class_generator
from Tests.New import _backend


def pytest_addoption(parser):
    parser.addoption(
        "--backend",
        choices=sorted(_backend.BACKENDS),
        default=_backend.DEFAULT_BACKEND,
        help="class implementation tested through backend_classes/backend_functions",
    )


def pytest_configure(config):
    # Before the collection: the test modules import the alias packages
    _backend.install(config.getoption("backend"))


def pytest_sessionstart(session):
    """Start the GUI tests on an empty result folder.

    The GUI tests check that their output files do not exist yet
    (``assert not isfile(...)``, ``makedirs``): the files left by a run
    stopped midway made the next run fail. Only ``Results/GUI`` is emptied
    (the legacy tests empty the whole Tests/Results folder at import); under
    pytest-xdist, only by the controller.
    """
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return
    clear_gui_results()


def clear_gui_results(path=None):
    """Empty the result folder of the GUI tests (save_gui_path)."""
    from Tests.New._test_paths import save_gui_path

    path = Path(path or save_gui_path)
    if path.is_dir():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def pytest_report_header(config):
    return f"pyleecan backend: {config.getoption('backend')}"


@pytest.fixture(scope="session")
def backend(request):
    """Class implementation under test ("dataclass" or "pydantic")"""
    return request.config.getoption("backend")


@pytest.fixture(autouse=True)
def legacy_section_classes(monkeypatch):
    """Read the Section helper classes from the legacy package if not copied.

    The File, Variable and MATC classes are defined in the legacy
    Methods/Elmer/Section/__init__.py and are written by the generator in the
    generated section.py module. Tests that generate classes in a temporary
    folder without this legacy file (any generation with the full gen_dict
    prepares Section to collect the shared errors) use the repository one.
    Tests that copy it in their temporary tree keep using their copy.
    """
    read_section_classes = class_generator._section_module_classes

    def section_module_classes(path_to_gen):
        method_package = join(
            dirname(path_to_gen), "Methods", "Elmer", "Section", "__init__.py"
        )
        if not isfile(method_package):
            path_to_gen = join(MAIN_DIR, "Classes_new")
        return read_section_classes(path_to_gen)

    monkeypatch.setattr(
        class_generator, "_section_module_classes", section_module_classes
    )
