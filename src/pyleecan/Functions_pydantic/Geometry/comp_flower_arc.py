"""Deprecated aliases (merged into utils.geometry, removed in Phase 2)."""

from warnings import warn


def comp_flower_arc(*args, **kwargs):
    """Deprecated: use utils.geometry.comp_flower_arc"""
    from ..utils.geometry import comp_flower_arc as function

    warn(
        "comp_flower_arc is deprecated, use utils.geometry.comp_flower_arc (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
