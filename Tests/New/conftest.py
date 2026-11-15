"""Shared configuration of the tests of the new classes.

``pytest --backend=dataclass|pydantic`` selects the class implementation the
tests import through the ``backend_classes`` / ``backend_functions`` alias
packages (see _backend.py). The default is dataclass.
"""

from os.path import dirname, isfile, join

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
