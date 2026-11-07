# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineSCIM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .lam_slot_wind import LamSlotWind
from .lam_squirrel_cage import LamSquirrelCage
from .machine_dfim import MachineDFIM


@dataclass(eq=False)
class MachineSCIM(MachineDFIM):
    """Squirrel Cage Induction Machine

    Attributes
    ----------
    """

    # Inlined from Methods.Machine.MachineSCIM.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self : MachineSCIM
            A MachineSCIM object

        Returns
        -------
        None

        Raises
        _______
        M1C_WrongRotor
            The Rotor of a MachineSCIM must be a LamSquirrelCage
        M1C_WrongStator
            The Stator of a MachineSCIM must be a LamSlotWind
        M1C_SquirrelCagePError
            The stator and the rotor winding must have the same value for p
        M1C_RingTooLarge
            The Ring is larger than the stator internal radius
        """
        # Call Machine check, skip MachineDFIM check
        self.__class__.__bases__[0].__bases__[0].check(self)

        if not isinstance(self.rotor, LamSquirrelCage):
            raise M1C_WrongRotor("The Rotor of a MachineSCIM must be a LamSquirrelCage")
        if not isinstance(self.stator, LamSlotWind):
            raise M1C_WrongStator("The Stator of a MachineSCIM must be a LamSlotWind")
        if self.rotor.winding.p != self.stator.winding.p:
            raise M1C_SquirrelCagePError(
                "The stator and the rotor winding must have the same value for p"
            )
        if self.rotor.is_internal and (
            self.rotor.slot.comp_radius_mid_active() + self.rotor.Hscr / 2.0
            > self.stator.Rint
        ):
            raise M1C_RingTooLarge("The Ring is larger than the stator internal radius")

    # Inlined from Methods.Machine.MachineSCIM.get_machine_type
    def get_machine_type(self):
        """Return a string with the may information about the machine architecture

        Parameters
        ----------
        self : MachineSCIM
            A MachineSCIM object

        Returns
        -------
        type_str: str
            SCIM Zs/Zr/p (int/ext rotor)

        """

        type_str = "SCIM "

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

    class M1C_RingTooLarge(MachineCheckError):
        """ """

    class M1C_SquirrelCagePError(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        winding
            have a different p value as the rotor one

        """

    class M1C_WrongRotor(MachineCheckError):
        """ """

    class M1C_WrongStator(MachineCheckError):
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


MachineCheckError = MachineSCIM.MachineCheckError
M1C_RingTooLarge = MachineSCIM.M1C_RingTooLarge
M1C_SquirrelCagePError = MachineSCIM.M1C_SquirrelCagePError
M1C_WrongRotor = MachineSCIM.M1C_WrongRotor
M1C_WrongStator = MachineSCIM.M1C_WrongStator
