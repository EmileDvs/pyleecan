"""Deprecated alias of VarSimu.get_elec_datakeeper_dict (moved to the class, removed in Phase 2)."""

from warnings import warn


def get_elec_datakeeper_dict(*args, **kwargs):
    """Deprecated: use VarSimu.get_elec_datakeeper_dict"""
    from ....Classes_new.simulation.var_simu import VarSimu

    warn(
        "get_elec_datakeeper_dict is deprecated, use VarSimu.get_elec_datakeeper_dict (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return VarSimu.get_elec_datakeeper_dict(*args, **kwargs)
