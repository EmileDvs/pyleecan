"""Check of the legacy parent links against the generated rules.

Parent links are a legacy feature (see PLAN.md): the check is shared by the
class implementations until it moves to their legacy layer.
"""

import warnings
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


class ContainerFallbackWarning(PendingDeprecationWarning):
    """A method read its container through the legacy parent links.

    Emitted by ``container_or_parent`` / ``ancestor_with`` when the container
    argument is not given and a parent link provides it. Ignored by default
    in Phase 1 (pending); Phase 2 turns it into a DeprecationWarning, then
    removes the fallback with the parent links. The hand-maintained tests
    (Tests/New) turn it into an error: they pass the containers.
    """


def _warn_fallback(obj, name):
    # stacklevel 4: the caller of the method calling container_or_parent
    warnings.warn(
        f"{type(obj).__name__}: the {name or 'container'} argument is not given, "
        "read from the parent links (deprecated: pass it explicitly)",
        ContainerFallbackWarning,
        stacklevel=4,
    )


def container_or_parent(obj, container, name, depth=1):
    """Container of obj: the given one, else the legacy parent (PLAN.md Step 11)

    The methods reading their container take it as an optional argument; the
    new code passes it, the old calls (``slot.comp_height()``) fall back to the
    parent links. Every fallback goes through this function: Phase 2 adds the
    DeprecationWarning here, then removes the fallback with the parent links.

    Parameters
    ----------
    obj : object
        Object whose method reads its container
    container : object or None
        Container given by the caller (None: the fallback)
    name : str
        Name of the argument (for the Phase 2 warning)
    depth : int
        Number of parent links up to the container (2: ``obj.parent.parent``)

    Returns
    -------
    container : object or None
        The given container, else the ancestor of obj at depth (None if the
        chain is broken)

    Warns
    -----
    ContainerFallbackWarning
        If the container is read from the parent links
    """
    if container is not None:
        return container
    container = obj
    for _ in range(depth):
        container = getattr(container, "parent", None)
        if container is None:
            return None
    _warn_fallback(obj, name)
    return container


def ancestor_with(obj, attribute, container=None, name=None):
    """Container of obj having an attribute: the given one, else the first
    legacy ancestor having it (PLAN.md Step 16)

    For the objects found at different depths (an operating point in an
    input or in a LUT, an equivalent circuit in a model or in an output):
    the parent walk of ``container_or_parent`` with an unknown depth. Phase 2
    adds the same DeprecationWarning here.

    Parameters
    ----------
    obj : object
        Object whose method reads its container
    attribute : str
        Attribute of the container looked for (``"machine"``, ``"simu"``)
    container : object or None
        Container given by the caller (None: the fallback)
    name : str
        Name of the argument (for the Phase 2 warning)

    Returns
    -------
    container : object or None
        The given container, else the closest ancestor of obj having the
        attribute (None if there is none)
    """
    if container is not None:
        return container
    ancestor = getattr(obj, "parent", None)
    while ancestor is not None and not hasattr(ancestor, attribute):
        ancestor = getattr(ancestor, "parent", None)
    if ancestor is not None:
        _warn_fallback(obj, name)
    return ancestor
