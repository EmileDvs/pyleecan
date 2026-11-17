"""Deprecated alias of MeshSolution.get_indices_limited (moved to the class, removed in Phase 2)."""

from warnings import warn


def get_indices_limited(obj, *args, **kwargs):
    """Deprecated: use MeshSolution.get_indices_limited"""
    warn(
        "get_indices_limited is deprecated, use MeshSolution.get_indices_limited (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return obj.get_indices_limited(*args, **kwargs)
