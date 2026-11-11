# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineSIPMSM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from ._error import MachineCheckError
from ._import import import_class
from .lam_slot_m import LamSlotM
from .lam_slot_wind import LamSlotWind
from .lamination import Lamination
from .machine_sync import MachineSync


@dataclass(eq=False)
class MachineSIPMSM(MachineSync):
    """Inset and Surface Permanent Magnet Synchronous Machine

    Attributes
    ----------
    rotor : LamSlotM or None
        Machine's Rotor
        Default: LamSlotM()
    stator : Lamination or None
        Machine's Stator
        Default: Lamination()
    """

    rotor: LamSlotM | None = field(
        default_factory=lambda: import_class("LamSlotM")(),
        metadata={"default_class": "LamSlotM"},
    )
    """Machine's Rotor"""
    stator: Lamination | None = field(
        default_factory=lambda: Lamination(), metadata={"default_class": "Lamination"}
    )
    """Machine's Stator"""

    # Inlined from Methods.Machine.MachineSIPMSM.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self : MachineSIPMSM
            A MachineSIPMSM object

        Returns
        -------
        None

        Raises
        _______
        M2C_WrongRotor
            The Rotor of a Machine_Type_2 must be a LamSlotM
        M2C_WrongStator
            The Stator of a Machine_Type_2 must be a LamSlotWind
        M2C_PError
            The stator and the rotor must have the same value for p
        M2C_MagnetTooLarge
            The airgap is too small for the magnet
        """

        super(type(self), self).check()

        if not isinstance(self.rotor, LamSlotM):
            raise self.M2C_WrongRotor(
                "The Rotor of a Machine_Type_2 must be a LamSlotM"
            )
        if not isinstance(self.stator, LamSlotWind):
            raise self.M2C_WrongStator(
                "The Stator of a Machine_Type_2 must be a LamSlotWind"
            )

        if self.rotor.get_pole_pair_number() != self.stator.get_pole_pair_number():
            raise self.M2C_PError(
                "The stator and the rotor must have the same value for p"
            )

        if self.rotor.is_internal and (
            self.rotor.w_slot.comp_radius_mid_active(self.rotor.Rext)
            + self.rotor.Hscr / 2.0
            > self.stator.Rint
        ):
            raise self.M2C_MagnetTooLarge("The airgap is too small for the magnet")

    # Inlined from Methods.Machine.MachineSIPMSM.get_machine_type
    def get_machine_type(self):
        """Return a string with the may information about the machine architecture

        Parameters
        ----------
        self : MachineSIPMSM
            A MachineSIPMSM object

        Returns
        -------
        str
            type_str: SIPMSM Zs/p (int/ext rotor)

        """

        type_str = "SIPMSM "

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

    class M2C_MagnetTooLarge(MachineCheckError):
        """ """

    class M2C_PError(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        values


        """

    class M2C_WrongRotor(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        Magnet


        """

    class M2C_WrongStator(MachineCheckError):
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
