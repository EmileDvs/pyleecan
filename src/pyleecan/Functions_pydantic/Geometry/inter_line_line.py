"""Deprecated aliases (merged into utils.geometry, removed in Phase 2)."""

from warnings import warn


def inter_line_line(*args, **kwargs):
    """Deprecated: use utils.geometry.inter_line_line"""
    from ..utils.geometry import inter_line_line as function

    warn(
        "inter_line_line is deprecated, use utils.geometry.inter_line_line (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)


def find_line_eq(*args, **kwargs):
    """Deprecated: use utils.geometry.find_line_eq"""
    from ..utils.geometry import find_line_eq as function

    warn(
        "find_line_eq is deprecated, use utils.geometry.find_line_eq (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return function(*args, **kwargs)
