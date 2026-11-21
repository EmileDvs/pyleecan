"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def get_mesh_param(*args, **kwargs):
    """Deprecated: use femm_pyleecan.get_mesh_param"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "get_mesh_param is deprecated, use femm_pyleecan.get_mesh_param (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return femm_pyleecan.get_mesh_param(*args, **kwargs)
