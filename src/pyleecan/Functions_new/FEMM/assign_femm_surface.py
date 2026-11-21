"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def assign_FEMM_surface(*args, **kwargs):
    """Deprecated: use femm_pyleecan.assign_FEMM_surface"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "assign_FEMM_surface is deprecated, use femm_pyleecan.assign_FEMM_surface (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(0)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.assign_FEMM_surface(*args, **kwargs)
