"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def draw_FEMM_surfaces(*args, **kwargs):
    """Deprecated: use femm_pyleecan.draw_FEMM_surfaces"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "draw_FEMM_surfaces is deprecated, use femm_pyleecan.draw_FEMM_surfaces (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(0)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.draw_FEMM_surfaces(*args, **kwargs)
