"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def create_FEMM_bar(*args, **kwargs):
    """Deprecated: use femm_pyleecan.create_FEMM_bar"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "create_FEMM_bar is deprecated, use femm_pyleecan.create_FEMM_bar (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(0)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.create_FEMM_bar(*args, **kwargs)
