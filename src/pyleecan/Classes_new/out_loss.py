# Experimental dataclass generated from Generator/ClassesRef/Output/OutLoss.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions.SciDataTool.Plot.plot_2D import plot_2D
from ._pyleecan_class import PyleecanClass
from .data import Data
from .out_loss_model import OutLossModel
from .output import Output


@dataclass(eq=False)
class OutLoss(PyleecanClass):
    """Gather the loss module outputs

    Attributes
    ----------
    axes_dict : {Data} or None
        Dict containing axes data used for Magnetics
        Default: None
    loss_dict : {OutLossModel}
        Dict containing OutLossModel obects for each type of loss
        Default: {}
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Loss"
    """

    axes_dict: dict[str, Data] | None = None
    """Dict containing axes data used for Magnetics"""
    loss_dict: dict[str, OutLossModel] = {}
    """Dict containing OutLossModel obects for each type of loss"""
    logger_name: str = "Pyleecan.Loss"
    """Name of the logger to use"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Output,)):
            raise TypeError(
                "OutLoss parent must be an instance of Output, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Output.OutLoss.__getitem__
    def __getitem__(self, idx):
        """Method to behave like a dict and iterate in the object"""
        return self.loss_dict.__getitem__(idx)

    # Inlined from Methods.Output.OutLoss.__len__
    def __len__(self):
        """Method to behave like a dict and iterate in the object"""
        return len(self.loss_dict)

    # Inlined from Methods.Output.OutLoss.get_loss_density_ag
    def get_loss_density_ag(self):
        """Get loss density in the airgap

        Parameters
        ----------
        self : OutLoss
            an OutLoss object

        Returns
        -------
        loss_density_ag : float
            airgap loss density [W/m^2]

        """

        loss = self.get_loss_overall()

        machine = self.parent.simu.machine

        Rag = machine.comp_Rgap_mec()
        Sag = 2 * np.pi * Rag * machine.stator.L1

        loss_density_ag = loss / Sag

        return loss_density_ag

    # Inlined from Methods.Output.OutLoss.get_loss_overall
    def get_loss_overall(self):
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

    # Inlined from Methods.Output.OutLoss.get_power_dict
    def get_power_dict(self):
        """Return a dictionnary with all the scalar losses

        Parameters
        ----------
        self : OutLoss
            An OutLoss object

        Returns
        -------
        power_dict : {float}
            Dictionnary of all the scalar losses
        """

        if self.parent is None:
            raise Exception("Error: OutLoss is not in Output object")
        out = self.parent
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
    def plot_losses(self, N0_array=None, save_path=None, is_show_fig=True):
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
        """

        if N0_array is None:
            N0_array = np.linspace(10, 8000, 100)
        if self.parent is None:
            raise Exception("Error: OutLoss is not in Output object")

        p = self.parent.simu.machine.get_pole_pair_number()

        array_list = [
            np.array([out_loss.get_loss_scalar(speed / 60 * p) for speed in N0_array])
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
