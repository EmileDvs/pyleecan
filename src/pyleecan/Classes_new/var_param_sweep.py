# Experimental dataclass generated from Generator/ClassesRef/Simulation/VarParamSweep.csv
"""Generated experimental dataclass; do not edit by hand."""

import itertools
from dataclasses import dataclass
from typing import ClassVar

from .param_explorer_set import ParamExplorerSet
from .var_param import VarParam


@dataclass(eq=False)
class VarParamSweep(VarParam):
    """Handle multisimulation by varying parameters

    Attributes
    ----------
    """

    NAME: ClassVar = "Parameter Sweep"

    # Inlined from Methods.Simulation.VarParamSweep.check_param
    def check_param(self):
        """Check VarParamSweep parameters validity

        Raises
        ------
        ParamExplorerError: Error in ParamExplorer setting
        VarParamSweepError: Error in VarParamSweep general setting
        DataKeeperError: Error in DataKeeper setting
        """
        # run the base class check first
        super(type(self), self).check_param()

        # Check ParamExplorers
        for paramexplorer in self.paramexplorer_list:
            if paramexplorer.setter is None:
                raise self.ParamExplorerError("ParamExplorer.setter must be defined")
            elif len(paramexplorer.symbol) == 0:
                raise self.ParamExplorerError("ParamExplorer.symbol cannot be empty")
            elif (
                isinstance(paramexplorer, ParamExplorerSet)
                and len(paramexplorer.value) == 0
            ):
                raise self.ParamExplorerError(
                    "ParamExplorer.value_list cannot be empty"
                )

        # Default simulation index
        N_simu = self.get_simu_number()

        # Keep every output if there is no DataKeeper defined
        if len(self.datakeeper_list) == 0 and self.is_keep_all_output is False:
            logger = self.get_logger()
            logger.warning(
                "No datakeeper has been define in VarParamSweep, setting is_keep_all_output as True."
            )
            self.is_keep_all_output = True

        # Check DataKeepers
        for datakeeper in self.datakeeper_list:
            if datakeeper.symbol in ["", None]:
                raise self.DataKeeperError("DataKeeper.symbol cannot be empty")
            elif datakeeper.keeper is None:
                raise self.DataKeeperError("DataKeeper.keeper must be defined")

    # Inlined from Methods.Simulation.VarParamSweep.generate_simulation_list
    def generate_simulation_list(self, ref_simu=None):
        """Generate all the simulation for the multi-simulation

        Parameters
        ----------
        self : VarSimu
            A VarSimu object
        ref_simu : Simulation
            Reference simulation to copy / update

        Returns
        -------
        multisim_dict : dict
            dictionary containing the simulation and paramexplorer list
        """

        # Build the list
        setter_list = []  # Store ParamExplorer setters
        params_value_dict = {}  # Store parameter value list per ParamExplorer
        params_symbol_list = []  # Store ParamExplorer symbols
        params_value_list = []  # Store ParamExplorer values to perform cartesian product
        multisim_shape = []

        n_param = 0
        # Add values and shape in the list
        for param_explorer in self.paramexplorer_list:
            n_param += 1
            params_value_dict[param_explorer.symbol] = []
            params_symbol_list.append(param_explorer.symbol)
            setter_list.append(param_explorer.setter)

            # Generate values
            values = param_explorer.get_value()
            params_value_list.append(values)
            multisim_shape.append(len(values))

        multisim_dict = {
            "paramexplorer_list": [],  # Setter's values
            "simulation_list": [],
        }

        # Cartesian product to generate every simulation
        for simu_param_values in itertools.product(*params_value_list):
            # Generate the simulation
            new_simu = ref_simu.copy()

            # Edit it using setter
            for setter, value, symbol in zip(
                setter_list, simu_param_values, params_symbol_list
            ):
                params_value_dict[symbol].append(value)
                setter(new_simu, value)

            # Add the simulation
            multisim_dict["simulation_list"].append(new_simu)

        # Create slices to extract ndarrays from multisim_values
        slices = ()
        for _ in multisim_shape:
            slices += (slice(None),)

        # Create ParamExplorerSet to be stored in XOutput
        for param_explorer in self.paramexplorer_list:
            multisim_dict["paramexplorer_list"].append(
                ParamExplorerSet(init_dict=param_explorer.as_dict(keep_function=True))
            )
            multisim_dict["paramexplorer_list"][-1].value = params_value_dict[
                param_explorer.symbol
            ]

        return multisim_dict

    # Inlined from Methods.Simulation.VarParamSweep.get_simu_number
    def get_simu_number(self):
        """Return the number of simulation defined by the Param Explorer

        Parameters
        ----------
        self : VarParamSweep
            A VarParamSweep object

        Returns
        -------
        nb_simu : int
            number of simulation
        """

        nb_simu = 1
        for paramexplorer in self.paramexplorer_list:
            nb_simu *= paramexplorer.get_N()

        return nb_simu

    class DataKeeperError(Exception):
        pass

    class ParamExplorerError(Exception):
        pass
