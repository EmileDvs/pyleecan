"""Deprecated aliases (merged into utils.geometry, removed in Phase 2)."""

from warnings import warn


def cut_lines_between_angles(*args, **kwargs):
    """Deprecated: use utils.geometry.cut_lines_between_angles"""
    from ..utils.geometry import cut_lines_between_angles as function

    warn(
        "cut_lines_between_angles is deprecated, use utils.geometry.cut_lines_between_angles (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
