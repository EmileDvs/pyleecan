"""Deprecated alias of VarSimu.run_multisim_step (moved to the class, removed in Phase 2)."""

from warnings import warn


def run_multisim_step(*args, **kwargs):
    """Deprecated: use VarSimu.run_multisim_step"""
    from ....Classes_pydantic.simulation.var_simu import VarSimu

    warn(
        "run_multisim_step is deprecated, use VarSimu.run_multisim_step (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return VarSimu.run_multisim_step(*args, **kwargs)
