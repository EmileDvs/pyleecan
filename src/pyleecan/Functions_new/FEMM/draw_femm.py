"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn

from ...classes_common.errors import FEMMError  # noqa: F401


def draw_FEMM(*args, **kwargs):
    """Deprecated: use femm_pyleecan.draw_FEMM"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "draw_FEMM is deprecated, use femm_pyleecan.draw_FEMM (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(0)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.draw_FEMM(*args, **kwargs)
