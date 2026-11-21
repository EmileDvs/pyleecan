"""Deprecated alias of OptiGenAlgNsga2Deap.tournamentDCD (moved to the class, removed in Phase 2)."""

from warnings import warn


def tournamentDCD(*args, **kwargs):
    """Deprecated: use OptiGenAlgNsga2Deap.tournamentDCD"""
    from ...Classes_pydantic.optimization.opti_gen_alg_nsga_2_deap import (
        OptiGenAlgNsga2Deap,
    )

    warn(
        "tournamentDCD is deprecated, use OptiGenAlgNsga2Deap.tournamentDCD (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return OptiGenAlgNsga2Deap.tournamentDCD(*args, **kwargs)
