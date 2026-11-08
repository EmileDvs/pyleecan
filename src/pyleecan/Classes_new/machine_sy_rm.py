# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineSyRM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._error import MachineCheckError
from .lam_hole import LamHole
from .lam_slot_wind import LamSlotWind
from .machine_sync import MachineSync


@dataclass(eq=False)
class MachineSyRM(MachineSync):
    """Synchronous Reluctance Machine

    Attributes
    ----------
    rotor : LamHole or None
        Machine's Rotor
        Default: None
    stator : LamSlotWind or None
        Machine's Stator
        Default: None
    """

    rotor: LamHole | None = None
    """Machine's Rotor"""
    stator: LamSlotWind | None = None
    """Machine's Stator"""

    # Inlined from Methods.Machine.MachineSyRM.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self : MachineSyRM
            The machine object to check

        Returns
        -------
        None


        Raises
        _______
        M3C_WrongRotor
            The Rotor of a Machine_Type_3 must be a LamHole
        M3C_WrongStator
            The Stator of a Machine_Type_3 must be a LamSlotWind
        M3C_PError
            The stator and the rotor must have the same value for p

        """

        super(type(self), self).check()

        if not isinstance(self.rotor, LamHole):
            raise self.MSy_WrongRotor("The Rotor of a MachineSyRM must be a LamHole")
        if not isinstance(self.stator, LamSlotWind):
            raise self.MSy_WrongStator(
                "The Stator of a MachineSyRM must be a LamSlotWind"
            )

        if self.rotor.get_pole_pair_number() != self.stator.get_pole_pair_number():
            raise self.MSy_PError(
                "The stator and the rotor must have the same value for p"
            )

    # Inlined from Methods.Machine.MachineSyRM.get_machine_type
    def get_machine_type(self):
        """Return a string with the may information about the machine architecture

        Parameters
        ----------
        self : MachineSyRM
            A MachineSyRM object

        Returns
        -------
        type_str: str
            SyRM Zs/Zr/p (int/ext rotor)

        """

        type_str = "SyRM "
        if self.stator.slot.Zs is not None:
            type_str += str(self.stator.slot.Zs) + "s / "
        else:
            type_str += "?s / "

        if self.stator.winding.p is not None:
            type_str += str(self.stator.winding.p) + "p"
        else:
            type_str += "?p"

        if self.stator.is_internal:
            type_str += " (ext rotor)"
        else:
            type_str += " (int rotor)"

        return type_str

    class MSy_PError(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        values


        """

    class MSy_WrongRotor(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        with
            Magnet

        """

    class MSy_WrongStator(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        with
            Winding

        """
