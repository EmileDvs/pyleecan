"""Deprecated module: moved to utils.path_tools (removed in Phase 2)."""

from warnings import warn

from ..classes_common.errors import FileError  # noqa: F401
from ..classes_common.errors import PathImportError as ImportError
from .utils.path_tools import abs_file_path, importName, rel_file_path

warn(
    "pyleecan.Functions.path_tools is deprecated, use pyleecan.Functions.utils.path_tools (removed in Phase 2)",
    DeprecationWarning,
    stacklevel=2,
)
