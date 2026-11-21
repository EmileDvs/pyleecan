"""Deprecated alias of VarSimu.log_datakeeper_step_result (moved to the class, removed in Phase 2)."""

from warnings import warn


def log_datakeeper_step_result(*args, **kwargs):
    """Deprecated: use VarSimu.log_datakeeper_step_result"""
    from ....Classes_new.simulation.var_simu import VarSimu

    warn(
        "log_datakeeper_step_result is deprecated, use VarSimu.log_datakeeper_step_result (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return VarSimu.log_datakeeper_step_result(*args, **kwargs)
