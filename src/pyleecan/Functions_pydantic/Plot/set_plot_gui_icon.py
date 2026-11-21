"""Deprecated module: moved to GUI_new.Tools.set_plot_gui_icon (removed in Phase 2)."""

from warnings import warn

from ...GUI_pydantic.Tools.set_plot_gui_icon import set_plot_gui_icon

warn(
    "pyleecan.Functions.Plot.set_plot_gui_icon is deprecated, use Tools.set_plot_gui_icon of the GUI package (removed in Phase 2)",
    DeprecationWarning,
    stacklevel=2,
)
