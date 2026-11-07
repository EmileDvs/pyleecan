# Experimental dataclass generated from Generator/ClassesRef/Machine/EndWindingRect.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .end_winding import EndWinding
from .lam_slot_wind import LamSlotWind


@dataclass(eq=False)
class EndWindingRect(EndWinding):
    """Class of the machine's end winding assuming a rectangular shape

    Attributes
    ----------
    coil_pitch : float or None
        effective coil pitch (override) for length calculation
        Default: None
    lambda_length : float
        permeance factor related to end winding length
        Default: 0; Minimum: 0
    lambda_width : float
        permeance factor related to end winding width
        Default: 0; Minimum: 0
    """

    coil_pitch: float | None = None
    """effective coil pitch (override) for length calculation"""
    lambda_length: float = 0
    """permeance factor related to end winding length"""
    lambda_width: float = 0
    """permeance factor related to end winding width"""

    # Inlined from Methods.Machine.EndWindingRect.comp_inductance
    def comp_inductance(self):
        """Compute the end winding inductance based on permeance coefficient stored in EndWindingRect object
        from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition

        Parameters
        ----------
        self: EndWindingRect
            A EndWindingRect object

        Returns
        -------
        Lew : float
            end winding inductance [H].
        """

        if self.parent is not None:
            winding = self.parent
        else:
            return 0

        p = winding.p
        Ntcoil = winding.Ntcoil

        mu0 = 4 * np.pi * 1e-7

        if winding.Lewout is not None:
            l_ew = winding.Lewout
        else:
            l_ew = 0

        # Calculate width of end winding
        w_ew = 2 * self.comp_length()

        # Calculate Eq(4.100)
        l_lambda = 2 * l_ew * self.lambda_length + w_ew * self.lambda_width

        # Calculate end-winding inductance from Eq (4.98) p.261
        Lw = 2 / p * Ntcoil**2 * mu0 * l_lambda

        return Lw

    # Inlined from Methods.Machine.EndWindingRect.comp_length
    def comp_length(self):
        """Compute the end winding conductor length on one side for a half-turn
        excluding the straight conductor length outside of the lamination (winding.Lewout).

        Parameters
        ----------
        self: EndWindingRect
            A EndWindingRect object

        Returns
        -------
        end_wind_length : float
            End-winding length on one side for a half-turn [m].
        """

        # check that Endwinding is in Winding of a Lamination with slots
        if (
            self.parent is None
            or self.parent.parent is None
            or not isinstance(self.parent.parent, LamSlotWind)
            or self.parent.parent.slot is None
        ):
            self.get_logger.warning(
                "EndWindingRect.comp_length(): "
                + "EndWindingRect has to be in a lamination with slot winding to calculate "
                + "the end winding length. Returning zero lenght."
            )
            return 0

        Rmid = self.parent.parent.slot.comp_radius_mid_active()
        Zs = self.parent.parent.slot.Zs
        p = self.parent.p

        # get the coil pitch (with some fall backs), first from the user definition
        # TODO utilize swat_em coil pitch calc.
        coil_pitch = self.coil_pitch
        if coil_pitch is None:
            # try to get coil_pitch of winding
            coil_pitch = getattr(self.parent, "coil_pitch", None)
            if coil_pitch is None:
                coil_pitch = Zs / p / 2
                self.get_logger().warning(
                    "EndWindingCirc.comp_lenght_endwinding():"
                    + "Using a coil pitch of one pole pitch for EW length calculation."
                )

        # end winding length is half the distance between two slots separated by the coil pitch
        end_wind_length = coil_pitch * np.pi / Zs * Rmid

        return end_wind_length
