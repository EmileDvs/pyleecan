"""Deprecated aliases of pv_plotter_pyleecan methods (removed in Phase 2)."""

from warnings import warn

from .pv_plotter_pyleecan import COLOR_MAP  # noqa: F401


def plot_mesh_field(*args, **kwargs):
    """Deprecated: use pv_plotter_pyleecan.plot_mesh_field"""
    from .pv_plotter_pyleecan import pv_plotter_pyleecan

    warn(
        "plot_mesh_field is deprecated, use pv_plotter_pyleecan.plot_mesh_field (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return pv_plotter_pyleecan.plot_mesh_field(*args, **kwargs)
