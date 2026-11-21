"""Deprecated aliases of gmsh_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def comp_gmsh_mesh_dict(*args, **kwargs):
    """Deprecated: use gmsh_pyleecan.comp_gmsh_mesh_dict"""
    from .gmsh_pyleecan import gmsh_pyleecan

    warn(
        "comp_gmsh_mesh_dict is deprecated, use gmsh_pyleecan.comp_gmsh_mesh_dict (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return gmsh_pyleecan.comp_gmsh_mesh_dict(*args, **kwargs)
