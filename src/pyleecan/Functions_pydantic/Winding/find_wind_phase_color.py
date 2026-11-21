"""Deprecated alias of Winding.find_wind_phase_color, Winding.get_phase_id (moved to the class, removed in Phase 2)."""

from warnings import warn


def find_wind_phase_color(*args, **kwargs):
    """Deprecated: use Winding.find_wind_phase_color"""
    from ...Classes_pydantic.machine.winding import Winding

    warn(
        "find_wind_phase_color is deprecated, use Winding.find_wind_phase_color (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Winding.find_wind_phase_color(*args, **kwargs)


def get_phase_id(*args, **kwargs):
    """Deprecated: use Winding.get_phase_id"""
    from ...Classes_pydantic.machine.winding import Winding

    warn(
        "get_phase_id is deprecated, use Winding.get_phase_id (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Winding._get_phase_id(*args, **kwargs)
