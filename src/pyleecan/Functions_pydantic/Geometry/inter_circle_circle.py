"""Deprecated aliases (merged into utils.geometry, removed in Phase 2)."""

from warnings import warn


def inter_circle_circle(*args, **kwargs):
    """Deprecated: use utils.geometry.inter_circle_circle"""
    from ..utils.geometry import inter_circle_circle as function

    warn(
        "inter_circle_circle is deprecated, use utils.geometry.inter_circle_circle (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
