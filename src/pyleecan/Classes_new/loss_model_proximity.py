# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModelProximity.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .loss_model import LossModel


@dataclass(eq=False)
class LossModelProximity(LossModel):
    """Proximity Loss Model Class

    Attributes
    ----------
    k_p : float or None
        Proximity loss coefficient
        Unit: W/kg; Default: None
    """

    k_p: float | None = None
    """Proximity loss coefficient"""

    # Inlined from Methods.Loss.LossModelProximity.comp_coeff
    def comp_coeff(self):
        """Compute the Proximity loss coefficient [W/kg]

        Parameters
        ----------
        self : LossModelProximity
        """
        T_op = self.parent.Tsta
        winding = self.parent.parent.machine.stator.winding
        sigma = winding.conductor.cond_mat.elec.get_conductivity(T_op=T_op)
        d = winding.conductor.Wwire
        kf = self.parent.parent.machine.stator.comp_fill_factor()

        # Proximity loss coefficient [W/kg]
        self.k_p = kf * np.pi**2 / 8 * sigma * d**2

    # Inlined from Methods.Loss.LossModelProximity.comp_loss
    def comp_loss(self):
        """Calculate proximity loss density assuming it is given by:

            P = k_p * f^2 * B^2

        Parameters
        ----------
        self: LossModelProximity
            a LossModelProximity object

        Returns
        -------
        Pcore_density : ndarray
            Core loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """

        if self.parent.parent.parent is None:
            raise Exception("Cannot calculate core losses if simu is not in an Output")
        else:
            output = self.parent.parent.parent

        machine = output.simu.machine

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        lamination = machine.stator if "stator" in self.group else machine.rotor
        Lst = lamination.L1

        # Compute the Proximity loss coefficient (if not enforced)
        if self.k_p is None:
            self.comp_coeff()
        k_p = self.k_p

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        if output.mag is None:
            raise Exception("Cannot calculate core losses if OutMag is None")

        if output.mag.meshsolution is None:
            raise Exception(
                "Cannot calculate core losses if OutMag.meshsolution is None"
            )
        else:
            meshsol = output.mag.meshsolution

        group_list = list(meshsol.group.keys())

        if self.group not in group_list:
            raise Exception("Cannot calculate core losses for group=" + self.group)

        try:
            solution_B = meshsol["B"]
        except ValueError:
            raise ValueError("Cannot calculate core losses if B is not in meshsolution")

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = meshsol.mesh.get_element_area()[Igrp]

        Bvect = solution_B.field
        axes_list = Bvect.get_axes()
        Time_orig = axes_list[0]
        Time = Time_orig.copy()

        # Check Time axis periodicity in function of group
        is_change_Time = False
        if "rotor" in self.group:
            if "antiperiod" in Time_orig.symmetries:
                Time.symmetries = {"period": Time_orig.symmetries["antiperiod"]}
                is_change_Time = True
        if is_change_Time:
            for comp in Bvect.components.values():
                comp.axes[0] = Time

        # Compute magnetic flux density FFT
        Bfft = Bvect.get_xyz_along("freqs", "indice=" + str(Igrp), "z=mean")
        freqs = Bfft["freqs"]
        Bfft_magnitude = np.sqrt(
            np.abs(Bfft["comp_x"]) ** 2 + np.abs(Bfft["comp_y"]) ** 2
        )

        # Proximity loss density for each frequency and element
        Pcore_density = k_p * freqs[:, None] ** 2 * Bfft_magnitude**2

        if is_change_Time:
            # Change periodicity back to original periodicity
            for comp in Bvect.components.values():
                comp.axes[0] = Time_orig

        # Get frequency orders
        n = freqs / felec

        # Integrate loss density over group volume to get polynomial coefficients
        coeff = Lst * per_a * np.matmul(Bfft_magnitude**2, Se)
        A = np.sum(k_p * coeff * n**2)
        self.coeff_dict = {"2": A}

        return Pcore_density, freqs
