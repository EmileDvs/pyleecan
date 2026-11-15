"""Import a class of this package from its name.

Binding of the shared lookup (``classes_common.class_lookup``) to the classes
of this package; see that module for the rules. Only for the class names known
at runtime (e.g. the ``"__class__"`` key of a serialized object).
"""

from ..classes_common.class_lookup import ClassLookup, class_module_name

LOOKUP = ClassLookup(__package__)
"""Lookup of the classes of this package"""

import_class = LOOKUP.import_class
module_path = LOOKUP.module_path

__all__ = ["LOOKUP", "class_module_name", "import_class", "module_path"]


def __getattr__(name):
    """Lazy access to the classes: ``_import.LamSlotWind``."""
    cls = LOOKUP.find_class(name)
    if cls is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return cls
