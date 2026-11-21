"""Deprecated aliases of pv_plotter_pyleecan methods (removed in Phase 2)."""

from warnings import warn


def get_arrows_plt(*args, **kwargs):
    """Deprecated: use pv_plotter_pyleecan.get_arrows_plt"""
    from .pv_plotter_pyleecan import pv_plotter_pyleecan

    warn(
        "get_arrows_plt is deprecated, use pv_plotter_pyleecan.get_arrows_plt (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return pv_plotter_pyleecan.get_arrows_plt(*args, **kwargs)
