"""Deprecated aliases of femm_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def get_airgap_surface(*args, **kwargs):
    """Deprecated: use femm_pyleecan.get_airgap_surface"""
    from .femm_pyleecan import femm_pyleecan

    warn(
        "get_airgap_surface is deprecated, use femm_pyleecan.get_airgap_surface (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return femm_pyleecan.get_airgap_surface(*args, **kwargs)
