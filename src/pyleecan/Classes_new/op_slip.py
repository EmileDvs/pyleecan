# Experimental dataclass generated from Generator/ClassesRef/Simulation/OPslip.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._error import InputError
from .op import OP


@dataclass(eq=False)
class OPslip(OP):
    """Operating Point defined with slip, I0

    Attributes
    ----------
    I0_ref : float or None
        Current rms value
        Unit: Arms; Default: None
    IPhi0_ref : float or None
        Current phase
        Unit: rad; Default: None
    slip_ref : float
        Rotor mechanical slip
        Default: 0
    U0_ref : float or None
        stator voltage (phase to neutral)
        Unit: Vrms; Default: None
    UPhi0_ref : float or None
        Voltage phase
        Unit: rad; Default: None
    """

    I0_ref: float | None = None
    """Current rms value"""
    IPhi0_ref: float | None = None
    """Current phase"""
    slip_ref: float = 0
    """Rotor mechanical slip"""
    U0_ref: float | None = None
    """stator voltage (phase to neutral)"""
    UPhi0_ref: float | None = None
    """Voltage phase"""

    # Inlined from Methods.Simulation.OPslip.get_felec
    def get_felec(self, p=None):
        """Returns the electrical frequency

        Parameters
        ----------
        self : OPslip
            An OPslip object
        p: int
            pole pair number

        Returns
        -------
        felec : float
            Electrical Frequency [Hz]
        """

        if self.slip_ref is None:
            raise InputError("OPslip object can't have felec and slip_ref both None")

        if p is None and (self.felec is None or self.N0 is None):
            machine = self.get_machine_from_parent()
            if machine is None:
                raise InputError(
                    "OPslip object can't find machine parent to compute felec"
                )

            p = machine.get_pole_pair_number()

        if self.felec is not None:
            return self.felec

        # Compute felec if possible
        if self.N0 is None:
            raise InputError("OPslip object can't have felec and N0 both None")

        if self.slip_ref != 1:
            self.felec = self.N0 * p / (60 * (1 - self.slip_ref))
        else:
            raise InputError(
                "Cannot calculate felec if slip_ref=1, felec must be enforced and N0 set to None or 0s"
            )

        return self.felec

    # Inlined from Methods.Simulation.OPslip.get_I0_Phi0
    def get_I0_Phi0(self):
        """Return I0 and Phi0

        Parameters
        ----------
        self : OPslip
            An OPslip object

        Returns
        -------
        I_dict : dict
            Dict with key "I0", "Phi0"
        """

        return {"I0": self.I0_ref, "Phi0": self.IPhi0_ref}

    # Inlined from Methods.Simulation.OPslip.get_Id_Iq
    def get_Id_Iq(self):
        """Return Id and Iq

        Parameters
        ----------
        self : OPslip
            An OPslip object

        Returns
        -------
        I_dict : dict
            Dict with key "Id", "Iq"
        """

        if self.IPhi0_ref is None:
            IPhi0_ref = 0
        else:
            IPhi0_ref = self.IPhi0_ref

        Z = self.I0_ref * np.exp(1j * IPhi0_ref)

        return {"Id": Z.real, "Iq": Z.imag}

    # Inlined from Methods.Simulation.OPslip.get_N0
    def get_N0(self, p=None):
        """Returns the Rotor speed

        Parameters
        ----------
        self : OPslip
            An OPslip object
        p: int
            pole pair number

        Returns
        -------
        N0 : float
            Rotor speed [rpm]
        """

        if self.slip_ref is None:
            raise InputError("OPslip object can't have felec and slip_ref both None")

        if self.N0 is not None:
            return self.N0

        # Compute N0 if possible
        if self.felec is None:
            raise InputError("OPslip object can't have felec and N0 both None")

        if p is None:
            machine = self.get_machine_from_parent()
            if machine is None:
                raise InputError(
                    "OPslip object can't find machine parent to compute N0"
                )

            p = machine.get_pole_pair_number()

        if self.slip_ref == 1 and self.N0 not in [0, None]:
            raise InputError(
                "Speed and slip values are not consistent: slip_ref=1 and N0 not in [0, None]"
            )
        if self.N0 == 0 and self.slip_ref not in [1, None]:
            raise InputError(
                "Speed and slip values are not consistent: N0=0 and slip_ref not in [1, None]"
            )

        self.N0 = 60 * (1 - self.slip_ref) * self.felec / p

        return self.N0

    # Inlined from Methods.Simulation.OPslip.get_slip
    def get_slip(self):
        """Returns the Rotor mechanical slip

        Parameters
        ----------
        self : OPslip
            An OPslip object

        Returns
        -------
        slip : float
            Rotor mechanical slip
        """

        return self.slip_ref

    # Inlined from Methods.Simulation.OPslip.get_U0_UPhi0
    def get_U0_UPhi0(self):
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

        return {"U0": self.U0_ref, "UPhi0": self.UPhi0_ref}

    # Inlined from Methods.Simulation.OPslip.get_Ud_Uq
    def get_Ud_Uq(self):
        """Return Ud and Uq

        Parameters
        ----------
        self : OPslip
            An OPslip object

        Returns
        -------
        U_dict : dict
            Dict with key "Ud", "Uq"
        """

        if self.UPhi0_ref is None:
            UPhi0_ref = 0
        else:
            UPhi0_ref = self.UPhi0_ref

        Z = self.U0_ref * np.exp(1j * UPhi0_ref)

        return {"Ud": Z.real, "Uq": Z.imag}

    # Inlined from Methods.Simulation.OPslip.set_I0_Phi0
    def set_I0_Phi0(self, I0, Phi0):
        """Set the value for I0 and IPhi0

        Parameters
        ----------
        self : OPslip
            An OPslip object
        I0 : float
            I0 value to set [Arms]
        Phi0 : float
            IPhi0 value to set [rad]
        """

        self.I0_ref = I0
        self.IPhi0_ref = Phi0

    # Inlined from Methods.Simulation.OPslip.set_Id_Iq
    def set_Id_Iq(self, Id, Iq):
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

        if Id == 0 and Iq == 0:
            self.I0_ref = 0
            self.IPhi0_ref = 0
        else:
            Z = Id + 1j * Iq
            self.I0_ref = abs(Z)
            self.IPhi0_ref = np.angle(Z)

    # Inlined from Methods.Simulation.OPslip.set_U0_UPhi0
    def set_U0_UPhi0(self, U0, UPhi0):
        """Set the value for I0 and IPhi0

        Parameters
        ----------
        self : OPslip
            An OPslip object
        U0 : float
            U0 value to set [Arms]
        UPhi0 : float
            UPhi0 value to set [rad]
        """

        self.U0_ref = U0
        self.UPhi0_ref = UPhi0

    # Inlined from Methods.Simulation.OPslip.set_Ud_Uq
    def set_Ud_Uq(self, Ud, Uq):
        """Set the value for Ud and Uq

        Parameters
        ----------
        self : OPdq
            An OPdq object
        Ud : float
            Ud value to set [Arms]
        Uq : float
            Uq value to set [Arms]
        """

        if Ud == 0 and Uq == 0:
            self.U0_ref = 0
            self.UPhi0_ref = 0
        else:
            Z = Ud + 1j * Uq
            self.U0_ref = abs(Z)
            self.UPhi0_ref = np.angle(Z)
