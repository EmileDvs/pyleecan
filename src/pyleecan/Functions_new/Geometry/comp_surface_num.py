"""Deprecated aliases (merged into utils.geometry, removed in Phase 2)."""

from warnings import warn


def comp_surface_num(*args, **kwargs):
    """Deprecated: use utils.geometry.comp_surface_num"""
    from ..utils.geometry import comp_surface_num as function

    warn(
        "comp_surface_num is deprecated, use utils.geometry.comp_surface_num (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
