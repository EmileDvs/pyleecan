# File generated according to Generator/ClassesRef/Simulation/VarSimu.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/VarSimu"""

from os import linesep
from sys import getsizeof

import numpy as np

from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass
from pyleecan.Classes.DataKeeper import DataKeeper
from pyleecan.Classes.ElecLUTdq import ElecLUTdq
from pyleecan.Classes.MagFEMM import MagFEMM
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.save import save
from pyleecan.Functions.Simulation.VarSimu.get_elec_datakeeper_dict import (
    get_elec_datakeeper_dict,
)
from pyleecan.Functions.Simulation.VarSimu.log_datakeeper_step_result import (
    log_datakeeper_step_result,
)
from pyleecan.Functions.Simulation.VarSimu.run_multisim_step import run_multisim_step


class VarSimu(FrozenClass):
    """Abstract class for the multi-simulation"""

    VERSION = 1

    # cf Methods.Simulation.VarSimu.check_param
    def check_param(self):
        """Check VarParamSweep parameters validity"""
        if type(self).__name__ == "VarSimu":
            raise VarSimuError(
                "VarSimu is an abstract class, please create one of its daughters."
            )

        Simulation = import_class("pyleecan.Classes", "Simulation")
        # Check for simulation or VarSimu
        if self.parent is None or not isinstance(self.parent, Simulation):
            raise VarSimuError("VarSimu object must be inside a Simulation object")

    # cf Methods.Simulation.VarSimu.gen_datakeeper_list
    def gen_datakeeper_list(self, ref_simu):
        """Generate default DataKeepers according the reference simulation type"""
        datakeeper_list = []

        # To avoid adding twice a DataKeeper
        symbol_list = [dk.symbol for dk in self.datakeeper_list]
        # For multi-simulation of multi-simulation (different DataKeepe<r)
        is_multi = ref_simu.var_simu is not None
        # Dynamic import to avoid loop
        InputCurrent = import_class("pyleecan.Classes", "InputCurrent", "")

        # Save speed
        if not is_multi and "N0" not in symbol_list:
            datakeeper_list.append(
                DataKeeper(
                    name="Speed",
                    symbol="N0",
                    unit="rpm",
                    keeper="lambda output: output.elec.OP.get_N0()",
                )
            )

        # Get default datakeeper
        if ref_simu.elec or isinstance(ref_simu.input, InputCurrent):
            datakeeper_list.extend(
                self.get_elec_datakeeper(symbol_list, is_multi=is_multi)
            )
        if ref_simu.mag:
            datakeeper_list.extend(
                self.get_mag_datakeeper(symbol_list, is_multi=is_multi)
            )
        if ref_simu.force:
            datakeeper_list.extend(
                self.get_force_datakeeper(symbol_list, is_multi=is_multi)
            )

        self.datakeeper_list.extend(datakeeper_list)

    # cf Methods.Simulation.VarSimu.generate_simulation_list
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
        raise VarSimuError(
            "VarSimu is an abstract class, please create one of its daughters."
        )

    # cf Methods.Simulation.VarSimu.get_elec_datakeeper
    def get_elec_datakeeper(self, symbol_list, is_multi=False):
        """Generate DataKeepers to store by default results from electric module
        Parameters
        ----------
        self: VarLoad
            A VarLoad object
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
        quantity_list = ["Id", "Iq", "Ud", "Uq"]

        # Save Id
        if not is_multi:
            for key in quantity_list:
                if key not in symbol_list:
                    dk_list.append(dk_dict[key])

        return dk_list

    # cf Methods.Simulation.VarSimu.get_force_datakeeper
    def get_force_datakeeper(self, symbol_list, is_multi=False):
        """
        Generate DataKeepers to store by default results from force module

        Parameters
        ----------
        self: VarLoad
            A VarLoad object
        symbol_list : list
            List of the existing datakeeper (to avoid duplicate)
        is_multi : bool
            True for multi-simulation of multi-simulation

        Returns
        -------
        dk_list: list
            list of DataKeeper
        """
        dk_list = []

        return dk_list

    # cf Methods.Simulation.VarSimu.get_mag_datakeeper
    def get_mag_datakeeper(self, symbol_list, is_multi=False):
        """
        Generate DataKeepers to store by default results from magnetic module

        Parameters
        ----------
        self: VarLoad
            A VarLoad object
        symbol_list : list
            List of the existing datakeeper (to avoid duplicate)
        is_multi : bool
            True for multi-simulation of multi-simulation

        Returns
        -------
        dk_list: list
            list of DataKeeper
        """
        dk_list = []
        error_nan = "lambda simu: np.nan"
        if is_multi:
            # Max Average torque Datakeeper
            if "Max_Tem_av" not in symbol_list:
                dk_list.append(
                    DataKeeper(
                        name="Max Average Torque",
                        symbol="Max_Tem_av",
                        unit="N.m",
                        keeper="lambda output: max([val for val in output.xoutput_dict['Tem_av'].result if val is not None]) if output.xoutput_dict['Tem_av'].result[0] is not None else None",
                        error_keeper=error_nan,
                    )
                )
            # Max Peak to Peak Torque ripple
            if "Max_Tem_rip_pp" not in symbol_list:
                dk_list.append(
                    DataKeeper(
                        name="Max Peak to Peak Torque ripple",
                        symbol="Max_Tem_rip_pp",
                        unit="N.m",
                        keeper="lambda output: max([val for val in output.xoutput_dict['Tem_rip_pp'].result if val is not None]) if output.xoutput_dict['Tem_rip_pp'].result[0] is not None else None",
                        error_keeper=error_nan,
                    )
                )
            # Max Peak to Peak Torque ripple normalized
            if "Max_Tem_rip_norm" not in symbol_list:
                dk_list.append(
                    DataKeeper(
                        name="Max Peak to Peak Torque ripple normalized",
                        symbol="Max_Tem_rip_norm",
                        unit="-",
                        keeper="lambda output: max([val for val in output.xoutput_dict['Tem_rip_norm'].result if val is not None]) if output.xoutput_dict['Tem_rip_norm'].result[0] is not None else None",
                        error_keeper=error_nan,
                    )
                )
        else:
            # Average torque Datakeeper
            if "Tem_av" not in symbol_list:
                dk_list.append(
                    DataKeeper(
                        name="Average Torque",
                        symbol="Tem_av",
                        unit="N.m",
                        keeper="lambda out: out.mag.Tem_av",
                        error_keeper=error_nan,
                    )
                )
            # Peak to Peak Torque ripple
            if "Tem_rip_pp" not in symbol_list:
                dk_list.append(
                    DataKeeper(
                        name="Peak to Peak Torque ripple",
                        symbol="Tem_rip_pp",
                        unit="N.m",
                        keeper="lambda out: out.mag.Tem_rip_pp",
                        error_keeper=error_nan,
                    )
                )
            # Peak to Peak Torque ripple normalized
            if "Tem_rip_norm" not in symbol_list:
                dk_list.append(
                    DataKeeper(
                        name="Peak to Peak Torque ripple normalized",
                        symbol="Tem_rip_norm",
                        unit="-",
                        keeper="lambda out: out.mag.Tem_rip_norm",
                        error_keeper=error_nan,
                    )
                )
            # Output Power Datakeeper
            if "Pem_av" not in symbol_list:
                dk_list.append(
                    DataKeeper(
                        name="Output Power",
                        symbol="Pem_av",
                        unit="W",
                        keeper="lambda out: out.mag.Pem_av",
                        error_keeper=error_nan,
                    )
                )
        return dk_list

    # cf Methods.Simulation.VarSimu.get_ref_simu_index
    def get_ref_simu_index(self, ref_simu, simu_dict):
        """Get the index of the reference simulation (None if must be computed)

        Parameters
        ----------
        self : VarSimu
            A VarSimu object
        ref_simu : Simulation
            A Simulation object (reference simulation)
        simu_dict : dict
            Dict of simulations

        Returns
        -------
        ref_simu_index : int
            index of the reference simulation (None if must be computed)
        """
        ref_simu_index = None
        for ii, simu in enumerate(simu_dict["simulation_list"]):
            diff_list = simu.compare(ref_simu, name="simu")
            # Remove not meaningfull differences
            if "simu.mag.file_name" in diff_list:
                diff_list.remove("simu.mag.file_name")
            if len(diff_list) == 0:
                ref_simu_index = ii
                break

        return ref_simu_index

    # cf Methods.Simulation.VarSimu.run
    def run(self):
        """Run the multi-simulation
        The VarSimu object must be in a Simulation object (and not a VarSimu one)

        Parameters
        ----------
        self : VarSimu
            A VarSimu object
        """

        logger = self.get_logger()
        Output = import_class("pyleecan.Classes", "Output")

        # Check var_simu parameters
        self.check_param()  # Check isinstance(self.parent, Simulation)

        # Get xoutput to store results (created in Simulation.run)
        xoutput = self.parent.parent

        # Create reference simulation
        ref_simu = self.parent.copy()
        ref_simu.var_simu = self.var_simu  # var_simu default is None
        ref_simu.index = None
        ref_simu.layer = self.parent.layer + 1
        # None clean-up
        if xoutput.xoutput_dict is None:
            xoutput.xoutput_dict = dict()

        # Generate simulation list and ParamExplorerValue list
        simu_dict = self.generate_simulation_list(ref_simu)
        # Generate default datakeeper
        self.gen_datakeeper_list(ref_simu)

        # Check if one of the simulation from the list matches the reference one
        ref_simu_index = self.get_ref_simu_index(ref_simu, simu_dict)

        # Fill/initialize input/output parameters
        nb_simu = len(simu_dict["simulation_list"])
        xoutput.nb_simu = nb_simu
        self.nb_simu = nb_simu
        xoutput.paramexplorer_list = simu_dict["paramexplorer_list"]
        simulation_list = simu_dict["simulation_list"]
        if self.is_keep_all_output:
            xoutput.output_list = [None] * self.nb_simu
        keeper_list = list()  # Copy keeper to store results in xoutput and not in simu
        for datakeeper in self.datakeeper_list:
            keeper_list.append(datakeeper.copy())
            xoutput.xoutput_dict[datakeeper.symbol] = keeper_list[-1]
            keeper_list[-1].result = [None] * self.nb_simu

        # Run Reference simulation
        if ref_simu.layer == 2:
            logger.info("    Computing reference simulation for " + self.NAME)
        else:
            logger.info("Computing reference simulation for " + self.NAME)

        if self.NAME == "Parameter Sweep":
            for param in simu_dict["paramexplorer_list"]:
                logger.info(param.get_desc(ref_simu))

        progress = 0  # For progress bar
        nb_simu += 1  # Count reference simulation in progress bar

        # Run the simulation & call DataKeeper and post-proc handling errors
        xoutput_ref = run_multisim_step(
            ref_simu,
            datakeeper_list=keeper_list,  # datakeeper.result will be updated (if needed)
            stop_if_error=True,  # Reference simulation must be correct
            post_keeper_postproc_list=self.post_keeper_postproc_list,
            simu_type=self.NAME,
        )
        # Save reference xoutput (if requested)
        if self.is_keep_all_output:
            if ref_simu_index is None:
                xoutput.xoutput_ref = xoutput_ref
            else:  # Avoid duplicating the XOutput
                xoutput.xoutput_ref_index = ref_simu_index

        progress += 1
        self.print_progress_bar(nb_simu, progress, ref_simu.layer)

        # Store the Ouput part of the xoutput_ref into the main xoutput
        ref_out_dict = Output.as_dict(xoutput_ref)
        if "simu" in ref_out_dict:  # Avoid erasing original simulation
            ref_out_dict.pop("simu")
        ref_out_dict.pop("__class__")
        for key, value in ref_out_dict.items():
            setattr(xoutput, key, value)

        # Reuse some intermediate results from reference simulation (if requested)
        for ii, simu in enumerate(simulation_list):
            # Log only for first simulation
            self.set_reused_data(
                simu,
                xoutput_ref,
                is_log=ii == 0,
                simu_type=self.NAME,
            )

        # Update the postprocessing list if needed
        if self.pre_keeper_postproc_list is not None:
            # Different post between simu list and ref simu
            for simu in simulation_list:
                simu.postproc_list = self.pre_keeper_postproc_list

        # Execute the simulation list
        for idx, simu_step in enumerate(simulation_list):
            # Display simulation progress
            self.log_step_simu(
                idx, self.nb_simu, xoutput.paramexplorer_list, logger, simu_step.layer
            )
            simu_step.index = idx
            if idx != ref_simu_index:
                # Run the simulation & call DataKeeper and post-proc handling errors
                xoutput_step = run_multisim_step(
                    simu_step,
                    keeper_list,  # datakeeper.result will be updated (if needed)
                    self.stop_if_error,
                    post_keeper_postproc_list=self.post_keeper_postproc_list,
                    simu_type=self.NAME,
                )
                if self.is_keep_all_output:
                    xoutput.output_list[idx] = xoutput_step
            else:
                if simu_step.layer == 2:
                    logger.info(
                        "    Simulation matches reference one: Skipping computation"
                    )
                else:
                    logger.info(
                        "Simulation matches reference one: Skipping computation"
                    )
                # Copy results from reference
                for keeper in keeper_list:
                    keeper.result[idx] = keeper.result_ref
                if self.is_keep_all_output:
                    xoutput.output_list[idx] = xoutput_ref
                # Print DataKeeper content
                log_datakeeper_step_result(simu_step, keeper_list, idx, self.NAME)
            progress += 1
            self.print_progress_bar(nb_simu, progress, simu_step.layer)

        # Running postprocessings
        if self.postproc_list:
            logger.info("Running " + self.NAME + " postprocessings...")
            for postproc in self.postproc_list:
                postproc.run(xoutput)

    @staticmethod
    def log_step_simu(index, nb_simu, paramexplorer_list, logger, layer):
        """Add in the log some information about the simulation about to run
        Ex: "Running simulation 3/4 with Id=-135.41881, Iq=113.62987"

        Parameters
        ----------
        index : int
            Index of the simulation about to run
        nb_simu : int
            Total number of simulation to run
        paramexplorer_list : list
            List of ParamExplorer to get the modification of the simu
        logger : Logger
            Logger to use (info)
        """

        if layer == 2:
            msg = "    "
        else:
            msg = ""
        InputCurrent = import_class("pyleecan.Classes", "InputCurrent")
        InputVoltage = import_class("pyleecan.Classes", "InputVoltage")
        msg += "Running simulation " + str(index + 1) + "/" + str(nb_simu) + " with "
        for param_exp in paramexplorer_list:
            value = param_exp.get_value()[index]
            if isinstance(value, InputCurrent):
                msg += "N0=" + format(value.OP.N0, ".6g") + " [rpm]"
                msg += ", Id=" + format(value.OP.Id_ref, ".4g") + " [Arms]"
                msg += ", Iq=" + format(value.OP.Iq_ref, ".4g") + " [Arms], "
            elif isinstance(value, InputVoltage):
                msg += "N0=" + format(value.OP.N0, ".6g") + " [rpm]"
                msg += ", U0=" + format(value.OP.U0_ref, ".4g") + " [Vrms]"
                msg += ", UPhi0=" + format(value.OP.UPhi0_ref, ".4g") + " [rad], "
                if value.OP.slip_ref is not None:
                    msg += ", slip=" + format(value.OP.slip_ref, ".4g") + " [-], "
            elif isinstance(value, (list, np.ndarray)):
                msg += param_exp.symbol
                msg += "="
                msg += format(value)
                msg += ", "
            else:
                try:
                    data_str = format(value, ".8g")
                except:
                    data_str = "'NA'"
                msg += param_exp.symbol
                msg += "="
                msg += data_str
                msg += ", "
        msg = msg[:-2]
        logger.info(msg)

    @staticmethod
    def print_progress_bar(Nsimu, index, layer):
        """Print the progress bar
        Ex: "[=========================                         ]  50%"

        Parameters
        ----------
        Nsimu : int
            Total number of simulation
        index : int
            Index of the simulation about to run
        """
        if layer == 2:
            msg = "               "
        else:
            msg = ""
        print(
            "\r"
            + msg
            + "["
            + "=" * (50 * index // (Nsimu))
            + " " * (50 - ((50 * index) // (Nsimu)))
            + "] {:3d}%".format(((100 * index) // (Nsimu)))
        )

    # cf Methods.Simulation.VarSimu.set_reused_data
    def set_reused_data(self, simu, output, is_log=True, simu_type="VarSimu"):
        """Resuse some data from the reference simulation to skip computation

        Parameters
        ----------
        self : VarSimu
            a VarSimu object
        simu : Simulation
            The simulation to update
        output : Output
            Output from the reference simulation to enforce
        is_log : bool
            True to log the changes
        simu_type : str
            Name of the multi-simulation kind
        """

        if simu.layer == 2:
            TAB = "    "
        else:
            TAB = ""

        if self.is_reuse_femm_file and isinstance(simu.mag, MagFEMM):
            if is_log:
                self.get_logger().info(
                    TAB
                    + simu_type
                    + ": Using same FEMM file for all simulations ("
                    + output.mag.internal.FEMM_dict["path_save"]
                    + ")"
                )
            simu.mag.import_file = output.mag.internal.FEMM_dict["path_save"]
            simu.mag.FEMM_dict_enforced = output.mag.internal.FEMM_dict

        if self.is_reuse_LUT and isinstance(simu.elec, ElecLUTdq):
            if is_log:
                self.get_logger().info(
                    TAB + simu_type + ": Using same LUT for all simulations"
                )
            simu.elec.LUT_enforced = output.simu.elec.LUT_enforced

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        name="",
        desc="",
        datakeeper_list=-1,
        is_keep_all_output=False,
        stop_if_error=False,
        var_simu=None,
        nb_simu=0,
        is_reuse_femm_file=True,
        postproc_list=-1,
        pre_keeper_postproc_list=None,
        post_keeper_postproc_list=None,
        is_reuse_LUT=True,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "desc" in list(init_dict.keys()):
                desc = init_dict["desc"]
            if "datakeeper_list" in list(init_dict.keys()):
                datakeeper_list = init_dict["datakeeper_list"]
            if "is_keep_all_output" in list(init_dict.keys()):
                is_keep_all_output = init_dict["is_keep_all_output"]
            if "stop_if_error" in list(init_dict.keys()):
                stop_if_error = init_dict["stop_if_error"]
            if "var_simu" in list(init_dict.keys()):
                var_simu = init_dict["var_simu"]
            if "nb_simu" in list(init_dict.keys()):
                nb_simu = init_dict["nb_simu"]
            if "is_reuse_femm_file" in list(init_dict.keys()):
                is_reuse_femm_file = init_dict["is_reuse_femm_file"]
            if "postproc_list" in list(init_dict.keys()):
                postproc_list = init_dict["postproc_list"]
            if "pre_keeper_postproc_list" in list(init_dict.keys()):
                pre_keeper_postproc_list = init_dict["pre_keeper_postproc_list"]
            if "post_keeper_postproc_list" in list(init_dict.keys()):
                post_keeper_postproc_list = init_dict["post_keeper_postproc_list"]
            if "is_reuse_LUT" in list(init_dict.keys()):
                is_reuse_LUT = init_dict["is_reuse_LUT"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.name = name
        self.desc = desc
        self.datakeeper_list = datakeeper_list
        self.is_keep_all_output = is_keep_all_output
        self.stop_if_error = stop_if_error
        self.var_simu = var_simu
        self.nb_simu = nb_simu
        self.is_reuse_femm_file = is_reuse_femm_file
        self.postproc_list = postproc_list
        self.pre_keeper_postproc_list = pre_keeper_postproc_list
        self.post_keeper_postproc_list = post_keeper_postproc_list
        self.is_reuse_LUT = is_reuse_LUT

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        VarSimu_str = ""
        if self.parent is None:
            VarSimu_str += "parent = None " + linesep
        else:
            VarSimu_str += "parent = " + str(type(self.parent)) + " object" + linesep
        VarSimu_str += 'name = "' + str(self.name) + '"' + linesep
        VarSimu_str += 'desc = "' + str(self.desc) + '"' + linesep
        if len(self.datakeeper_list) == 0:
            VarSimu_str += "datakeeper_list = []" + linesep
        for ii in range(len(self.datakeeper_list)):
            tmp = (
                self.datakeeper_list[ii].__str__().replace(linesep, linesep + "\t")
                + linesep
            )
            VarSimu_str += (
                "datakeeper_list[" + str(ii) + "] =" + tmp + linesep + linesep
            )
        VarSimu_str += "is_keep_all_output = " + str(self.is_keep_all_output) + linesep
        VarSimu_str += "stop_if_error = " + str(self.stop_if_error) + linesep
        if self.var_simu is not None:
            tmp = self.var_simu.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            VarSimu_str += "var_simu = " + tmp
        else:
            VarSimu_str += "var_simu = None" + linesep + linesep
        VarSimu_str += "nb_simu = " + str(self.nb_simu) + linesep
        VarSimu_str += "is_reuse_femm_file = " + str(self.is_reuse_femm_file) + linesep
        if len(self.postproc_list) == 0:
            VarSimu_str += "postproc_list = []" + linesep
        for ii in range(len(self.postproc_list)):
            tmp = (
                self.postproc_list[ii].__str__().replace(linesep, linesep + "\t")
                + linesep
            )
            VarSimu_str += "postproc_list[" + str(ii) + "] =" + tmp + linesep + linesep
        if len(self.pre_keeper_postproc_list) == 0:
            VarSimu_str += "pre_keeper_postproc_list = []" + linesep
        for ii in range(len(self.pre_keeper_postproc_list)):
            tmp = (
                self.pre_keeper_postproc_list[ii]
                .__str__()
                .replace(linesep, linesep + "\t")
                + linesep
            )
            VarSimu_str += (
                "pre_keeper_postproc_list[" + str(ii) + "] =" + tmp + linesep + linesep
            )
        if len(self.post_keeper_postproc_list) == 0:
            VarSimu_str += "post_keeper_postproc_list = []" + linesep
        for ii in range(len(self.post_keeper_postproc_list)):
            tmp = (
                self.post_keeper_postproc_list[ii]
                .__str__()
                .replace(linesep, linesep + "\t")
                + linesep
            )
            VarSimu_str += (
                "post_keeper_postproc_list[" + str(ii) + "] =" + tmp + linesep + linesep
            )
        VarSimu_str += "is_reuse_LUT = " + str(self.is_reuse_LUT) + linesep
        return VarSimu_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.name != self.name:
            return False
        if other.desc != self.desc:
            return False
        if other.datakeeper_list != self.datakeeper_list:
            return False
        if other.is_keep_all_output != self.is_keep_all_output:
            return False
        if other.stop_if_error != self.stop_if_error:
            return False
        if other.var_simu != self.var_simu:
            return False
        if other.nb_simu != self.nb_simu:
            return False
        if other.is_reuse_femm_file != self.is_reuse_femm_file:
            return False
        if other.postproc_list != self.postproc_list:
            return False
        if other.pre_keeper_postproc_list != self.pre_keeper_postproc_list:
            return False
        if other.post_keeper_postproc_list != self.post_keeper_postproc_list:
            return False
        if other.is_reuse_LUT != self.is_reuse_LUT:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._name != self._name:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._name) + ", other=" + str(other._name) + ")"
                )
                diff_list.append(name + ".name" + val_str)
            else:
                diff_list.append(name + ".name")
        if other._desc != self._desc:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._desc) + ", other=" + str(other._desc) + ")"
                )
                diff_list.append(name + ".desc" + val_str)
            else:
                diff_list.append(name + ".desc")
        if (other.datakeeper_list is None and self.datakeeper_list is not None) or (
            other.datakeeper_list is not None and self.datakeeper_list is None
        ):
            diff_list.append(name + ".datakeeper_list None mismatch")
        elif self.datakeeper_list is None:
            pass
        elif len(other.datakeeper_list) != len(self.datakeeper_list):
            diff_list.append("len(" + name + ".datakeeper_list)")
        else:
            for ii in range(len(other.datakeeper_list)):
                diff_list.extend(
                    self.datakeeper_list[ii].compare(
                        other.datakeeper_list[ii],
                        name=name + ".datakeeper_list[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if other._is_keep_all_output != self._is_keep_all_output:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_keep_all_output)
                    + ", other="
                    + str(other._is_keep_all_output)
                    + ")"
                )
                diff_list.append(name + ".is_keep_all_output" + val_str)
            else:
                diff_list.append(name + ".is_keep_all_output")
        if other._stop_if_error != self._stop_if_error:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._stop_if_error)
                    + ", other="
                    + str(other._stop_if_error)
                    + ")"
                )
                diff_list.append(name + ".stop_if_error" + val_str)
            else:
                diff_list.append(name + ".stop_if_error")
        if (other.var_simu is None and self.var_simu is not None) or (
            other.var_simu is not None and self.var_simu is None
        ):
            diff_list.append(name + ".var_simu None mismatch")
        elif self.var_simu is not None:
            diff_list.extend(
                self.var_simu.compare(
                    other.var_simu,
                    name=name + ".var_simu",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._nb_simu != self._nb_simu:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._nb_simu)
                    + ", other="
                    + str(other._nb_simu)
                    + ")"
                )
                diff_list.append(name + ".nb_simu" + val_str)
            else:
                diff_list.append(name + ".nb_simu")
        if other._is_reuse_femm_file != self._is_reuse_femm_file:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_reuse_femm_file)
                    + ", other="
                    + str(other._is_reuse_femm_file)
                    + ")"
                )
                diff_list.append(name + ".is_reuse_femm_file" + val_str)
            else:
                diff_list.append(name + ".is_reuse_femm_file")
        if (other.postproc_list is None and self.postproc_list is not None) or (
            other.postproc_list is not None and self.postproc_list is None
        ):
            diff_list.append(name + ".postproc_list None mismatch")
        elif self.postproc_list is None:
            pass
        elif len(other.postproc_list) != len(self.postproc_list):
            diff_list.append("len(" + name + ".postproc_list)")
        else:
            for ii in range(len(other.postproc_list)):
                diff_list.extend(
                    self.postproc_list[ii].compare(
                        other.postproc_list[ii],
                        name=name + ".postproc_list[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if (
            other.pre_keeper_postproc_list is None
            and self.pre_keeper_postproc_list is not None
        ) or (
            other.pre_keeper_postproc_list is not None
            and self.pre_keeper_postproc_list is None
        ):
            diff_list.append(name + ".pre_keeper_postproc_list None mismatch")
        elif self.pre_keeper_postproc_list is None:
            pass
        elif len(other.pre_keeper_postproc_list) != len(self.pre_keeper_postproc_list):
            diff_list.append("len(" + name + ".pre_keeper_postproc_list)")
        else:
            for ii in range(len(other.pre_keeper_postproc_list)):
                diff_list.extend(
                    self.pre_keeper_postproc_list[ii].compare(
                        other.pre_keeper_postproc_list[ii],
                        name=name + ".pre_keeper_postproc_list[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if (
            other.post_keeper_postproc_list is None
            and self.post_keeper_postproc_list is not None
        ) or (
            other.post_keeper_postproc_list is not None
            and self.post_keeper_postproc_list is None
        ):
            diff_list.append(name + ".post_keeper_postproc_list None mismatch")
        elif self.post_keeper_postproc_list is None:
            pass
        elif len(other.post_keeper_postproc_list) != len(
            self.post_keeper_postproc_list
        ):
            diff_list.append("len(" + name + ".post_keeper_postproc_list)")
        else:
            for ii in range(len(other.post_keeper_postproc_list)):
                diff_list.extend(
                    self.post_keeper_postproc_list[ii].compare(
                        other.post_keeper_postproc_list[ii],
                        name=name + ".post_keeper_postproc_list[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if other._is_reuse_LUT != self._is_reuse_LUT:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_reuse_LUT)
                    + ", other="
                    + str(other._is_reuse_LUT)
                    + ")"
                )
                diff_list.append(name + ".is_reuse_LUT" + val_str)
            else:
                diff_list.append(name + ".is_reuse_LUT")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.name)
        S += getsizeof(self.desc)
        if self.datakeeper_list is not None:
            for value in self.datakeeper_list:
                S += getsizeof(value)
        S += getsizeof(self.is_keep_all_output)
        S += getsizeof(self.stop_if_error)
        S += getsizeof(self.var_simu)
        S += getsizeof(self.nb_simu)
        S += getsizeof(self.is_reuse_femm_file)
        if self.postproc_list is not None:
            for value in self.postproc_list:
                S += getsizeof(value)
        if self.pre_keeper_postproc_list is not None:
            for value in self.pre_keeper_postproc_list:
                S += getsizeof(value)
        if self.post_keeper_postproc_list is not None:
            for value in self.post_keeper_postproc_list:
                S += getsizeof(value)
        S += getsizeof(self.is_reuse_LUT)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        VarSimu_dict = dict()
        VarSimu_dict["name"] = self.name
        VarSimu_dict["desc"] = self.desc
        if self.datakeeper_list is None:
            VarSimu_dict["datakeeper_list"] = None
        else:
            VarSimu_dict["datakeeper_list"] = list()
            for obj in self.datakeeper_list:
                if obj is not None:
                    VarSimu_dict["datakeeper_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    VarSimu_dict["datakeeper_list"].append(None)
        VarSimu_dict["is_keep_all_output"] = self.is_keep_all_output
        VarSimu_dict["stop_if_error"] = self.stop_if_error
        if self.var_simu is None:
            VarSimu_dict["var_simu"] = None
        else:
            VarSimu_dict["var_simu"] = self.var_simu.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        VarSimu_dict["nb_simu"] = self.nb_simu
        VarSimu_dict["is_reuse_femm_file"] = self.is_reuse_femm_file
        if self.postproc_list is None:
            VarSimu_dict["postproc_list"] = None
        else:
            VarSimu_dict["postproc_list"] = list()
            for obj in self.postproc_list:
                if obj is not None:
                    VarSimu_dict["postproc_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    VarSimu_dict["postproc_list"].append(None)
        if self.pre_keeper_postproc_list is None:
            VarSimu_dict["pre_keeper_postproc_list"] = None
        else:
            VarSimu_dict["pre_keeper_postproc_list"] = list()
            for obj in self.pre_keeper_postproc_list:
                if obj is not None:
                    VarSimu_dict["pre_keeper_postproc_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    VarSimu_dict["pre_keeper_postproc_list"].append(None)
        if self.post_keeper_postproc_list is None:
            VarSimu_dict["post_keeper_postproc_list"] = None
        else:
            VarSimu_dict["post_keeper_postproc_list"] = list()
            for obj in self.post_keeper_postproc_list:
                if obj is not None:
                    VarSimu_dict["post_keeper_postproc_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    VarSimu_dict["post_keeper_postproc_list"].append(None)
        VarSimu_dict["is_reuse_LUT"] = self.is_reuse_LUT
        # The class name is added to the dict for deserialisation purpose
        VarSimu_dict["__class__"] = "VarSimu"
        return VarSimu_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        name_val = self.name
        desc_val = self.desc
        if self.datakeeper_list is None:
            datakeeper_list_val = None
        else:
            datakeeper_list_val = list()
            for obj in self.datakeeper_list:
                datakeeper_list_val.append(obj.copy())
        is_keep_all_output_val = self.is_keep_all_output
        stop_if_error_val = self.stop_if_error
        if self.var_simu is None:
            var_simu_val = None
        else:
            var_simu_val = self.var_simu.copy()
        nb_simu_val = self.nb_simu
        is_reuse_femm_file_val = self.is_reuse_femm_file
        if self.postproc_list is None:
            postproc_list_val = None
        else:
            postproc_list_val = list()
            for obj in self.postproc_list:
                postproc_list_val.append(obj.copy())
        if self.pre_keeper_postproc_list is None:
            pre_keeper_postproc_list_val = None
        else:
            pre_keeper_postproc_list_val = list()
            for obj in self.pre_keeper_postproc_list:
                pre_keeper_postproc_list_val.append(obj.copy())
        if self.post_keeper_postproc_list is None:
            post_keeper_postproc_list_val = None
        else:
            post_keeper_postproc_list_val = list()
            for obj in self.post_keeper_postproc_list:
                post_keeper_postproc_list_val.append(obj.copy())
        is_reuse_LUT_val = self.is_reuse_LUT
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            name=name_val,
            desc=desc_val,
            datakeeper_list=datakeeper_list_val,
            is_keep_all_output=is_keep_all_output_val,
            stop_if_error=stop_if_error_val,
            var_simu=var_simu_val,
            nb_simu=nb_simu_val,
            is_reuse_femm_file=is_reuse_femm_file_val,
            postproc_list=postproc_list_val,
            pre_keeper_postproc_list=pre_keeper_postproc_list_val,
            post_keeper_postproc_list=post_keeper_postproc_list_val,
            is_reuse_LUT=is_reuse_LUT_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.name = None
        self.desc = None
        self.datakeeper_list = None
        self.is_keep_all_output = None
        self.stop_if_error = None
        if self.var_simu is not None:
            self.var_simu._set_None()
        self.nb_simu = None
        self.is_reuse_femm_file = None
        self.postproc_list = None
        self.pre_keeper_postproc_list = None
        self.post_keeper_postproc_list = None
        self.is_reuse_LUT = None

    def _get_name(self):
        """getter of name"""
        return self._name

    def _set_name(self, value):
        """setter of name"""
        check_var("name", value, "str")
        self._name = value

    name = property(
        fget=_get_name,
        fset=_set_name,
        doc="""Name of the multi-simulation

        :Type: str
        """,
    )

    def _get_desc(self):
        """getter of desc"""
        return self._desc

    def _set_desc(self, value):
        """setter of desc"""
        check_var("desc", value, "str")
        self._desc = value

    desc = property(
        fget=_get_desc,
        fset=_set_desc,
        doc="""Multi-simulation description

        :Type: str
        """,
    )

    def _get_datakeeper_list(self):
        """getter of datakeeper_list"""
        if self._datakeeper_list is not None:
            for obj in self._datakeeper_list:
                if obj is not None:
                    obj.parent = self
        return self._datakeeper_list

    def _set_datakeeper_list(self, value):
        """setter of datakeeper_list"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "datakeeper_list"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("datakeeper_list", value, "[DataKeeper]")
        self._datakeeper_list = value

    datakeeper_list = property(
        fget=_get_datakeeper_list,
        fset=_set_datakeeper_list,
        doc="""List containing DataKeepers to extract VarSimu results 

        :Type: [DataKeeper]
        """,
    )

    def _get_is_keep_all_output(self):
        """getter of is_keep_all_output"""
        return self._is_keep_all_output

    def _set_is_keep_all_output(self, value):
        """setter of is_keep_all_output"""
        check_var("is_keep_all_output", value, "bool")
        self._is_keep_all_output = value

    is_keep_all_output = property(
        fget=_get_is_keep_all_output,
        fset=_set_is_keep_all_output,
        doc="""True to store every output in a list

        :Type: bool
        """,
    )

    def _get_stop_if_error(self):
        """getter of stop_if_error"""
        return self._stop_if_error

    def _set_stop_if_error(self, value):
        """setter of stop_if_error"""
        check_var("stop_if_error", value, "bool")
        self._stop_if_error = value

    stop_if_error = property(
        fget=_get_stop_if_error,
        fset=_set_stop_if_error,
        doc="""Stop the multi-simulation if a simulation fails 

        :Type: bool
        """,
    )

    def _get_var_simu(self):
        """getter of var_simu"""
        return self._var_simu

    def _set_var_simu(self, value):
        """setter of var_simu"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "var_simu"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            VarSimu = import_class("pyleecan.Classes", "VarSimu", "var_simu")
            value = VarSimu()
        check_var("var_simu", value, "VarSimu")
        self._var_simu = value

        if self._var_simu is not None:
            self._var_simu.parent = self

    var_simu = property(
        fget=_get_var_simu,
        fset=_set_var_simu,
        doc="""Multi-simulation of a Multi-simulation definition

        :Type: VarSimu
        """,
    )

    def _get_nb_simu(self):
        """getter of nb_simu"""
        return self._nb_simu

    def _set_nb_simu(self, value):
        """setter of nb_simu"""
        check_var("nb_simu", value, "int")
        self._nb_simu = value

    nb_simu = property(
        fget=_get_nb_simu,
        fset=_set_nb_simu,
        doc="""Number of simulations

        :Type: int
        """,
    )

    def _get_is_reuse_femm_file(self):
        """getter of is_reuse_femm_file"""
        return self._is_reuse_femm_file

    def _set_is_reuse_femm_file(self, value):
        """setter of is_reuse_femm_file"""
        check_var("is_reuse_femm_file", value, "bool")
        self._is_reuse_femm_file = value

    is_reuse_femm_file = property(
        fget=_get_is_reuse_femm_file,
        fset=_set_is_reuse_femm_file,
        doc="""True to reuse the femm file for each simulation (draw the machine only once, MagFEMM only)

        :Type: bool
        """,
    )

    def _get_postproc_list(self):
        """getter of postproc_list"""
        if self._postproc_list is not None:
            for obj in self._postproc_list:
                if obj is not None:
                    obj.parent = self
        return self._postproc_list

    def _set_postproc_list(self, value):
        """setter of postproc_list"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "postproc_list"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("postproc_list", value, "[Post]")
        self._postproc_list = value

    postproc_list = property(
        fget=_get_postproc_list,
        fset=_set_postproc_list,
        doc="""List of post-processing to run on XOutput after the multisimulation

        :Type: [Post]
        """,
    )

    def _get_pre_keeper_postproc_list(self):
        """getter of pre_keeper_postproc_list"""
        if self._pre_keeper_postproc_list is not None:
            for obj in self._pre_keeper_postproc_list:
                if obj is not None:
                    obj.parent = self
        return self._pre_keeper_postproc_list

    def _set_pre_keeper_postproc_list(self, value):
        """setter of pre_keeper_postproc_list"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes",
                        obj.get("__class__"),
                        "pre_keeper_postproc_list",
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("pre_keeper_postproc_list", value, "[Post]")
        self._pre_keeper_postproc_list = value

    pre_keeper_postproc_list = property(
        fget=_get_pre_keeper_postproc_list,
        fset=_set_pre_keeper_postproc_list,
        doc="""If not None, replace the reference simulation postproc_list in each generated simulation (run before datakeeper)

        :Type: [Post]
        """,
    )

    def _get_post_keeper_postproc_list(self):
        """getter of post_keeper_postproc_list"""
        if self._post_keeper_postproc_list is not None:
            for obj in self._post_keeper_postproc_list:
                if obj is not None:
                    obj.parent = self
        return self._post_keeper_postproc_list

    def _set_post_keeper_postproc_list(self, value):
        """setter of post_keeper_postproc_list"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes",
                        obj.get("__class__"),
                        "post_keeper_postproc_list",
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("post_keeper_postproc_list", value, "[Post]")
        self._post_keeper_postproc_list = value

    post_keeper_postproc_list = property(
        fget=_get_post_keeper_postproc_list,
        fset=_set_post_keeper_postproc_list,
        doc="""List of post-processing to run on output after each simulation (except reference one) after the datakeeper.

        :Type: [Post]
        """,
    )

    def _get_is_reuse_LUT(self):
        """getter of is_reuse_LUT"""
        return self._is_reuse_LUT

    def _set_is_reuse_LUT(self, value):
        """setter of is_reuse_LUT"""
        check_var("is_reuse_LUT", value, "bool")
        self._is_reuse_LUT = value

    is_reuse_LUT = property(
        fget=_get_is_reuse_LUT,
        fset=_set_is_reuse_LUT,
        doc="""True to reuse the look up table

        :Type: bool
        """,
    )

    class VarSimuError(Exception):
        pass


VarSimuError = VarSimu.VarSimuError
