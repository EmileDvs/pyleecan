"""Deprecated aliases of pv_plotter_pyleecan methods (removed in Phase 2)."""

from warnings import warn

from .pv_plotter_pyleecan import COLOR_MAP  # noqa: F401


def plot_glyph_pv(*args, **kwargs):
    """Deprecated: use pv_plotter_pyleecan.plot_glyph_pv"""
    from .pv_plotter_pyleecan import pv_plotter_pyleecan

    warn(
        "plot_glyph_pv is deprecated, use pv_plotter_pyleecan.plot_glyph_pv (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return pv_plotter_pyleecan.plot_glyph_pv(*args, **kwargs)
