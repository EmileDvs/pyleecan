# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineSRM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from ._error import MachineCheckError
from ._import import import_class
from .lam_slot import LamSlot
from .lam_slot_wind import LamSlotWind
from .machine_sync import MachineSync


@dataclass(eq=False)
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

    rotor: LamSlot | None = field(
        default_factory=lambda: import_class("LamSlot")(),
        metadata={"default_class": "LamSlot"},
    )
    """Machine's Rotor"""
    stator: LamSlotWind | None = field(
        default_factory=lambda: import_class("LamSlotWind")(),
        metadata={"default_class": "LamSlotWind"},
    )
    """Machine's Stator"""

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
            raise self.SRM_WrongRotor("The Rotor of a MachineSRM must be a LamSlot")
        if not isinstance(self.stator, LamSlotWind):
            raise self.SRM_WrongStator(
                "The Stator of a MachineSRM must be a LamSlotWind"
            )

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

    class SRM_WrongRotor(MachineCheckError):
        pass

    class SRM_WrongStator(MachineCheckError):
        pass
