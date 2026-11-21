"""Deprecated aliases of pv_plotter_pyleecan methods (removed in Phase 2)."""

from warnings import warn

from .pv_plotter_pyleecan import FONT_FAMILY_PYVISTA  # noqa: F401


def configure_plot(*args, **kwargs):
    """Deprecated: use pv_plotter_pyleecan.configure_plot"""
    from .pv_plotter_pyleecan import pv_plotter_pyleecan

    warn(
        "configure_plot is deprecated, use pv_plotter_pyleecan.configure_plot (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return pv_plotter_pyleecan.configure_plot(*args, **kwargs)
