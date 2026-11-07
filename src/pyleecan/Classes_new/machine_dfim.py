# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineDFIM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .lam_slot_wind import LamSlotWind
from .machine_async import MachineAsync


@dataclass(eq=False)
class MachineDFIM(MachineAsync):
    """Doubly Fed Induction Machine

    Attributes
    ----------
    rotor : LamSlotWind or None
        Machine's Rotor
        Default: None
    stator : LamSlotWind or None
        Machine's Stator
        Default: None
    """

    rotor: LamSlotWind | None = None
    """Machine's Rotor"""
    stator: LamSlotWind | None = None
    """Machine's Stator"""

    # Inlined from Methods.Machine.MachineDFIM.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self : MachineDFIM
            A MachineDFIM object

        Returns
        -------
        None

        Raises
        _______
        M4C_WrongRotor
            The Rotor of a MachineDFIM must be a LamSlotWind
        M4C_WrongStator
            The Stator of a MachineDFIM must be a LamSlotWind
        M4C_PError
            The stator and the rotor winding must have the same value for p
        """

        super(type(self), self).check()

        if not isinstance(self.rotor, LamSlotWind):
            raise M4C_WrongRotor("The Rotor of a MachineDFIM must be a LamSlotWind")
        if not isinstance(self.stator, LamSlotWind):
            raise M4C_WrongStator("The Stator of a MachineDFIM must be a LamSlotWind")
        if self.rotor.winding.p != self.stator.winding.p:
            raise M4C_PError(
                "The stator and the rotor winding must have the same value for p"
            )

    # Inlined from Methods.Machine.MachineDFIM.get_machine_type
    def get_machine_type(self):
        """Return a string with the may information about the machine architecture

        Parameters
        ----------
        self : MachineDFIM
            A MachineDFIM object

        Returns
        -------
        type_str: str
            DFIM Zs/Zr/p (int/ext rotor)

        """

        type_str = "DFIM "

        if self.stator.slot.Zs is not None:
            type_str += str(self.stator.slot.Zs) + "s / "
        else:
            type_str += "?s / "

        if self.rotor.slot.Zs is not None:
            type_str += str(self.rotor.slot.Zs) + "r / "
        else:
            type_str += "?r / "

        if self.stator.winding.p is not None:
            type_str += str(self.stator.winding.p) + "p"
        else:
            type_str += "?p"

        if self.stator.is_internal:
            type_str += " (ext rotor)"
        else:
            type_str += " (int rotor)"

        return type_str

    class MachineCheckError(Exception):
        """ """

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


MachineCheckError = MachineDFIM.MachineCheckError
M4C_PError = MachineDFIM.M4C_PError
M4C_WrongRotor = MachineDFIM.M4C_WrongRotor
M4C_WrongStator = MachineDFIM.M4C_WrongStator
