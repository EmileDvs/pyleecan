# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineWRSM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from ._error import MachineCheckError
from ._import import import_class
from .lam_slot_wind import LamSlotWind
from .machine_sync import MachineSync


@dataclass(eq=False)
class MachineWRSM(MachineSync):
    """Wound Rotor Synchronous Machine

    Attributes
    ----------
    rotor : LamSlotWind or None
        Machine's Rotor
        Default: LamSlotWind()
    stator : LamSlotWind or None
        Machine's Stator
        Default: LamSlotWind()
    """

    rotor: LamSlotWind | None = field(
        default_factory=lambda: import_class("LamSlotWind")(),
        metadata={"default_class": "LamSlotWind"},
    )
    """Machine's Rotor"""
    stator: LamSlotWind | None = field(
        default_factory=lambda: import_class("LamSlotWind")(),
        metadata={"default_class": "LamSlotWind"},
    )
    """Machine's Stator"""

    # Inlined from Methods.Machine.MachineWRSM.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self : MachineWRSM
            A MachineWRSM object

        Returns
        -------
        None

        Raises
        _______
        M4C_WrongRotor
            The Rotor of a MachineWRSM must be a LamSlotWind
        M4C_WrongStator
            The Stator of a MachineWRSM must be a LamSlotWind
        M4C_PError
            The stator and the rotor winding must have the same value for p
        """

        super(type(self), self).check()

        if not isinstance(self.rotor, LamSlotWind):
            raise self.M4C_WrongRotor(
                "The Rotor of a MachineWRSM must be a LamSlotWind"
            )
        if not isinstance(self.stator, LamSlotWind):
            raise self.M4C_WrongStator(
                "The Stator of a MachineWRSM must be a LamSlotWind"
            )
        if self.rotor.winding.p != self.stator.winding.p:
            raise self.M4C_PError(
                "The stator and the rotor winding must have the same value for p"
            )

    # Inlined from Methods.Machine.MachineWRSM.get_machine_type
    def get_machine_type(self):
        """Return a string with the may information about the machine architecture

        Parameters
        ----------
        self : MachineWRSM
            A MachineWRSM object

        Returns
        -------
        type_str: str
            WRSM Zs/p (int/ext rotor)

        """

        type_str = "WRSM "

        if self.stator.slot.Zs is not None:
            type_str += str(self.stator.slot.Zs) + "s / "
        else:
            type_str += "?s / "

        if self.stator.winding.p is not None:
            type_str += str(self.stator.winding.p) + " p"
        else:
            type_str += "? p"

        if self.stator.is_internal:
            type_str += " (ext rotor)"
        else:
            type_str += " (int rotor)"

        return type_str

    class M4C_PError(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        different
            p value

        """

    class M4C_WrongRotor(MachineCheckError):
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

    class M4C_WrongStator(MachineCheckError):
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
