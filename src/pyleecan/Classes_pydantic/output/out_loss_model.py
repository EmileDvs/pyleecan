# Experimental pydantic model generated from Generator/ClassesRef/Output/OutLossModel.csv
"""Generated experimental pydantic model; do not edit by hand."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np

from .._legacy_model import LegacyModel
from .._pyleecan_model import NDArray
from ..mesh.mesh_solution import MeshSolution
from ..mesh.solution_data import SolutionData
from ..scidatatool.data_freq import DataFreq
from ..scidatatool.data_nd import DataND
from ..scidatatool.data_time import DataTime

if TYPE_CHECKING:
    from .out_loss_model import OutLossModel


class OutLossModel(LegacyModel):
    """Gather the loss module outputs

    Attributes
    ----------
    name : str
        Name of the loss
        Default: ""
    loss_density : ndarray or None
        Loss density
        Default: None
    coeff_dict : dict or None
        dict of coefficients to compute the scalar value with respcet to frequency
        Default: None
    group : str or None
        group to which the loss applies
        Default: None
    loss_model : str or None
        The name of the loss model used to compute the loss stored in this output
        Default: None
    scalar_value : float or None
        To store the value of get_loss_scalar (for scalar losses or with coeff_dict cleaned)
        Default: None
    loss_data : DataND or None
        DataTime containing losses values over time and for each source of losses : core (hysteresis/eddy/excess) / Joule / proximity / Magnet / Windage
        Default: None
    """

    name: str = ""
    """Name of the loss"""
    loss_density: NDArray | None = None
    """Loss density """
    coeff_dict: dict[str, Any] | None = None
    """dict of coefficients to compute the scalar value with respcet to frequency"""
    group: str | None = None
    """group to which the loss applies"""
    loss_model: str | None = None
    """The name of the loss model used to compute the loss stored in this output"""
    scalar_value: float | None = None
    """To store the value of get_loss_scalar (for scalar losses or with coeff_dict cleaned)"""
    loss_data: DataND | None = None
    """DataTime containing losses values over time and for each source of losses : core (hysteresis/eddy/excess) / Joule / proximity / Magnet / Windage"""

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Output.OutLossModel.__add__
    def __add__(self, other: OutLossModel | dict) -> OutLossModel:
        """Add two loss models output (called for: self + other)

        Parameters
        ----------
        self : OutLossModel
            First loss model to add
        other : OutLossModel or dict
            Second loss model to add

        Returns
        -------
        loss_tot : OutLossModel
            Resulting Losses output
        """

        if other == 0:
            return self
        try:
            other_loss_density = other.loss_density
            other_coeff_dict = other.coeff_dict
            other_group = other.group
            other_name = other.name
        except AttributeError:
            other_loss_density = other["loss_density"]
            other_coeff_dict = other["coeff_dict"]
            other_group = other["group"]
            other_name = other["name"]

        new_loss_density = self.loss_density + other_loss_density
        new_coeff_dict = self.coeff_dict.copy()
        for key, value in other_coeff_dict.items():
            if key in new_coeff_dict:
                new_coeff_dict[key] += value
            else:
                new_coeff_dict[key] = value
        new_group = self.group + " + " + other_group
        new_name = self.name + " + " + other_name
        return OutLossModel(
            name=new_name,
            loss_density=new_loss_density,
            coeff_dict=new_coeff_dict,
            group=new_group,
        )

    # Inlined from Methods.Output.OutLossModel.__radd__
    def __radd__(self, other: OutLossModel | dict) -> OutLossModel:
        """Add two loss models output (called for: other + self)

        Parameters
        ----------
        self : OutLossModel
            First loss model to add
        other : OutLossModel or dict
            Second loss model to add

        Returns
        -------
        loss_tot : OutLossModel
            Resulting Losses output
        """
        if other == 0:
            return self
        try:
            other_loss_density = other.loss_density
            other_coeff_dict = other.coeff_dict
            other_group = other.group
            other_name = other.name
        except AttributeError:
            other_loss_density = other["loss_density"]
            other_coeff_dict = other["coeff_dict"]
            other_name = other["name"]
            other_group = other["group"]

        new_loss_density = self.loss_density + other_loss_density
        new_coeff_dict = self.coeff_dict.copy()
        for key, value in other_coeff_dict.items():
            if key in new_coeff_dict:
                new_coeff_dict[key] += value
            else:
                new_coeff_dict[key] = value
        new_group = self.group + " + " + other_group
        new_name = self.name + " + " + other_name
        return OutLossModel(
            name=new_name,
            loss_density=new_loss_density,
            coeff_dict=new_coeff_dict,
            group=new_group,
        )

    # Inlined from Methods.Output.OutLossModel.__rsub__
    def __rsub__(self, other: OutLossModel | dict) -> OutLossModel:
        """Substract two loss models output (called for: other - self)

        Parameters
        ----------
        self : OutLossModel
            First loss model to sub
        other : OutLossModel or dict
            Second loss model to sub

        Returns
        -------
        loss_tot : OutLossModel
            Resulting Losses output
        """

        if other == 0:
            return self
        try:
            other_loss_density = other.loss_density
            other_coeff_dict = other.coeff_dict
            other_group = other.group
            other_name = other.name
        except AttributeError:
            other_loss_density = other["loss_density"]
            other_coeff_dict = other["coeff_dict"]
            other_group = other["group"]
            other_name = other["name"]

        new_loss_density = other_loss_density - self.loss_density
        new_coeff_dict = other_coeff_dict.copy()
        for key, value in self.coeff_dict.items():
            if key in new_coeff_dict:
                new_coeff_dict[key] -= value
            else:
                new_coeff_dict[key] = -value
        new_group = self.group + " - " + other_group
        new_name = self.name + " - " + other_name
        return OutLossModel(
            name=new_name,
            loss_density=new_loss_density,
            coeff_dict=new_coeff_dict,
            group=new_group,
        )

    # Inlined from Methods.Output.OutLossModel.__sub__
    def __sub__(self, other: OutLossModel | dict) -> OutLossModel:
        """Substract two loss models output (called for: self - other)

        Parameters
        ----------
        self : OutLossModel
            First loss model to sub
        other : OutLossModel or dict
            Second loss model to sub

        Returns
        -------
        loss_tot : OutLossModel
            Resulting Losses output
        """
        if other == 0:
            return self
        try:
            other_loss_density = other.loss_density
            other_coeff_dict = other.coeff_dict
            other_group = other.group
            other_name = other.name
        except AttributeError:
            other_loss_density = other["loss_density"]
            other_coeff_dict = other["coeff_dict"]
            other_group = other["group"]
            other_name = other["name"]

        new_loss_density = self.loss_density - other_loss_density
        new_coeff_dict = self.coeff_dict.copy()
        for key, value in other_coeff_dict.items():
            if key in new_coeff_dict:
                new_coeff_dict[key] -= value
            else:
                new_coeff_dict[key] = -value
        new_group = self.group + " - " + other_group
        new_name = self.name + " - " + other_name
        return OutLossModel(
            name=new_name,
            loss_density=new_loss_density,
            coeff_dict=new_coeff_dict,
            group=new_group,
        )

    # Inlined from Methods.Output.OutLossModel.get_loss_scalar
    def get_loss_scalar(self, felec: float | None = None) -> float:
        """Get loss power from coefficients stored in coeff_dict

        Parameters
        ----------
        self : OutLossModel
            an OutLossModel object
        felec : float
            the electrical frequency [Hz]

        Returns
        -------
        Ploss : float
            loss power for the specified frequency [W]
        """

        if self.coeff_dict is None:
            return self.scalar_value  # Can be None
        else:
            if felec is None:
                output = self.parent.parent
                felec = output.elec.OP.felec
            Ploss = 0
            for key, value in self.coeff_dict.items():
                Ploss += value * felec ** float(key)
            self.scalar_value = Ploss
        return self.scalar_value

    # Inlined from Methods.Output.OutLossModel.get_mesh_solution
    def get_mesh_solution(self) -> MeshSolution:
        """Returns the MeshSolution object corresponding to the losses

        Parameters
        ----------
        self : OutLossModel
            Result of a Loss model computation

        Returns
        -------
        MS : MeshSolution
            Losses as fct(freq) on the machine mesh
        """
        output = self.parent.parent
        # group = meshsol.group
        axes_dict = self.parent.axes_dict
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

    # Inlined from Methods.Output.OutLossModel.plot_mesh
    def plot_mesh(self, group_names: list | None = None, save_path: str | None = None):
        """Plot the losses on the mesh solution

        Parameters
        ----------
        self : OutLossModel
            An OutLossModel object
        group_names : list
            a list of str corresponding to group name(s)
        save_path : str
            path to save the figure

        """
        return (
            self.get_mesh_solution()
            .get_group(group_names)
            .plot_contour(
                "freqs=sum",
                label=f"{self.name} loss density",
                save_path=save_path,
            )
        )
