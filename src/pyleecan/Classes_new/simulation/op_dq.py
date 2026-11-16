# Experimental dataclass generated from Generator/ClassesRef/Simulation/OPdq.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np

from ...classes_common.errors import InputError
from .op import OP


@dataclass(eq=False)
class OPdq(OP):
    """Operating Point defined in DQH frame

    Attributes
    ----------
    Id_ref : float or None
        d-axis current rms value
        Unit: Arms; Default: None
    Iq_ref : float or None
        q-axis current rms value
        Unit: Arms; Default: None
    Ud_ref : float or None
        d-axis voltage rms value
        Unit: Vrms; Default: None
    Uq_ref : float or None
        q-axis voltage rms value
        Unit: Vrms; Default: None
    """

    Id_ref: float | None = field(default=None, metadata={"unit": "Arms"})
    """d-axis current rms value"""
    Iq_ref: float | None = field(default=None, metadata={"unit": "Arms"})
    """q-axis current rms value"""
    Ud_ref: float | None = field(default=None, metadata={"unit": "Vrms"})
    """d-axis voltage rms value"""
    Uq_ref: float | None = field(default=None, metadata={"unit": "Vrms"})
    """q-axis voltage rms value"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.OPdq.get_felec
    def get_felec(self, p: int | None = None) -> float:
        """Returns the electrical frequency

        Parameters
        ----------
        self : OPdq
            An OPdq object
        p: int
            pole pair number

        Returns
        -------
        felec : float
            Electrical Frequency [Hz]
        """

        if self.felec is not None:
            return self.felec

        # Compute felec if possible
        if self.N0 is None:
            raise InputError("OPdq object can't have felec and N0 both None")

        if p is None:
            machine = self.get_machine_from_parent()
            if machine is None:
                raise InputError(
                    "OPdq object can't find machine parent to compute felec"
                )

            p = machine.get_pole_pair_number()

        self.felec = self.N0 * p / 60

        return self.felec

    # Inlined from Methods.Simulation.OPdq.get_I0_Phi0
    def get_I0_Phi0(self) -> dict:
        """Return I0 and Phi0

        Parameters
        ----------
        self : OPdq
            An OPdq object

        Returns
        -------
        I_dict : dict
            Dict with key "I0", "Phi0"
        """
        if self.Id_ref is None or self.Iq_ref is None:
            return {"I0": None, "Phi0": None}
        else:
            Z = self.Id_ref + 1j * self.Iq_ref
            return {"I0": abs(Z), "Phi0": np.angle(Z) % (2 * np.pi)}

    # Inlined from Methods.Simulation.OPdq.get_Id_Iq
    def get_Id_Iq(self) -> dict:
        """Return Id and Iq

        Parameters
        ----------
        self : OPdq
            An OPdq object

        Returns
        -------
        I_dict : dict
            Dict with key "Id", "Iq"
        """

        return {"Id": self.Id_ref, "Iq": self.Iq_ref}

    # Inlined from Methods.Simulation.OPdq.get_N0
    def get_N0(self, p: int | None = None) -> float:
        """Returns the Rotor speed

        Parameters
        ----------
        self : OPdq
            An OPdq object
        p: int
            pole pair number

        Returns
        -------
        N0 : float
            Rotor speed [rpm]
        """

        if self.N0 is not None:
            return self.N0

        # Compute N0 if possible
        if self.felec is None:
            raise InputError("OPdq object can't have felec and N0 both None")

        if p is None:
            machine = self.get_machine_from_parent()
            if machine is None:
                raise InputError("OPdq object can't find machine parent to compute N0")
            p = machine.get_pole_pair_number()

        self.N0 = self.felec * 60 / p

        return self.N0

    # Inlined from Methods.Simulation.OPdq.get_slip
    def get_slip(self) -> float:
        """Returns the Rotor mechanical slip

        Parameters
        ----------
        self : OPdq
            An OPdq object

        Returns
        -------
        slip : float
            Rotor mechanical slip (0 for synchronous machines)
        """

        return 0

    # Inlined from Methods.Simulation.OPdq.get_U0_UPhi0
    def get_U0_UPhi0(self) -> dict:
        """Return U0 and UPhi0
        Parameters
        ----------
        self : OPdq
            An OPdq object
        Returns
        -------
        U_dict : dict
            Dict with key "U0", "UPhi0"
        """

        if self.Ud_ref is None or self.Uq_ref is None:
            return {"U0": None, "UPhi0": None}

        else:
            Z = self.Ud_ref + 1j * self.Uq_ref
            return {"U0": abs(Z), "UPhi0": np.angle(Z) % (2 * np.pi)}

    # Inlined from Methods.Simulation.OPdq.get_Ud_Uq
    def get_Ud_Uq(self) -> dict:
        """Return Ud and Uq

        Parameters
        ----------
        self : OPdq
            An OPdq object

        Returns
        -------
        U_dict : dict
            Dict with key "Ud", "Uq"
        """

        return {"Ud": self.Ud_ref, "Uq": self.Uq_ref}

    # Inlined from Methods.Simulation.OPdq.set_I0_Phi0
    def set_I0_Phi0(self, I0: float, Phi0: float) -> None:
        """Set the value for I0 and IPhi0

        Parameters
        ----------
        self : OPdq
            An OPdq object
        I0 : float
            I0 value to set [Arms]
        Phi0 : float
            IPhi0 value to set [rad]
        """

        if I0 == 0:
            self.Id_ref = 0
            self.Iq_ref = 0
        else:
            Z = I0 * np.exp(1j * Phi0)
            self.Id_ref = Z.real
            self.Iq_ref = Z.imag

    # Inlined from Methods.Simulation.OPdq.set_Id_Iq
    def set_Id_Iq(self, Id: float, Iq: float) -> None:
        """Set the value for Id and Iq

        Parameters
        ----------
        self : OPdq
            An OPdq object
        Id : float
            Id value to set [Arms]
        Iq : float
            Iq value to set [Arms]
        """

        self.Id_ref = Id
        self.Iq_ref = Iq

    # Inlined from Methods.Simulation.OPdq.set_U0_UPhi0
    def set_U0_UPhi0(self, U0: float, UPhi0: float) -> None:
        """Set the value for U0 and UPhi0
        Parameters
        ----------
        self : OPdq
            An OPdq object
        U0 : float
            U0 value to set [Arms]
        UPhi0 : float
            UPhi0 value to set [rad]
        """

        if U0 == 0:
            self.Ud_ref = 0
            self.Uq_ref = 0
        else:
            Z = U0 * np.exp(1j * UPhi0)
            self.Ud_ref = Z.real
            self.Uq_ref = Z.imag

    # Inlined from Methods.Simulation.OPdq.set_Ud_Uq
    def set_Ud_Uq(self, Ud: float, Uq: float) -> None:
        """Set the value for Ud and Uq

        Parameters
        ----------
        self : OPdq
            An OPdq object
        Ud : float
            Ud value to set [Vrms]
        Uq : float
            Uq value to set [Vrms]
        """

        self.Ud_ref = Ud
        self.Uq_ref = Uq
