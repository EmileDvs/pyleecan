"""Deprecated alias of Winding.shift_wind_mat (moved to the class, removed in Phase 2)."""

from warnings import warn


def shift_wind_mat(*args, **kwargs):
    """Deprecated: use Winding.shift_wind_mat"""
    from ...Classes_new.machine.winding import Winding

    warn(
        "shift_wind_mat is deprecated, use Winding.shift_wind_mat (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Winding.shift_wind_mat(*args, **kwargs)
