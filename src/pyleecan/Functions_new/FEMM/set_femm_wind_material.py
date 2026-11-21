"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def set_FEMM_wind_material(*args, **kwargs):
    """Deprecated: use femm_pyleecan.set_FEMM_wind_material"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "set_FEMM_wind_material is deprecated, use femm_pyleecan.set_FEMM_wind_material (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(0)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.set_FEMM_wind_material(*args, **kwargs)
