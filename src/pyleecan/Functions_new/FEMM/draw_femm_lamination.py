"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def draw_FEMM_lamination(*args, **kwargs):
    """Deprecated: use femm_pyleecan.draw_FEMM_lamination"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "draw_FEMM_lamination is deprecated, use femm_pyleecan.draw_FEMM_lamination (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(3)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.draw_FEMM_lamination(*args, **kwargs)
