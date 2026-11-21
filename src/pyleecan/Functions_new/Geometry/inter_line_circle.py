"""Deprecated aliases (merged into utils.geometry, removed in Phase 2)."""

from warnings import warn


def inter_line_circle(*args, **kwargs):
    """Deprecated: use utils.geometry.inter_line_circle"""
    from ..utils.geometry import inter_line_circle as function

    warn(
        "inter_line_circle is deprecated, use utils.geometry.inter_line_circle (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
