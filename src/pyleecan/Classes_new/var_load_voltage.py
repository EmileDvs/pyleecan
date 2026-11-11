# Experimental dataclass generated from Generator/ClassesRef/Simulation/VarLoadVoltage.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ..Functions_new.Simulation.VarSimu.get_elec_datakeeper_dict import (
    get_elec_datakeeper_dict,
)
from .input_voltage import InputVoltage
from .param_explorer_set import ParamExplorerSet
from .simulation import Simulation
from .var_load import VarLoad


@dataclass(eq=False)
class VarLoadVoltage(VarLoad):
    """Generate a multisimulation with InputVoltage at variable operating point

    Attributes
    ----------
    """

    # Inlined from Methods.Simulation.VarLoadVoltage.generate_simulation_list
    def generate_simulation_list(self, ref_simu=None):
        """Generate all the simulation for the multi-simulation

        Parameters
        ----------
        self : VarLoadVoltage
            A VarLoadVoltage object
        ref_simu : Simulation
            Reference simulation to copy / update

        Returns
        -------
        multisim_dict : dict
            dictionary containing the simulation and paramexplorer list
        """

        # Get InputCurrent list
        list_input = self.get_input_list()

        multisim_dict = {
            "paramexplorer_list": [],  # Setter's values
            "simulation_list": [],
        }

        # Create ParamExplorerSet
        #   This version uses a single ParamExplorerSet to define the simulation
        #   Other parameters can be stored in a dedicated ParamExplorerSet if needed
        multisim_dict["paramexplorer_list"].append(
            ParamExplorerSet(
                name="InputVoltage",
                symbol="In",
                unit="-",
                setter="simu.input",
                getter="simu.input",
                value=list_input,
            )
        )

        # Create Simulations 1 per load
        for input_obj in list_input:
            # Generate the simulation
            new_simu = ref_simu.copy()

            # Edit simulation
            new_simu.input = input_obj
            # Add simulation to the list
            multisim_dict["simulation_list"].append(new_simu)

        return multisim_dict

    # Inlined from Methods.Simulation.VarLoadVoltage.get_elec_datakeeper
    def get_elec_datakeeper(self, symbol_list, is_multi=False):
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

        dk_dict = get_elec_datakeeper_dict()
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

    # Inlined from Methods.Simulation.VarLoadVoltage.get_input_list
    def get_input_list(self):
        """Return a list of InputVoltage to set the Operating point"""

        # Check that the object has the correct type
        assert isinstance(self.parent, Simulation)
        ref_simu = self.parent
        assert isinstance(ref_simu.input, InputVoltage)

        OP_list = self.OP_matrix.get_OP_list()
        N_simu = len(OP_list)

        # Generate initial input_list
        ref_input = ref_simu.input.copy()
        input_list = [ref_input.copy() for ii in range(N_simu)]

        # Set default time vector (enforce definition Nt_tot, Nrev)
        if ref_input.Nt_tot is None:
            Nt_tot = len(ref_input.time.get_data())
        else:
            Nt_tot = ref_input.Nt_tot

        # Update OP according to OP_matrix
        for ii in range(N_simu):
            input_list[ii].OP = OP_list[ii]
            # Edit time vector
            input_list[ii].time = None
            input_list[ii].Nt_tot = Nt_tot
            input_list[ii].Nrev = ref_input.Nrev

        return input_list
