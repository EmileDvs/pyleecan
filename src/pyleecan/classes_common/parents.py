"""Check of the legacy parent links against the generated rules.

Parent links are a legacy feature (see PLAN.md): the check is shared by the
class implementations until it moves to their legacy layer.
"""

from functools import cache
from importlib import import_module

from .parent_types import PARENT_TYPES


def assert_parent_type(obj, parent, lookup):
    """Check that parent may hold obj, according to PARENT_TYPES.

    The rules of the closest class of the MRO of obj having rules apply.

    Parameters
    ----------
    obj : PyleecanBase
        Object receiving the parent link
    parent : object
        Parent object (None is always accepted)
    lookup : ClassLookup
        Lookup of the class package of obj, to import the parent classes

    Raises
    ------
    TypeError
        If parent is not an instance of the allowed parent classes
    """
    if parent is None:
        return
    rule = _parent_rule(type(obj), lookup)
    if rule is not None and not isinstance(parent, rule[1]):
        raise TypeError(
            f"{rule[0]} parent must be an instance of {rule[2]}, "
            f"or None; got {type(parent).__name__}"
        )


@cache
def _parent_rule(obj_class, lookup):
    """(class name, parent classes, expected names) of the rule of obj_class."""
    module_prefix = lookup.package + "."
    for cls in obj_class.__mro__:
        if not cls.__module__.startswith(module_prefix):
            continue
        # The rules use the class module names (without sub-package)
        key = (cls.__module__.rpartition(".")[2], cls.__name__)
        if key not in PARENT_TYPES:
            continue
        parent_names = PARENT_TYPES[key]
        parent_types = tuple(
            getattr(
                import_module(f"{lookup.package}.{lookup.module_path(module)}"), name
            )
            for module, name in parent_names
        )
        return cls.__name__, parent_types, " or ".join(n for _, n in parent_names)
    return None

