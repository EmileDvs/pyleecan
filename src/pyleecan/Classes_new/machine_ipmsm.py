# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineIPMSM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from ._error import MachineCheckError
from .lam_h import LamH
from .lam_hole import LamHole
from .lam_slot_wind import LamSlotWind
from .lamination import Lamination
from .machine_sync import MachineSync


@dataclass(eq=False)
class MachineIPMSM(MachineSync):
    """Interior Permanent Magnet Synchronous Machine

    Attributes
    ----------
    rotor : LamH or None
        Machine's Rotor
        Default: LamH()
    stator : Lamination or None
        Machine's Stator
        Default: Lamination()
    """

    rotor: LamH | None = field(
        default_factory=lambda: LamH(), metadata={"default_class": "LamH"}
    )
    """Machine's Rotor"""
    stator: Lamination | None = field(
        default_factory=lambda: Lamination(), metadata={"default_class": "Lamination"}
    )
    """Machine's Stator"""

    # Inlined from Methods.Machine.MachineIPMSM.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self : MachineIPMSM
            A MachineIPMSM object

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
            raise self.M3C_WrongRotor("The Rotor of a Machine_Type_3 must be a LamHole")
        if not isinstance(self.stator, LamSlotWind):
            raise self.M3C_WrongStator(
                "The Stator of a Machine_Type_3 must be a LamSlotWind"
            )

        if self.rotor.get_pole_pair_number() != self.stator.get_pole_pair_number():
            raise self.M3C_PError(
                "The stator and the rotor must have the same value for p"
            )

    # Inlined from Methods.Machine.MachineIPMSM.get_machine_type
    def get_machine_type(self):
        """Return a string with the may information about the machine architecture

        Parameters
        ----------
        self : MachineIPMSM
            A MachineIPMSM object

        Returns
        -------
        type_str: str
            IPMSM Zs/Zr/p (int/ext rotor)

        """

        type_str = "IPMSM "
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

    class M3C_PError(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        values


        """

    class M3C_WrongRotor(MachineCheckError):
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

    class M3C_WrongStator(MachineCheckError):
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
