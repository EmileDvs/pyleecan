"""Alias packages of the class implementation under test (pytest --backend).

The tests of Tests/New import the classes and the functions from two alias
packages, mapped to the implementation selected by ``pytest --backend``:

======================  ==========================  ==============================
alias                   --backend=dataclass         --backend=pydantic
======================  ==========================  ==============================
``backend_classes``     ``pyleecan.Classes_new``    ``pyleecan.Classes_pydantic``
``backend_functions``   ``pyleecan.Functions_new``  ``pyleecan.Functions_pydantic``
``backend_gui``         ``pyleecan.GUI_new``        ``pyleecan.GUI_pydantic``
======================  ==========================  ==============================

An alias module IS the module of the implementation (same object): classes,
isinstance checks and ``mock.patch("backend_functions.x.f")`` behave as with
the real names, which stay importable (cross tests use both implementations).
"""

import importlib
import importlib.abc
import importlib.util
import sys

BACKENDS = {
    "dataclass": {
        "backend_classes": "pyleecan.Classes_new",
        "backend_functions": "pyleecan.Functions_new",
        "backend_gui": "pyleecan.GUI_new",
    },
    "pydantic": {
        "backend_classes": "pyleecan.Classes_pydantic",
        "backend_functions": "pyleecan.Functions_pydantic",
        "backend_gui": "pyleecan.GUI_pydantic",
    },
}
DEFAULT_BACKEND = "dataclass"


class _AliasLoader(importlib.abc.Loader):
    """Loader returning the (imported) module of the implementation."""

    def __init__(self, target):
        self.target = target

    def create_module(self, spec):
        module = importlib.import_module(self.target)
        self._spec = module.__spec__  # Overwritten by the import system
        return module

    def exec_module(self, module):
        module.__spec__ = self._spec  # The module keeps its real identity


class _AliasFinder(importlib.abc.MetaPathFinder):
    """Finder of the alias packages, for the selected implementation."""

    def __init__(self, backend):
        self.backend = backend
        self.mapping = BACKENDS[backend]

    def find_spec(self, fullname, path=None, target=None):
        alias = fullname.partition(".")[0]
        if alias not in self.mapping:
            return None
        real_name = self.mapping[alias] + fullname[len(alias) :]
        if importlib.util.find_spec(real_name) is None:
            return None
        return importlib.util.spec_from_loader(fullname, _AliasLoader(real_name))


def install(backend=DEFAULT_BACKEND):
    """Map the alias packages to the implementation of backend.

    Parameters
    ----------
    backend : str
        "dataclass" or "pydantic"
    """
    if backend not in BACKENDS:
        raise ValueError(f"backend must be one of {sorted(BACKENDS)}: {backend!r}")
    for finder in [f for f in sys.meta_path if isinstance(f, _AliasFinder)]:
        sys.meta_path.remove(finder)
    for name in [n for n in sys.modules if n.partition(".")[0] in BACKENDS[backend]]:
        del sys.modules[name]  # Aliases of another backend
    sys.meta_path.insert(0, _AliasFinder(backend))


def current():
    """Backend of the alias packages ("dataclass" or "pydantic")."""
    for finder in sys.meta_path:
        if isinstance(finder, _AliasFinder):
            return finder.backend
    return None
