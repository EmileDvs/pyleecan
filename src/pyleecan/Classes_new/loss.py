# Experimental dataclass generated from Generator/ClassesRef/Loss/Loss.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._pyleecan_class import PyleecanClass
from .data_1d import Data1D
from .loss_model import LossModel
from .out_loss_model import OutLossModel
from .simulation import Simulation


@dataclass(eq=False)
class Loss(PyleecanClass):
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
        Average stator temperature for Electrical calculation
        Unit: deg Celsius; Default: 20
    Trot : float
        Average rotor temperature for Electrical calculation
        Unit: deg Celsius; Default: 20
    is_get_meshsolution : bool
        True to save loss density map as meshsolution
        Default: False
    """

    logger_name: str = "Pyleecan.Loss"
    """Name of the logger to use"""
    model_dict: dict[str, LossModel] | None = None
    """Dict of loss model whose key is a lamination and value is the associated loss model (alternative to model_index/model_list)"""
    Tsta: float = 20
    """Average stator temperature for Electrical calculation"""
    Trot: float = 20
    """Average rotor temperature for Electrical calculation"""
    is_get_meshsolution: bool = False
    """True to save loss density map as meshsolution"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Simulation,)):
            raise TypeError(
                "Loss parent must be an instance of Simulation, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Loss.Loss.comp_all_losses
    def comp_all_losses(
        self,
        axes_dict=None,
    ):
        """Compute all the losses models set in model_dict

        Parameters
        ----------
        self : Loss
            A Loss object
        axes_dict : dict
            Dict containing axes for loss calculation
        """

        output = self.parent.parent
        out_loss = output.loss
        # Store dict of axes
        if axes_dict is not None:
            out_loss.axes_dict = axes_dict

        meshsol = output.mag.meshsolution
        group = meshsol.group
        freqs = axes_dict["freqs"].get_values()
        Nelem = meshsol.mesh.element_dict["triangle"].nb_element

        out_loss.loss_dict = {}
        for key, model in self.model_dict.items():
            # Compute losses for each model
            P_density, f_array = model.comp_loss()
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
    def comp_axes(self, output):
        """Compute the axes required in Loss module

        Parameters
        ----------
        self : Loss
            a Loss object
        output : Output
            an Output object (to update)

        Returns
        -------
        axes_dict: {Data}
            Dict containing Time and Angle axes including (anti-)periodicties used in any Force module
        """

        axes_list = output.mag.meshsolution.get_solution().field.get_axes()
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
    def run(self):
        """Run the Loss module

        Parameters
        ----------
        self : Loss
            A Loss model
        """
        if self.parent is None:
            raise InputError("The Loss object must be in a Simulation object to run")
        if self.parent.parent is None:
            raise InputError("The Loss object must be in an Output object to run")

        self.get_logger().info("Running Loss module")

        # get output
        output = self.parent.parent

        axes_dict = self.comp_axes(output)
        # Comp and store in output
        self.comp_all_losses(axes_dict)

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""


InputError = Loss.InputError
