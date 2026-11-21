import numpy as np
from ....Classes_new.simulation.simulation import Simulation


def get_elec_datakeeper(self, symbol_list: list, is_multi: bool = False) -> list:
    """Generate DataKeepers to store by default results from electric module
    Parameters
    ----------
    self: VarLoadVoltage
        A VarLoadVoltage object
    symbol_list : list
        List of the existing datakeeper (to avoid duplicate)
    is_multi : bool
        True for multi-simulation of multi-simulation
    Returns
    -------
    dk_list: list
        list of DataKeeper
    """

    dk_dict = self.get_elec_datakeeper_dict()
    dk_list = []

    if not is_multi:
        quantity_list = ["Ud", "Uq"]
        # Add "U0", "UPhi0" for Async machine
        if (
            self.parent is not None
            and isinstance(self.parent, Simulation)
            and not self.parent.machine.is_synchronous()
        ):
            quantity_list.extend(["U0", "UPhi0"])
        elif (
            self.parent is not None
            and self.parent.parent is not None
            and isinstance(self.parent.parent, Simulation)
            and not self.parent.parent.machine.is_synchronous()
        ):
            quantity_list.extend(["U0", "UPhi0"])
        # Add slip if provided in the OP_matrix
        if self.OP_matrix is not None and self.OP_matrix.has_slip():
            quantity_list.append("slip")
        # Add torque if provided in the OP_matrix
        if self.OP_matrix is not None and self.OP_matrix.has_Tem():
            quantity_list.append("Tem_av_ref")

    # Save Id
    if not is_multi:
        for key in quantity_list:
            if key not in symbol_list:
                dk_list.append(dk_dict[key])

    return dk_list
