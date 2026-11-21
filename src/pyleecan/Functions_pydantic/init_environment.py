"""Deprecated module: moved to utils.init_environment (removed in Phase 2)."""

from warnings import warn

from .utils.init_environment import (
    REPLACE_ATTEMPTS,
    REPLACE_DELAY,
    get_config_dict,
    init_config_dict,
    init_user_dir,
    save_config_dict,
    update_dict,
    update_user_dir,
)

warn(
    "pyleecan.Functions.init_environment is deprecated, use pyleecan.Functions.utils.init_environment (removed in Phase 2)",
    DeprecationWarning,
    stacklevel=2,
)
