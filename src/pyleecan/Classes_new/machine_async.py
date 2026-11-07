# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineAsync.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .machine import Machine


@dataclass(eq=False)
class MachineAsync(Machine):
    """Abstract class for asynchronous machines

    Attributes
    ----------
    """

    # Inlined from Methods.Machine.MachineAsync.comp_desc_dict
    def comp_desc_dict(self):
        """Compute a dictionary with the main parameters/output of the machine

        Parameters
        ----------
        self : Machine
            A Machine object

        Returns
        -------
        desc_dict: list
            list of dictionary containing the main parameters of the machine
        """

        desc_dict = Machine.comp_desc_dict(self)

        Zr_dict = dict(
            {
                "name": "Zr",
                "path": "machine.rotor.slot.Zs",
                "verbose": "Rotor slot number",
                "type": int,
                "unit": "",
                "is_input": True,
                "value": self.rotor.slot.Zs,
            }
        )
        desc_dict.insert(2, Zr_dict)
        return desc_dict

    # Inlined from Methods.Machine.MachineAsync.is_synchronous
    def is_synchronous(self):
        """Return if a machine is synchronous or not

        Parameters
        ----------
        self : MachineAsync
            A MachineAsync

        Returns
        -------
        is_synchronous: bool
            Asynchronous machines are not synchronous

        """
        return False
