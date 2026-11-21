"""Deprecated alias of SolutionVector.build_solution_vector (moved to the class, removed in Phase 2)."""

from warnings import warn


def build_solution_vector(*args, **kwargs):
    """Deprecated: use SolutionVector.build_solution_vector"""
    from ...Classes_pydantic.mesh.solution_vector import SolutionVector

    warn(
        "build_solution_vector is deprecated, use SolutionVector.build_solution_vector (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return SolutionVector.build_solution_vector(*args, **kwargs)
