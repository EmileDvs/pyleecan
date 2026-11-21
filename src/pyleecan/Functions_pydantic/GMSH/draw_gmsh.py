"""Deprecated aliases of gmsh_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def draw_GMSH(*args, **kwargs):
    """Deprecated: use gmsh_pyleecan.draw_GMSH"""
    from .gmsh_pyleecan import gmsh_pyleecan

    warn(
        "draw_GMSH is deprecated, use gmsh_pyleecan.draw_GMSH (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return gmsh_pyleecan.draw_GMSH(*args, **kwargs)
