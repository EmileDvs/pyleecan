"""Deprecated: the methods take their container as an argument (PLAN.md Step 16),
read with classes_common.parents.container_or_parent (removed in Phase 2)."""

from warnings import warn

from ..classes_common.parents import container_or_parent


def check_parent(obj, Nparent: int) -> bool:
    """Recursively check that the object have the correct number of parent
    For instance: check_parent(stator, 3) will check that
    output.simu.machine.stator exist

    Deprecated: use container_or_parent(obj, None, name, depth=Nparent)

    Parameters
    ----------
    obj :
        A pyleecan object
    Nparent : int
        Number of parent we expect the object to have

    Returns
    -------
    has_parent : bool
        True if the object has N parent
    """
    warn(
        "check_parent is deprecated, the methods take their container as an "
        "argument (classes_common.parents.container_or_parent; removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return container_or_parent(obj, None, "parent", depth=Nparent) is not None
