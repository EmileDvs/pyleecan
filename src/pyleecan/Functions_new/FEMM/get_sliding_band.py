"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def get_sliding_band(*args, **kwargs):
    """Deprecated: use femm_pyleecan.get_sliding_band"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "get_sliding_band is deprecated, use femm_pyleecan.get_sliding_band (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return femm_pyleecan.get_sliding_band(*args, **kwargs)
