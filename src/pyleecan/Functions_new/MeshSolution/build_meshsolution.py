"""Deprecated alias of the MeshSolution constructor (removed in Phase 2)."""

from warnings import warn


def build_meshsolution(solution_dict, mesh, label="", dimension=2, group=None):
    """Deprecated: use MeshSolution(label=, mesh=, solution_dict=, dimension=, group=)"""
    from ...Classes_new.mesh.mesh_solution import MeshSolution

    warn(
        "build_meshsolution is deprecated, use MeshSolution(label=..., mesh=..., "
        "solution_dict=..., dimension=..., group=...) (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return MeshSolution(
        label=label,
        mesh=mesh,
        solution_dict=solution_dict,
        dimension=dimension,
        group=group,
    )
