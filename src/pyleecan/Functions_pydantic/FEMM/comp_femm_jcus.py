"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def comp_FEMM_Jcus(*args, **kwargs):
    """Deprecated: use femm_pyleecan.comp_FEMM_Jcus"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "comp_FEMM_Jcus is deprecated, use femm_pyleecan.comp_FEMM_Jcus (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return femm_pyleecan.comp_FEMM_Jcus(*args, **kwargs)
