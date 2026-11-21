"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def comp_FEMM_Phi_wind(*args, **kwargs):
    """Deprecated: use femm_pyleecan.comp_FEMM_Phi_wind"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "comp_FEMM_Phi_wind is deprecated, use femm_pyleecan.comp_FEMM_Phi_wind (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(0)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.comp_FEMM_Phi_wind(*args, **kwargs)
