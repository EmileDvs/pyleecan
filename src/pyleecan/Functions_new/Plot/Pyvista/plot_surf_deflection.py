"""Deprecated aliases of pv_plotter_pyleecan methods (removed in Phase 2)."""

from warnings import warn

from .pv_plotter_pyleecan import COLOR_MAP  # noqa: F401


def plot_surf_deflection(*args, **kwargs):
    """Deprecated: use pv_plotter_pyleecan.plot_surf_deflection"""
    from .pv_plotter_pyleecan import pv_plotter_pyleecan

    warn(
        "plot_surf_deflection is deprecated, use pv_plotter_pyleecan.plot_surf_deflection (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return pv_plotter_pyleecan.plot_surf_deflection(*args, **kwargs)
