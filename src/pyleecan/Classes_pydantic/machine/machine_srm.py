# Experimental pydantic model generated from Generator/ClassesRef/Machine/MachineSRM.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from ...classes_common.errors import SRM_WrongRotor, SRM_WrongStator
from .lam_slot import LamSlot
from .lam_slot_wind import LamSlotWind
from .machine_sync import MachineSync


class MachineSRM(MachineSync):
    """Switched Reluctance Machine

    Attributes
    ----------
    rotor : LamSlot or None
        Machine's Rotor
        Default: LamSlot()
    stator : LamSlotWind or None
        Machine's Stator
        Default: LamSlotWind()
    """

    rotor: LamSlot | None = Field(default_factory=lambda: LamSlot())
    """Machine's Rotor"""
    stator: LamSlotWind | None = Field(default_factory=lambda: LamSlotWind())
    """Machine's Stator"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.MachineSRM.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self : MachineSRM
            The machine object to check

        Returns
        -------
        None


        Raises
        _______
        SRM_WrongRotor
            The Rotor of a MachineSRM must be a LamSlot
        SRM_WrongStator
            The Stator of a MachineSRM must be a LamSlotWind

        """

        super(type(self), self).check()

        if not isinstance(self.rotor, LamSlot):
            raise SRM_WrongRotor("The Rotor of a MachineSRM must be a LamSlot")
        if not isinstance(self.stator, LamSlotWind):
            raise SRM_WrongStator("The Stator of a MachineSRM must be a LamSlotWind")

    # Inlined from Methods.Machine.MachineSRM.get_machine_type
    def get_machine_type(self):
        """Return a string with the main information about the machine architecture

        Parameters
        ----------
        self : MachineSRM
            A MachineSRM object

        Returns
        -------
        type_str: str
            SRM Zs/Zr/p (int/ext rotor)

        """

        type_str = "SRM "
        if self.stator.slot is None:
            type_str += "0s / "
        elif self.stator.slot.Zs is not None:
            type_str += str(self.stator.slot.Zs) + "s / "
        else:
            type_str += "?s / "

        if self.rotor.slot is None:
            type_str += "0r / "
        elif self.rotor.slot.Zs is not None:
            type_str += str(self.rotor.slot.Zs) + "r / "
        else:
            type_str += "?r / "

        if self.stator.winding.qs is not None:
            type_str += str(self.stator.winding.qs) + "qs"
        else:
            type_str += "?qs"

        if self.stator.is_internal:
            type_str += " (ext rotor)"
        else:
            type_str += " (int rotor)"

        return type_str

    # Inlined from Methods.Machine.MachineSRM.get_pole_pair_number
    def get_pole_pair_number(self):
        """Returns the number of pole pairs of the machine

        Parameters
        ----------
        self : MachineSRM
            MachineSRM object

        Returns
        -------
        p: int
            Pole pair number of the machine
        """

        return self.rotor.get_Zs()

    # Inlined from Methods.Machine.MachineSRM.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pole pairs of the machine

        Parameters
        ----------
        self : MachineSRM
            MachineSRM object
        p: int
            Pole pair number of the machine
        """

        # Set pole pair number for stator only
        self.stator.set_pole_pair_number(p)
