"""Check of the legacy parent links against the generated rules.

Parent links are a legacy feature (see PLAN.md): the check is shared by the
class implementations until it moves to their legacy layer.
"""

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
    module_prefix = lookup.package + "."
    for cls in type(obj).__mro__:
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
        if not isinstance(parent, parent_types):
            expected = " or ".join(name for _, name in parent_names)
            raise TypeError(
                f"{cls.__name__} parent must be an instance of {expected}, "
                f"or None; got {type(parent).__name__}"
            )
        return

