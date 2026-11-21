"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def get_FEMM_BC_propname(*args, **kwargs):
    """Deprecated: use femm_pyleecan.get_FEMM_BC_propname"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "get_FEMM_BC_propname is deprecated, use femm_pyleecan.get_FEMM_BC_propname (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    args = list(args)
    femm = kwargs.pop("femm") if "femm" in kwargs else args.pop(0)
    if not isinstance(femm, femm_pyleecan):  # FEMM handler
        femm = femm_pyleecan(femm)
    return femm.get_FEMM_BC_propname(*args, **kwargs)
