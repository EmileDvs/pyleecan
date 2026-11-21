"""Deprecated alias of Machine.get_color_legend_from_surface (moved to the class, removed in Phase 2)."""

from warnings import warn


def get_color_legend_from_surface(*args, **kwargs):
    """Deprecated: use Machine.get_color_legend_from_surface"""
    from ...Classes_new.machine.machine import Machine

    warn(
        "get_color_legend_from_surface is deprecated, use Machine.get_color_legend_from_surface (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return Machine.get_color_legend_from_surface(*args, **kwargs)
