"""Deprecated aliases of gmsh_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def get_sliding_band(*args, **kwargs):
    """Deprecated: use gmsh_pyleecan.get_sliding_band"""
    from .gmsh_pyleecan import gmsh_pyleecan

    warn(
        "get_sliding_band is deprecated, use gmsh_pyleecan.get_sliding_band (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return gmsh_pyleecan.get_sliding_band(*args, **kwargs)
