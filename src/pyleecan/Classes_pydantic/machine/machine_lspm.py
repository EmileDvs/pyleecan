# Experimental pydantic model generated from Generator/ClassesRef/Machine/MachineLSPM.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from ...classes_common.errors import MachineCheckError
from .lam_slot_wind import LamSlotWind
from .lam_squirrel_cage_mag import LamSquirrelCageMag
from .machine_sync import MachineSync


class MachineLSPM(MachineSync):
    """Line Start Permanent Magnet Machine

    Attributes
    ----------
    rotor : LamSquirrelCageMag or None
        Machine's Rotor
        Default: LamSquirrelCageMag()
    stator : LamSlotWind or None
        Machine's Stator
        Default: LamSlotWind()
    """

    rotor: LamSquirrelCageMag | None = Field(
        default_factory=lambda: LamSquirrelCageMag()
    )
    """Machine's Rotor"""
    stator: LamSlotWind | None = Field(default_factory=lambda: LamSlotWind())
    """Machine's Stator"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.MachineLSPM.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self : MachineLSPM
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

        if self.rotor.get_pole_pair_number() != self.stator.get_pole_pair_number():
            raise MachineCheckError(
                "The stator and the rotor must have the same value for p"
            )

    # Inlined from Methods.Machine.MachineLSPM.get_machine_type
    def get_machine_type(self):
        """Return a string with the may information about the machine architecture

        Parameters
        ----------
        self : MachineLSPM
            A MachineLSPM object

        Returns
        -------
        type_str: str
            SyRM Zs/Zr/p (int/ext rotor)

        """

        type_str = "LSPM "
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
