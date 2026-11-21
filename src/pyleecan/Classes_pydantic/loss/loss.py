# Experimental pydantic model generated from Generator/ClassesRef/Loss/Loss.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import numpy as np
from pydantic import Field

from ...classes_common.errors import InputError
from ...classes_common.logger_context import get_logger
from ...classes_common.parents import container_or_parent
from .._legacy_model import LegacyModel
from ..output.out_loss_model import OutLossModel
from ..scidatatool.data_1d import Data1D
from .loss_model import LossModel

if TYPE_CHECKING:
    from ..mesh.mesh_solution import MeshSolution
    from ..output.output import Output
    from ..scidatatool.data import Data


class Loss(LegacyModel):
    """Loss module object that contain the loss models.

    Attributes
    ----------
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Loss"
    model_dict : {LossModel} or None
        Dict of loss model whose key is a lamination and value is the associated loss model (alternative to model_index/model_list)
        Default: None
    Tsta : float
        Average stator temperature for Loss calculation
        Unit: deg Celsius; Default: 20
    Trot : float
        Average rotor temperature for Loss calculation
        Unit: deg Celsius; Default: 20
    is_get_meshsolution : bool
        True to save loss density map as meshsolution
        Default: False
    is_clean_magmesh : bool
        True to clean meshsolution from OutMag after loss calculation
        Default: False
    """

    logger_name: str = "Pyleecan.Loss"
    """Name of the logger to use"""
    model_dict: dict[str, LossModel] | None = None
    """Dict of loss model whose key is a lamination and value is the associated loss model (alternative to model_index/model_list)"""
    Tsta: float = Field(default=20, json_schema_extra={"unit": "deg Celsius"})
    """Average stator temperature for Loss calculation"""
    Trot: float = Field(default=20, json_schema_extra={"unit": "deg Celsius"})
    """Average rotor temperature for Loss calculation"""
    is_get_meshsolution: bool = False
    """True to save loss density map as meshsolution"""
    is_clean_magmesh: bool = False
    """True to clean meshsolution from OutMag after loss calculation"""

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Loss.Loss.comp_all_losses
    def comp_all_losses(
        self,
        axes_dict: dict | None = None,
        meshsol: MeshSolution | None = None,
    ) -> None:
        """Compute all the losses models set in model_dict

        Parameters
        ----------
        self : Loss
            A Loss object
        axes_dict : dict
            Dict containing axes for loss calculation
        meshsol : MeshSolution
            magnetic meshsolution with stator and rotor solutions merged (default: OutMag.get_meshsolution())
        """

        output = self.parent.parent
        out_loss = output.loss
        # Store dict of axes
        if axes_dict is not None:
            out_loss.axes_dict = axes_dict

        if meshsol is None:
            meshsol = output.mag.get_meshsolution()
        group = meshsol.group
        freqs = axes_dict["freqs"].get_values()
        Nelem = meshsol.mesh.element_dict["triangle"].nb_element

        out_loss.loss_dict = {}
        for key, model in self.model_dict.items():
            # Compute losses for each model
            P_density, f_array = model.comp_loss(meshsol=meshsol)
            if self.is_get_meshsolution:
                loss_density = np.zeros((freqs.size, Nelem))
                If = np.argmin(np.abs(freqs[:, None] - f_array[None, :]), axis=0)[
                    :, None
                ]
                Ie = np.array(group[model.group])[None, :]
                loss_density[If, Ie] += P_density
            else:
                loss_density = None
            # Store results of each model in a different object
            out_loss_model = OutLossModel(
                name=key,
                loss_density=loss_density,
                scalar_value=None,
                coeff_dict=model.coeff_dict,
                group=model.group,
                loss_model=type(model).__name__,
            )
            out_loss.loss_dict[key] = out_loss_model

    # Inlined from Methods.Loss.Loss.comp_axes
    def comp_axes(
        self, output: Output, meshsol: MeshSolution | None = None
    ) -> dict[str, Data]:
        """Compute the axes required in Loss module

        Parameters
        ----------
        self : Loss
            a Loss object
        output : Output
            an Output object (to update)
        meshsol : MeshSolution
            magnetic meshsolution with stator and rotor solutions merged (default: OutMag.get_meshsolution())

        Returns
        -------
        axes_dict: {Data}
            Dict containing Time and Angle axes including (anti-)periodicties used in any Force module
        """

        if meshsol is None:
            meshsol = output.mag.get_meshsolution()

        axes_list = meshsol.get_solution().field.get_axes()
        Time = axes_list[0]

        freqs = Time.get_values(is_oneperiod=True, operation="time_to_freqs")

        if "antiperiod" in Time.symmetries:
            Time_per = Time.copy()
            Time_per.symmetries = {"period": Time.symmetries["antiperiod"]}
            freqs_per = Time_per.get_values(
                is_oneperiod=True, operation="time_to_freqs"
            )
            freqs = np.unique(np.concatenate((freqs, freqs_per)))

        Freqs = Data1D(
            name="freqs",
            unit="Hz",
            values=freqs,
            normalizations=Time.normalizations.copy(),
        )

        axes_dict = {"freqs": Freqs, "indice": axes_list[1]}

        return axes_dict

    # Inlined from Methods.Loss.Loss.run
    def run(self, output: Output | None = None) -> None:
        """Run the Loss module

        Parameters
        ----------
        self : Loss
            A Loss model
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)
        """
        output = container_or_parent(self, output, "output", depth=2)
        if output is None and self.parent is None:
            raise InputError("The Loss object must be in a Simulation object to run")
        if output is None:
            raise InputError("The Loss object must be in an Output object to run")

        get_logger(self).info("Running Loss module")

        # get output

        # Merge stator and rotor frame magnetic solutions once for all loss models
        meshsol = output.mag.get_meshsolution()

        axes_dict = self.comp_axes(output, meshsol=meshsol)
        # Comp and store in output
        self.comp_all_losses(axes_dict, meshsol=meshsol)
