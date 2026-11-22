# Experimental dataclass generated from Generator/ClassesRef/Machine/Conductor.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np

from ...definitions import config_dict
from .._legacy_class import LegacyClass
from ..material.material import Material


@dataclass(eq=False)
class Conductor(LegacyClass):
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

    COND_COLOR: ClassVar = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0].copy()
    INS_COLOR: ClassVar = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][1].copy()

    cond_mat: Material = field(
        default_factory=lambda: Material(), metadata={"default_class": "Material"}
    )
    """Material of the conductor"""
    ins_mat: Material = field(
        default_factory=lambda: Material(), metadata={"default_class": "Material"}
    )
    """Material of the insulation"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

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
        self,
        freq: float | np.ndarray,
        T_op: float = 20,
        T_ref: float = 20,
        b4: float | None = None,
        h4: float | None = None,
        zt: int | None = None,
    ) -> float:
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
    def comp_skin_effect_resistance(
        self,
        freq: float | np.ndarray,
        T_op: float = 20,
        T_ref: float = 20,
        b: float | None = None,
        zt: int | None = None,
    ) -> float:
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
    def comp_temperature_effect(self, T_op: float, T_ref: float = 20) -> float:
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

    # Inlined from Methods.Machine.Conductor.comp_cond_function
    @staticmethod
    def comp_cond_function(
        alpha_cond: float, W0: float, alpha_rad: np.ndarray
    ) -> np.ndarray:
        """Single conductor winding function for magnetomotive force calculation

        Parameters
        ----------
        alpha_cond : float
            angular position of the conductor [rad]
        W0 : float
            slot opening angular width (for linear rise of the mmf) [rad]
        alpha_rad : ndarray
            Position vector to compute the conductor winding function

        Returns
        -------
        wf: ndarray
            The conductor winding function

        """

        alpha_rad = np.mod(alpha_rad + np.pi - alpha_cond, 2 * np.pi)

        thi = 0
        thf = 2 * np.pi
        if W0 == 0:
            A = (alpha_rad < np.pi) * 1
            B = (alpha_rad > np.pi) * 1

            return B * ((alpha_rad - thf) / (np.pi - thf)) - A * (
                (alpha_rad - thi) / (np.pi - thi)
            )

        else:
            x1 = np.pi - W0 / 2.0
            x2 = np.pi + W0 / 2.0

            A = (alpha_rad < x1) * 1
            B = (alpha_rad > x2) * 1

            C = 1 - A - B
            return (
                C * (alpha_rad - np.pi) / (W0 / 2.0)
                + B * ((alpha_rad - thf) / (x2 - thf))
                - A * ((alpha_rad - thi) / (x1 - thi))
            )
