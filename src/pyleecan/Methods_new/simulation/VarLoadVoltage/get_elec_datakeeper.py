from ....classes_common.parents import ancestor_with
import numpy as np
from ....Classes_new.simulation.simulation import Simulation


def get_elec_datakeeper(
    self, symbol_list: list, is_multi: bool = False, simu: Simulation | None = None
) -> list:
    """Generate DataKeepers to store by default results from electric module
    Parameters
    ----------
    self: VarLoadVoltage
        A VarLoadVoltage object
    symbol_list : list
        List of the existing datakeeper (to avoid duplicate)
    is_multi : bool
        True for multi-simulation of multi-simulation
    simu : Simulation, optional
        Simulation of the object (default: the parent, or its parent for a
        multi-simulation of multi-simulation)
    Returns
    -------
    dk_list: list
        list of DataKeeper
    """

    # The simulation: the parent, or the grandparent (VarSimu in a VarSimu)
    simu = ancestor_with(self, "machine", simu, "simu")
    dk_dict = self.get_elec_datakeeper_dict()
    dk_list = []

    if not is_multi:
        quantity_list = ["Ud", "Uq"]
        # Add "U0", "UPhi0" for Async machine
        if isinstance(simu, Simulation) and not simu.machine.is_synchronous():
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
