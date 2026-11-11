# Experimental dataclass generated from Generator/ClassesRef/Machine/Conductor.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ._pyleecan_class import PyleecanClass
from .material import Material


@dataclass(eq=False)
class Conductor(PyleecanClass):
    """abstact class for conductors

    Attributes
    ----------
    cond_mat : Material or None
        Material of the conductor
        Default: Material()
    ins_mat : Material or None
        Material of the insulation
        Default: Material()
    """

    cond_mat: Material | None = field(
        default_factory=lambda: Material(), metadata={"default_class": "Material"}
    )
    """Material of the conductor"""
    ins_mat: Material | None = field(
        default_factory=lambda: Material(), metadata={"default_class": "Material"}
    )
    """Material of the insulation"""

    # Inlined from Methods.Machine.Conductor.check
    def check(self):
        """Check that the Conductor object is correct

        Parameters
        ----------
        self : Conductor
            A Conductor object

        Returns
        -------
        None
        """
        pass

    # Inlined from Methods.Machine.Conductor.comp_skin_effect_inductance
    def comp_skin_effect_inductance(
        self, freq, T_op=20, T_ref=20, b4=None, h4=None, zt=None
    ):
        """Compute the skin effect factor on inductance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
        All parameters bc, h4, z4, are defined in Fig(4.14) p.249

        Parameters
        ----------
        self : Conductor
            an Conductor object
        freq: float or ndarray
            electrical frequency [Hz]
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]
        b4: float
            Slot width [m]
        h4: float
            Slot height [m]
        zt: int
            Number of radial adjacent conductors

        Returns
        ----------
        kl_skin : float
            skin effect coeff for inductance at given frequency and temperature
        """

        if b4 is None:
            # Compute slot average width
            slot = self.parent.parent.slot
            b4 = slot.comp_width()

        if h4 is None:
            # Compute slot height
            slot = self.parent.parent.slot
            h4 = slot.comp_height()

        if zt is None:
            # Get number of turns in series per coil
            zt = self.parent.Ntcoil

        # conductor width
        bc = self.comp_width_wire()

        # Electrical conductivity accounting for temperature increase
        sigma = self.cond_mat.elec.get_conductivity(T_op=T_op, T_ref=T_ref)

        # Magnetic permeability
        mu0 = 4 * np.pi * 1e-7
        if self.cond_mat.mag is None or self.cond_mat.mag.mur_lin is None:
            mur = 1
        else:
            mur = self.cond_mat.mag.mur_lin

        # Electrical pulsation
        w = 2 * np.pi * freq

        # reduced conductor height Eq(4.90) p.257 + addind relative permeatibility
        ksi = h4 * np.sqrt(w * mu0 * mur * sigma * bc / (2 * b4))

        if not isinstance(ksi, float):
            # Avoid numerical error with 0
            ksi[ksi == 0] = 1e-4

        # resistance factor function phi prime Eq(4.92) p.257
        phip = (
            3
            / (2 * ksi)
            * (np.sinh(2 * ksi) - np.sin(2 * ksi))
            / (np.cosh(2 * ksi) - np.cos(2 * ksi))
        )

        # resistance factor function psi prime Eq(4.91) p.257
        psip = 1 / ksi * (np.sinh(ksi) + np.sin(ksi)) / (np.cosh(ksi) + np.cos(ksi))

        # average resistance factor  Eq(4.91) p.257
        kl_skin = phip / zt**2 + ((zt**2 - 1) / zt**2) * psip

        return kl_skin

    # Inlined from Methods.Machine.Conductor.comp_skin_effect_resistance
    def comp_skin_effect_resistance(self, freq, T_op=20, T_ref=20, b=None, zt=None):
        """Compute the skin effect factor on resistance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
        All parameters are defined p.270 / 271

        Parameters
        ----------
        self : Conductor
            an Conductor object
        b: float
            Slot width [m]
        zt: int
            Number of turns in series per coil
        freq: float or ndarray
            electrical frequency [Hz]
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]

        Returns
        ----------
        kr_skin : float
            skin effect coeff for resistance at given frequency and temperature
        """

        if b is None:
            # Compute slot average width
            slot = self.parent.parent.slot
            b = slot.comp_width()

        if zt is None:
            # Get number of turns in series per coil
            zt = self.parent.Ntcoil

        # check if wires are round or rectangular
        is_round_wire = self.is_round_wire()

        # conductor height
        hc0 = self.comp_height_wire()
        # conductor width
        bc0 = self.comp_width_wire()
        # Number of circumferential adjacent wires
        za = self.comp_nb_circumferential_wire()
        # Number of radial adjacent wires
        zp = self.comp_nb_radial_wire()
        # Equivalent height of conductor
        hc = zp * hc0

        # Electrical conductivity accounting for temperature increase
        sigma = self.cond_mat.elec.get_conductivity(T_op=T_op, T_ref=T_ref)

        # Magnetic permeability
        mu0 = 4 * np.pi * 1e-7
        if self.cond_mat.mag is None or self.cond_mat.mag.mur_lin is None:
            mur = 1
        else:
            mur = self.cond_mat.mag.mur_lin

        # Electrical pulsation
        w = 2 * np.pi * freq

        # reduced conductor height Eq(5.24) p.270 + adding relative permeatibility
        ksi = hc * np.sqrt((1 / 2) * w * mu0 * mur * sigma * za * bc0 / b)

        if not isinstance(ksi, float):
            # Avoid numerical error with 0
            ksi[ksi == 0] = 1e-4

        # average resistance factor
        if is_round_wire:
            # Use round wire approximation Eq(5.30) p.271
            kr_skin = 1 + 0.59 * ((zt**2 - 0.2) / 9) * ksi**4
        else:
            # resistance factor function phi Eq(5.26) p.271
            phi = (
                ksi
                * (np.sinh(2 * ksi) + np.sin(2 * ksi))
                / (np.cosh(2 * ksi) - np.cos(2 * ksi))
            )

            # resistance factor function psi Eq(5.27) p.271
            psi = 2 * ksi * (np.sinh(ksi) - np.sin(ksi)) / (np.cosh(ksi) + np.cos(ksi))

            kr_skin = phi + ((zt**2 - 1) / 3) * psi  # Eq(5.28) p.271
            # kr_approx = 1 + (zt ** 2 - 0.2) / 9 * ksi ** 4  # Eq(5.29) p.271

        return kr_skin

    # Inlined from Methods.Machine.Conductor.comp_temperature_effect
    def comp_temperature_effect(self, T_op, T_ref=20):
        """Compute the temperature effect factor for the conductor

        Parameters
        ----------
        self : Conductor
            an Conductor object
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]

        Returns
        ----------
        Tfact : float
            temperature effect coeff for resistance at T_op
        """

        alphasw = self.cond_mat.elec.alpha
        Tfact = 1 + alphasw * (T_op - T_ref)

        return Tfact
