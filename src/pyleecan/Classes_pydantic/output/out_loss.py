# Experimental pydantic model generated from Generator/ClassesRef/Output/OutLoss.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import numpy as np
from pydantic import Field

from ...classes_common.parents import container_or_parent
from ...Functions_pydantic.SciDataTool.Plot.plot_2d import plot_2D
from .._legacy_model import LegacyModel
from ..mesh.mesh_solution import MeshSolution
from ..mesh.solution_data import SolutionData
from ..scidatatool.data import Data
from .out_loss_model import OutLossModel

if TYPE_CHECKING:
    from .output import Output


class OutLoss(LegacyModel):
    """Gather the loss module outputs

    Attributes
    ----------
    axes_dict : {Data} or None
        Dict containing axes data used for Magnetics
        Default: None
    loss_dict : {OutLossModel}
        Dict containing OutLossModel objects for each type of loss
        Default: {}
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Loss"
    meshsolution : MeshSolution or None
        FEA software mesh and solution
        Default: None
    P_in : float or None
        Input electric power used to calculate efficiency
        Unit: W; Default: None
    P_out : float or None
        Output mechanical power used to calculate efficiency
        Unit: W; Default: None
    efficiency : float or None
        Efficiency (p.u)
        Default: None
    Tmech_av : float or None
        Average mechanical torque
        Unit: Nm; Default: None
    """

    axes_dict: dict[str, Data] | None = None
    """Dict containing axes data used for Magnetics"""
    loss_dict: dict[str, OutLossModel] = Field(default_factory=dict)
    """Dict containing OutLossModel objects for each type of loss"""
    logger_name: str = "Pyleecan.Loss"
    """Name of the logger to use"""
    meshsolution: MeshSolution | None = None
    """FEA software mesh and solution"""
    P_in: float | None = Field(default=None, json_schema_extra={"unit": "W"})
    """Input electric power used to calculate efficiency"""
    P_out: float | None = Field(default=None, json_schema_extra={"unit": "W"})
    """Output mechanical power used to calculate efficiency"""
    efficiency: float | None = None
    """Efficiency (p.u)"""
    Tmech_av: float | None = Field(default=None, json_schema_extra={"unit": "Nm"})
    """Average mechanical torque"""

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Output.OutLoss.__getitem__
    def __getitem__(self, idx):
        """Method to behave like a dict and iterate in the object"""
        return self.loss_dict.__getitem__(idx)

    # Inlined from Methods.Output.OutLoss.__len__
    def __len__(self) -> int:
        """Method to behave like a dict and iterate in the object"""
        return len(self.loss_dict)

    # Inlined from Methods.Output.OutLoss.get_loss_density_ag
    def get_loss_density_ag(self, output: Output | None = None) -> float:
        """Get loss density in the airgap

        Parameters
        ----------
        self : OutLoss
            an OutLoss object
        output : Output, optional
            Output of the simulation holding the object (default: the parent)

        Returns
        -------
        loss_density_ag : float
            airgap loss density [W/m^2]

        """
        output = container_or_parent(self, output, "output")

        loss = self.get_loss_overall()

        machine = output.simu.machine

        Rag = machine.comp_Rgap_mec()
        Sag = 2 * np.pi * Rag * machine.stator.L1

        loss_density_ag = loss / Sag

        return loss_density_ag

    # Inlined from Methods.Output.OutLoss.get_loss_overall
    def get_loss_overall(self) -> float:
        """Get overall loss by summing all losses in OutLoss

        Parameters
        ----------
        self : OutLoss
            an OutLoss object

        Returns
        -------
        loss : float
            overall loss [W]

        """

        overall_loss = 0

        for loss in self.loss_dict.values():
            if loss.scalar_value is not None:
                overall_loss += loss.scalar_value

        return overall_loss

    # Inlined from Methods.Output.OutLoss.get_meshsolution
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

    # Inlined from Methods.Output.OutLoss.get_power_dict
    def get_power_dict(self, output: Output | None = None) -> dict[str, float]:
        """Return a dictionnary with all the scalar losses

        Parameters
        ----------
        self : OutLoss
            An OutLoss object
        output : Output, optional
            Output of the simulation holding the object (default: the parent)

        Returns
        -------
        power_dict : {float}
            Dictionnary of all the scalar losses
        """
        output = container_or_parent(self, output, "output")

        if output is None:
            raise Exception("Error: OutLoss is not in Output object")
        out = output
        if out.elec is None or out.elec.OP is None:
            raise Exception("Error: OP is not set")

        power_dict = dict(
            [
                (o.name, o.get_loss_scalar(out.elec.OP.felec))
                for o in self.loss_dict.values()
            ]
        )

        if out.mag is not None and out.mag.Pem_av is not None:
            power_dict["total_power"] = out.mag.Pem_av

        return power_dict

    # Inlined from Methods.Output.OutLoss.plot_losses
    def plot_losses(
        self,
        N0_array: np.ndarray | None = None,
        save_path: str | None = None,
        is_show_fig: bool = True,
        output: Output | None = None,
    ) -> None:
        """Plot the losses as a fct of speed

        Parameters
        ----------
        self : OutLoss
            An OutLoss object
        N0_array : ndarray
            speed array to use as X axis [rpm]
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            True to show figure after plot
        output : Output, optional
            Output of the simulation holding the object (default: the parent)
        """
        output = container_or_parent(self, output, "output")

        if N0_array is None:
            N0_array = np.linspace(10, 8000, 100)
        if output is None:
            raise Exception("Error: OutLoss is not in Output object")

        p = output.simu.machine.get_pole_pair_number()

        array_list = [
            np.array(
                [
                    out_loss.get_loss_scalar(speed / 60 * p, output=output)
                    for speed in N0_array
                ]
            )
            for out_loss in self.loss_dict.values()
        ]

        plot_2D(
            [N0_array],
            array_list,
            xlabel="Speed [rpm]",
            ylabel="Losses [W]",
            legend_list=[out_loss.name for out_loss in self.loss_dict.values()],
            is_show_fig=is_show_fig,
            save_path=save_path,
        )
