"""Module name of a Pyleecan class and class lookup by name.

Only for the class names known at runtime, e.g. the ``"__class__"`` key of a
serialized object. When the class name is known when writing the code, use a
regular import instead (in a function to avoid an import cycle), that linters
and type checkers can follow::

    from ..geometry.arc_1 import Arc1  # in a class module of another sub-package

The module of a class is derived from its name by ``class_module_name``
(``LamSlotWind`` -> ``lam_slot_wind``): a class must be defined in the module
named accordingly, in one of the sub-packages of its implementation package
(``Classes_new/machine/lam_slot_wind.py``). The sub-package of a module is
found by walking the sub-packages, no generated table is needed.

Each implementation package binds a ``ClassLookup`` to itself in its
``_import`` module.
"""

import re
from importlib import import_module
from keyword import iskeyword
from pathlib import Path

SPECIAL_MODULE_NAMES = {
    "Data1D": "data_1d",
    "OPdq": "op_dq",
    "OPdqf": "op_dqf",
    "OPslip": "op_slip",
    "ScalarProductL2": "scalar_product_l2",
    "XOutput": "xoutput",
}
"""Module names that do not follow the general naming rule"""

NORMALIZATION_CLASS_NAMES = {
    "Norm_ref": "NormRef",
    "Norm_affine": "NormAffine",
    "Norm_func": "NormFunc",
    "Norm_indices": "NormIndices",
    "Norm_vector": "NormVector",
}
"""Legacy name -> name of the renamed classes (still accepted when loading)"""


SUPPORT_CLASSES = {
    # The FEMM handlers kept in OutMagFEMM.handler_list are saved with the
    # legacy support class name
    "_FEMMHandler": ("pyleecan.classes_common.femm_handler", "_FEMMHandler"),
}
"""Serialized support class names ("__class__") -> (module, class), shared
by the class packages (not generated classes)"""


def class_module_name(class_name):
    """Convert a class name to its module name, keeping acronyms together.

    Parameters
    ----------
    class_name : str
        Name of the class (e.g. "LamSlotWind", "EEC_SCIM", "SlotW11_2")

    Returns
    -------
    module_name : str
        Name of the module defining the class (e.g. "lam_slot_wind")

    Raises
    ------
    ValueError
        If no valid module name can be derived from the class name
    """
    if class_name in SPECIAL_MODULE_NAMES:
        return SPECIAL_MODULE_NAMES[class_name]
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", class_name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Za-z])([0-9])", r"\1_\2", name).lower()
    if "LUT" in class_name:
        name = re.sub(r"(^|_)lu_t(?=[a-z])", r"\1lut_", name)
    if iskeyword(name):
        name += "_"
    if not name.isidentifier():
        raise ValueError(f"Cannot derive a Python module name from {class_name!r}")
    return name


def find_module_paths(package_dir):
    """Path of each class module of a class package.

    The class modules are the public modules of the public sub-packages; names
    starting with "_" are support modules or vendored packages.

    Parameters
    ----------
    package_dir : str or Path
        Folder of the class package (e.g. ``Classes_new``)

    Returns
    -------
    module_paths : dict
        {module name: "subpackage.module"} (e.g. {"arc_1": "geometry.arc_1"})

    Raises
    ------
    ImportError
        If a module name is defined in two sub-packages
    """
    paths = {}
    for subpackage in sorted(Path(package_dir).iterdir()):
        if (
            not subpackage.is_dir()
            or subpackage.name.startswith(("_", "."))
            or not (subpackage / "__init__.py").is_file()
        ):
            continue
        for module_file in sorted(subpackage.glob("*.py")):
            module = module_file.stem
            if module.startswith("_"):
                continue
            if module in paths:
                raise ImportError(
                    f"Class module {module!r} is defined in both "
                    f"{paths[module]!r} and {subpackage.name}.{module!r}"
                )
            paths[module] = f"{subpackage.name}.{module}"
    return paths


class ClassLookup:
    """Lookup of the classes of one implementation package by name.

    Parameters
    ----------
    package : str
        Name of the class package (e.g. "pyleecan.Classes_new")
    """

    def __init__(self, package):
        self.package = package
        self._module_paths = None

    def module_paths(self):
        """{module name: "subpackage.module"} of the class modules (cached)."""
        if self._module_paths is None:
            package_dir = Path(import_module(self.package).__file__).parent
            self._module_paths = find_module_paths(package_dir)
        return self._module_paths

    def module_path(self, module_name):
        """Path of a class module in the package ("arc_1" -> "geometry.arc_1").

        Parameters
        ----------
        module_name : str
            Name of the class module (see class_module_name)

        Returns
        -------
        path : str or None
            "subpackage.module", None if there is no such class module
        """
        return self.module_paths().get(module_name)

    def find_class(self, class_name):
        """Return the class defined in the module named after it, or None."""
        if (
            not isinstance(class_name, str)
            or not class_name.isidentifier()
            or class_name.startswith("_")
        ):
            return None
        path = self.module_path(class_module_name(class_name))
        if path is None:
            return None
        target = self.package + "." + path
        try:
            module = import_module(target)
        except ModuleNotFoundError as error:
            if error.name != target:  # Missing dependency of an existing module
                raise
            return None
        cls = getattr(module, class_name, None)
        if not isinstance(cls, type) or cls.__module__ != module.__name__:
            return None
        return cls

    def import_class(self, class_name, prop_name=""):
        """Import a Pyleecan class from its name (legacy names are accepted).

        Parameters
        ----------
        class_name : str
            Name of the class to import
        prop_name : str
            Name of the property being loaded (for the error message)

        Returns
        -------
        cls : type
            The class

        Raises
        ------
        InitUnKnowClassError
            If there is no Pyleecan class with this name
        """
        if class_name in SUPPORT_CLASSES:  # Shared by the class packages
            module_name, name = SUPPORT_CLASSES[class_name]
            return getattr(import_module(module_name), name)
        cls = self.find_class(class_name)
        if cls is None and class_name in NORMALIZATION_CLASS_NAMES:
            cls = self.find_class(NORMALIZATION_CLASS_NAMES[class_name])
        if cls is None:
            from .errors import InitUnKnowClassError

            message = "Unknow class name " + str(class_name)
            if prop_name:
                message += " in init_dict for property " + prop_name
            else:
                message += " when loading"
            raise InitUnKnowClassError(message)
        return cls
