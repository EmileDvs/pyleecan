"""Deprecated aliases of gmsh_pyleecan methods (removed in Phase 2)."""

from warnings import warn

from .gmsh_pyleecan import tol  # noqa: F401


def draw_surf_line(*args, **kwargs):
    """Deprecated: use gmsh_pyleecan.draw_surf_line"""
    from .gmsh_pyleecan import gmsh_pyleecan

    warn(
        "draw_surf_line is deprecated, use gmsh_pyleecan.draw_surf_line (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return gmsh_pyleecan.draw_surf_line(*args, **kwargs)
