"""Deprecated aliases of gmsh_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def get_air_box(*args, **kwargs):
    """Deprecated: use gmsh_pyleecan.get_air_box"""
    from .gmsh_pyleecan import gmsh_pyleecan

    warn(
        "get_air_box is deprecated, use gmsh_pyleecan.get_air_box (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return gmsh_pyleecan.get_air_box(*args, **kwargs)
