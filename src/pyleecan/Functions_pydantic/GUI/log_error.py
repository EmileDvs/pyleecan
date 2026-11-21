"""Deprecated module: moved to GUI_new.Tools.log_error (removed in Phase 2)."""

from warnings import warn

from ...GUI_pydantic.Tools.log_error import log_error

warn(
    "pyleecan.Functions.GUI.log_error is deprecated, use Tools.log_error of the GUI package (removed in Phase 2)",
    DeprecationWarning,
    stacklevel=2,
)
