"""Import a Pyleecan class from its name.

Only for the class names known at runtime, e.g. the ``"__class__"`` key of a
serialized object. When the class name is known when writing the code, use a
regular import instead (in a function to avoid an import cycle), that linters
and type checkers can follow::

    from .arc_1 import Arc1

The module of a class is derived from its name by ``class_module_name``
(``LamSlotWind`` -> ``lam_slot_wind``): a class must be defined in the module
of this package named accordingly.
"""

import re
from importlib import import_module
from keyword import iskeyword

SPECIAL_MODULE_NAMES = {
    "Data1D": "data_1d",
    "OPdq": "op_dq",
    "OPdqf": "op_dqf",
    "OPslip": "op_slip",
    "ScalarProductL2": "scalar_product_l2",
    "XOutput": "xoutput",
}
"""Module names that do not follow the general naming rule"""


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


def _find_class(class_name):
    """Return the class defined in the module named after it, or None."""
    if (
        not isinstance(class_name, str)
        or not class_name.isidentifier()
        or class_name.startswith("_")
    ):
        return None
    target = __package__ + "." + class_module_name(class_name)
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


def _legacy_class_names():
    """Legacy class names of the renamed classes (e.g. Norm_ref -> NormRef)."""
    try:
        from ..Functions_new.Load.retrocompatibility import NORMALIZATION_CLASS_NAMES
    except ModuleNotFoundError:
        return {}
    return NORMALIZATION_CLASS_NAMES


def import_class(class_name, prop_name=""):
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
    cls = _find_class(class_name)
    if cls is None and class_name in _legacy_class_names():
        cls = _find_class(_legacy_class_names()[class_name])
    if cls is None:
        from ._error import InitUnKnowClassError

        message = "Unknow class name " + str(class_name)
        if prop_name:
            message += " in init_dict for property " + prop_name
        else:
            message += " when loading"
        raise InitUnKnowClassError(message)
    return cls


def __getattr__(name):
    """Lazy access to the classes: ``_import.LamSlotWind``."""
    cls = _find_class(name)
    if cls is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return cls
