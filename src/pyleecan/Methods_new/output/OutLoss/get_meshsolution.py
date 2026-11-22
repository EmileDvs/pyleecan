from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.mesh.mesh_solution import MeshSolution
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def get_meshsolution(self, output: Output | None = None) -> MeshSolution:
    """Get loss density meshsolution

    Parameters
    ----------
    self : OutLoss
        an OutLoss object
    output : Output, optional
        Output of the simulation holding the object (default: the parent)

    Returns
    -------
    ms_loss : MeshSolution
        Losses as function of time on the machine mesh

    """
    output = container_or_parent(self, output, "output")

    from ....Classes_new.mesh.solution_data import SolutionData
    if self.meshsolution is None:
        # Get magnetic output
        outmag = output.mag

        # Get mesh and groups from magnetic meshsolution
        meshsol = outmag.meshsolution
        mesh = meshsol.mesh
        group = meshsol.group

        # Get axes
        Ndim1 = list(self.loss_dict.values())[0].loss_density.shape[0]
        Indice_Element = self.axes_dict["indice_element"]
        Nelem = Indice_Element.get_length()
        if list(self.loss_dict.values())[0].loss_density.shape[0] == 1:
            axis_list = [self.axes_dict["freqs"].copy(), Indice_Element.copy()]
        else:
            axis_list = [self.axes_dict["time"].copy(), Indice_Element.copy()]

        # Get loss density values stored in OutLossModelTime objects
        loss_density = np.zeros((Ndim1, Nelem), dtype=float)
        for outloss in self.loss_dict.values():
            Igrp = group[outloss.group]
            loss_density[:, Igrp] += outloss.loss_density

        # Build SolutionData
        solution_data = SolutionData.build_solution_data(
            field=loss_density,
            axis_list=axis_list,
            name="Loss density",
            symbol="L",
            unit="W/m3",
            type_element="triangle",
        )

        # Build meshsolution
        self.meshsolution = MeshSolution(
            solution_dict={solution_data.label: solution_data},
            label=solution_data.label,
            mesh=mesh,
            group=group,
            dimension=2,
        )

    return self.meshsolution
