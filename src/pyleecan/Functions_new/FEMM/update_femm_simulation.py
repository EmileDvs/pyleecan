"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def update_FEMM_simulation(*args, **kwargs):
    """Deprecated: use femm_pyleecan.update_FEMM_simulation"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "update_FEMM_simulation is deprecated, use femm_pyleecan.update_FEMM_simulation (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(0)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.update_FEMM_simulation(*args, **kwargs)
