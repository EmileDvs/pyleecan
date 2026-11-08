# Experimental dataclass generated from Generator/ClassesRef/Loss/LossFEA.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._error import InputError
from .loss import Loss
from .loss_model_joule import LossModelJoule
from .loss_model_magnet import LossModelMagnet
from .loss_model_proximity import LossModelProximity
from .loss_model_steinmetz import LossModelSteinmetz


@dataclass(eq=False)
class LossFEA(Loss):
    """Simplified loss module, with predefined loss models for a quick setup

    Attributes
    ----------
    k_ed : float or None
        eddy current loss coefficients
        Unit: W/(m3*T2*Hz2); Default: None
    k_hy : float or None
        hysteresis loss coefficients
        Unit: W/(m3*T2*Hz); Default: None
    k_p : float or None
        proximity loss coefficients
        Unit: W/(m3*T2*Hz2); Default: None
    type_skin_effect : int
        Skin effect for resistance calculation (0 to ignore skin effect, 1 to consider it)
        Default: 1
    """

    k_ed: float | None = None
    """eddy current loss coefficients"""
    k_hy: float | None = None
    """hysteresis loss coefficients"""
    k_p: float | None = None
    """proximity loss coefficients"""
    type_skin_effect: int = 1
    """Skin effect for resistance calculation (0 to ignore skin effect, 1 to consider it)"""

    # Inlined from Methods.Loss.LossFEA.run
    def run(self):
        """Run the LossFEA module

        Paramaters
        ----------
        self : LossFEA
            A LossFEA object
        """
        if self.parent is None:
            raise InputError("The Loss object must be in a Simulation object to run")
        if self.parent.parent is None:
            raise InputError("The Loss object must be in an Output object to run")

        self.get_logger().info("Running LossFEA module")

        # get output
        output = self.parent.parent
        machine = output.simu.machine
        axes_dict = self.comp_axes(output)

        # Define all relevant loss models
        self.model_dict = {
            "stator core": LossModelSteinmetz(
                group="stator core",
                k_hy=self.k_hy,
                k_ed=self.k_ed,
                alpha_f=1,
                alpha_B=2,
            ),
            "rotor core": LossModelSteinmetz(
                group="rotor core", k_hy=self.k_hy, k_ed=self.k_ed, alpha_f=1, alpha_B=2
            ),
            "joule": LossModelJoule(
                group="stator winding", type_skin_effect=self.type_skin_effect
            ),
            "proximity": LossModelProximity(group="stator winding", k_p=self.k_p),
        }
        if machine.is_synchronous() and machine.rotor.has_magnet():
            self.model_dict["magnets"] = LossModelMagnet(group="rotor magnets")

        self.comp_all_losses(axes_dict)

        # Add overall by adding all losses sources
        overall = sum(output.loss.loss_dict.values())
        overall.name = "overall"
        output.loss.loss_dict["overall"] = overall
