"""Deprecated aliases of gmsh_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def get_boundary_condition(*args, **kwargs):
    """Deprecated: use gmsh_pyleecan.get_boundary_condition"""
    from .gmsh_pyleecan import gmsh_pyleecan

    warn(
        "get_boundary_condition is deprecated, use gmsh_pyleecan.get_boundary_condition (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return gmsh_pyleecan.get_boundary_condition(*args, **kwargs)
