"""Deprecated aliases (merged into utils.geometry, removed in Phase 2)."""

from warnings import warn


def circle_from_3_points(*args, **kwargs):
    """Deprecated: use utils.geometry.circle_from_3_points"""
    from ..utils.geometry import circle_from_3_points as function

    warn(
        "circle_from_3_points is deprecated, use utils.geometry.circle_from_3_points (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
