from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.scidatatool.data_freq import DataFreq

from ....Classes_new.mesh.mesh_solution import MeshSolution
from ....Classes_new.mesh.solution_data import SolutionData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.out_loss import OutLoss
    from ....Classes_new.output.output import Output


def get_mesh_solution(self, out_loss: OutLoss | None = None, output: Output | None = None) -> MeshSolution:
    """Returns the MeshSolution object corresponding to the losses

    Parameters
    ----------
    self : OutLossModel
        Result of a Loss model computation
    out_loss : OutLoss, optional
        OutLoss holding the model (default: the parent)
    output : Output, optional
        Output of the simulation (default: the parent of the OutLoss)

    Returns
    -------
    MS : MeshSolution
        Losses as fct(freq) on the machine mesh
    """
    out_loss = container_or_parent(self, out_loss, "out_loss")
    output = container_or_parent(self, output, "output", depth=2)
    # group = meshsol.group
    axes_dict = out_loss.axes_dict
    # freqs = axes_dict["freqs"].get_values()
    # Nelem = meshsol.mesh.element["triangle"].nb_element

    # If = np.argmin(np.abs(freqs[:, None] - self.freqs[None, :]), axis=0)[:, None]
    # Ie = np.array(group[self.group])[None, :]
    # global_loss_density = np.zeros((freqs.size, Nelem))
    # global_loss_density[If, Ie] += self.loss_density

    # TODO : Do time dependent version
    # output = self.parent.parent
    # axes_dict = self.parent.axes_dict

    # Igrp = output.mag.meshsolution.group[self.name]

    # Indice = Data1D(
    #     name="indice",
    #     values=Igrp,
    #     is_components=True,
    #     is_overlay=False,
    # )

    # Loss_density_df = DataTime(
    #     name=f"{self.name} loss density",
    #     unit="W/m3",
    #     symbol="L",
    #     values=self.loss_density,
    #     is_real=True,
    #     axes=[axes_dict["time"], Indice],
    # )

    # Loss_density_sd = SolutionData(
    #     label=Loss_density_df.name,
    #     field=Loss_density_df,
    #     unit=Loss_density_df.unit,
    # )

    # ms_loss = MeshSolution(
    #     label=Loss_density_sd.label,
    #     group=ms_mag.group,
    #     mesh=ms_mag.mesh,
    #     solution_dict={Loss_density_sd.label: Loss_density_sd},
    #     dimension=2,
    # )

    ms_mag = output.mag.get_meshsolution()

    # The loss density on all the elements of the mesh (indice_element axis
    # since the OutMag meshsolution of #751; the density of a model is given
    # on the elements of its group), as OutLoss.get_meshsolution
    Indice_Element = axes_dict["indice_element"]
    Nelem = Indice_Element.get_length()
    loss_density = self.loss_density
    if loss_density.shape[-1] != Nelem:
        loss_density_all = np.zeros((loss_density.shape[0], Nelem), dtype=float)
        loss_density_all[:, ms_mag.group[self.group]] = loss_density
        loss_density = loss_density_all
    if loss_density.shape[0] == 1:  # Frequency model: average value
        Loss_density_df = DataFreq(
            name=f"{self.name} loss density",
            unit="W/m3",
            symbol="L",
            values=loss_density,
            is_real=True,
            axes=[axes_dict["freqs"], Indice_Element],
        )
    else:  # Time model
        from ....Classes_new.scidatatool.data_time import DataTime

        Loss_density_df = DataTime(
            name=f"{self.name} loss density",
            unit="W/m3",
            symbol="L",
            values=loss_density,
            is_real=True,
            axes=[axes_dict["time"], Indice_Element],
        )

    Loss_density_sd = SolutionData(
        label=Loss_density_df.name,
        field=Loss_density_df,
        unit=Loss_density_df.unit,
    )

    ms_loss = MeshSolution(
        label=Loss_density_sd.label,
        group=ms_mag.group,
        mesh=ms_mag.mesh,
        solution_dict={Loss_density_sd.label: Loss_density_sd},
        dimension=2,
    )

    return ms_loss
