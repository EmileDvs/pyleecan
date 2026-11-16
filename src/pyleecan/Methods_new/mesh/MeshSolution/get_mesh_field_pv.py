from ....Classes_new.mesh.solution_vector import SolutionVector
from ....Classes_new.mesh.mesh_vtk import MeshVTK
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_mesh_field_pv(
    self,
    *args,
    label: str | None = None,
    indices: list | None = None,
    is_surf: bool = False,
    is_radial: bool = False,
    is_center: bool = False,
    is_normal: bool = False,
    field_name: str | None = None,
    itimefreq: int = 0,
):
    """Return the mesh and field adapted to pyvista plots.

    Parameters
    ----------
    self : MeshSolution
        an MeshSolution object
    *args: list of strings
        List of axes requested by the user, their units and values (optional)
    label : str
        label of the solution
    indices : list
        list of indices
    is_radial : bool
        radial component only
    is_center : bool
        field at element centers
    field_name : str
        label of the field to return
    itimefreq : int
        if the field depends has a time/freqs axis, return the timefreq-th slice.

    Returns
    -------
    mesh_pv: vtk.vtkPointSet
        a pyvista mesh object
    field : ndarray
        an extracted field
    field_name : str
        name of the extracted field (useful if not specified as input)

    """

    new_mesh = self.mesh.copy()

    if not isinstance(new_mesh, MeshVTK):
        new_mesh.renum()

    mesh_pv = new_mesh.get_mesh_pv()

    solution = self.get_solution(
        label=label,
    )

    args_list = list()
    if len(args) > 0:
        for a in args:
            args_list.append(a)
    args_list.append("indice")
    if isinstance(solution, SolutionVector):
        args_list.append("components")

    field = self.get_field(
        *args_list,
        label=label,
        indices=indices,
        is_surf=is_surf,
        is_radial=is_radial,
        is_center=is_center,
        is_normal=is_normal,
    )

    if field_name is None:
        field_name = label if label is not None else "Field"

    return mesh_pv, field, field_name
