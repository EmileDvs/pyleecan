"""Deprecated alias of MeshSolution.get_area (moved to the class, removed in Phase 2)."""

from warnings import warn


def get_area(obj, *args, **kwargs):
    """Deprecated: use MeshSolution.get_area"""
    warn(
        "get_area is deprecated, use MeshSolution.get_area (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return obj.get_area(*args, **kwargs)
