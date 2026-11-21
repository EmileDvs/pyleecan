"""Deprecated aliases of gmsh_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def gen_3D_mesh(*args, **kwargs):
    """Deprecated: use gmsh_pyleecan.gen_3D_mesh"""
    from .gmsh_pyleecan import gmsh_pyleecan

    warn(
        "gen_3D_mesh is deprecated, use gmsh_pyleecan.gen_3D_mesh (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return gmsh_pyleecan.gen_3D_mesh(*args, **kwargs)
