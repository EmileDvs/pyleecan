# Experimental pydantic model generated from Generator/ClassesRef/Simulation/VarSimu.csv
"""Generated experimental pydantic model; do not edit by hand."""

from __future__ import annotations

from logging import WARNING
from typing import TYPE_CHECKING, ClassVar

import numpy as np
from pydantic import Field

from ...classes_common.errors import VarSimuError
from ...Functions_pydantic.Simulation.VarSimu.get_elec_datakeeper_dict import (
    get_elec_datakeeper_dict,
)
from ...Functions_pydantic.Simulation.VarSimu.log_datakeeper_step_result import (
    log_datakeeper_step_result,
)
from ...loggers import CONSOLE_LEVEL
from .._legacy_model import LegacyModel
from ..magnetics.mag_femm import MagFEMM
from ..post.post import Post
from .data_keeper import DataKeeper

if TYPE_CHECKING:
    from logging import Logger

    from ..output.output import Output
    from .simulation import Simulation


class VarSimu(LegacyModel):
    """Abstract class for the multi-simulation

    Attributes
    ----------
    name : str
        Name of the multi-simulation
        Default: ""
    desc : str
        Multi-simulation description
        Default: ""
    datakeeper_list : [DataKeeper] or None
        List containing DataKeepers to extract VarSimu results
        Default: []
    is_keep_all_output : bool
        True to store every output in a list
        Default: False
    stop_if_error : bool
        Stop the multi-simulation if a simulation fails
        Default: False
    var_simu : VarSimu or None
        Multi-simulation of a Multi-simulation definition
        Default: None
    nb_simu : int
        Number of simulations
        Default: 0
    is_reuse_femm_file : bool
        True to reuse the femm file for each simulation (draw the machine only once, MagFEMM only)
        Default: True
    postproc_list : [Post] or None
        List of post-processing to run on XOutput after the multisimulation
        Default: []
    pre_keeper_postproc_list : [Post] or None
        If not None, replace the reference simulation postproc_list in each generated simulation (run before datakeeper)
        Default: None
    post_keeper_postproc_list : [Post] or None
        List of post-processing to run on output after each simulation (except reference one) after the datakeeper.
        Default: None
    is_reuse_LUT : bool
        True to reuse the look up table
        Default: True
    """

    name: str = ""
    """Name of the multi-simulation"""
    desc: str = ""
    """Multi-simulation description"""
    datakeeper_list: list[DataKeeper] | None = Field(default_factory=list)
    """List containing DataKeepers to extract VarSimu results """
    is_keep_all_output: bool = False
    """True to store every output in a list"""
    stop_if_error: bool = False
    """Stop the multi-simulation if a simulation fails """
    var_simu: VarSimu | None = None
    """Multi-simulation of a Multi-simulation definition"""
    nb_simu: int = 0
    """Number of simulations"""
    is_reuse_femm_file: bool = True
    """True to reuse the femm file for each simulation (draw the machine only once, MagFEMM only)"""
    postproc_list: list[Post] | None = Field(default_factory=list)
    """List of post-processing to run on XOutput after the multisimulation"""
    pre_keeper_postproc_list: list[Post] | None = None
    """If not None, replace the reference simulation postproc_list in each generated simulation (run before datakeeper)"""
    post_keeper_postproc_list: list[Post] | None = None
    """List of post-processing to run on output after each simulation (except reference one) after the datakeeper."""
    is_reuse_LUT: bool = True
    """True to reuse the look up table"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.VarSimu.check_param
    def check_param(self) -> None:
        """Check VarParamSweep parameters validity"""
        from .simulation import Simulation

        if type(self).__name__ == "VarSimu":
            raise VarSimuError(
                "VarSimu is an abstract class, please create one of its daughters."
            )

        # Check for simulation or VarSimu
        if self.parent is None or not isinstance(self.parent, Simulation):
            raise VarSimuError("VarSimu object must be inside a Simulation object")

    # Inlined from Methods.Simulation.VarSimu.gen_datakeeper_list
    def gen_datakeeper_list(self, ref_simu) -> None:
        """Generate default DataKeepers according the reference simulation type"""
        from .input_current import InputCurrent

        datakeeper_list = []

        # To avoid adding twice a DataKeeper
        symbol_list = [dk.symbol for dk in self.datakeeper_list]
        # For multi-simulation of multi-simulation (different DataKeepe<r)
        is_multi = ref_simu.var_simu is not None
        # Dynamic import to avoid loop

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
        if ref_simu.loss:
            datakeeper_list.extend(
                self.get_loss_datakeeper(symbol_list, is_multi=is_multi)
            )

        self.datakeeper_list.extend(datakeeper_list)

    # Inlined from Methods.Simulation.VarSimu.generate_simulation_list
    def generate_simulation_list(self, ref_simu: Simulation | None = None) -> dict:
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

    # Inlined from Methods.Simulation.VarSimu.get_elec_datakeeper
    def get_elec_datakeeper(self, symbol_list: list, is_multi: bool = False) -> list:
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

    # Inlined from Methods.Simulation.VarSimu.get_force_datakeeper
    def get_force_datakeeper(self, symbol_list: list, is_multi: bool = False) -> list:
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

    # Inlined from Methods.Simulation.VarSimu.get_loss_datakeeper
    def get_loss_datakeeper(self, symbol_list: list, is_multi: bool = False) -> list:
        """Generate DataKeepers to store by default results from loss module

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

        dict_loss = {
            "L_{tot}": "overall",
            "L_{sta}": "stator core",
            "L_{joule}": "stator joule",
            "L_{prox}": "stator proximity",
            "L_{rot}": "rotor core",
            "L_{mag}": "rotor magnets",
        }

        dk_list = [
            DataKeeper(
                name="Input power",
                unit="W",
                symbol="P_{in}",
                keeper="lambda output: output.loss.P_in",
                error_keeper="lambda simu: np.nan",
            ),
            DataKeeper(
                name="Output power",
                unit="W",
                symbol="P_{out}",
                keeper="lambda output: output.loss.P_out",
                error_keeper="lambda simu: np.nan",
            ),
            DataKeeper(
                name="Efficiency",
                unit="%",
                symbol="\\eta",
                keeper="lambda output: 100*output.loss.efficiency",
                error_keeper="lambda simu: np.nan",
            ),
        ]

        dk_list.extend(
            [
                DataKeeper(
                    name=group_name + " losses",
                    unit="W",
                    symbol=symb,
                    keeper="lambda output: output.loss.loss_dict['"
                    + str(group_name)
                    + "'].get_loss_scalar(output.elec.OP.felec)",
                    error_keeper="lambda simu: np.nan",
                )
                for symb, group_name in dict_loss.items()
            ]
        )

        dk_list.append(
            DataKeeper(
                name="Mechanical torque",
                unit="Nm",
                symbol="Tmech_{av}",
                keeper="lambda output: output.loss.Tmech_av",
                error_keeper="lambda simu: np.nan",
            )
        )

        return dk_list

    # Inlined from Methods.Simulation.VarSimu.get_mag_datakeeper
    def get_mag_datakeeper(self, symbol_list: list, is_multi: bool = False) -> list:
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

    # Inlined from Methods.Simulation.VarSimu.get_ref_simu_index
    def get_ref_simu_index(self, ref_simu: Simulation, simu_dict: dict) -> int:
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

    # Inlined from Methods.Simulation.VarSimu.run
    def run(self) -> None:
        """Run the multi-simulation
        The VarSimu object must be in a Simulation object (and not a VarSimu one)

        Parameters
        ----------
        self : VarSimu
            A VarSimu object
        """

        from ..output.output import Output

        logger = self.get_logger()

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
            xoutput.xoutput_dict = {}

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
        keeper_list = []  # Copy keeper to store results in xoutput and not in simu
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
        xoutput_ref = self.run_multisim_step(
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
                xoutput_step = self.run_multisim_step(
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
    def log_step_simu(
        index: int, nb_simu: int, paramexplorer_list: list, logger: Logger, layer
    ) -> None:
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

        from .input_current import InputCurrent
        from .input_voltage import InputVoltage

        if layer == 2:
            msg = "    "
        else:
            msg = ""
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
    def print_progress_bar(Nsimu: int, index: int, layer) -> None:
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

    # Inlined from Methods.Simulation.VarSimu.set_reused_data
    def set_reused_data(
        self,
        simu: Simulation,
        output: Output,
        is_log: bool = True,
        simu_type: str = "VarSimu",
    ) -> None:
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

        from ..electrical.elec_lut_dq import ElecLUTdq

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

    # Inlined from Methods.Simulation.VarSimu.run_multisim_step
    @staticmethod
    def run_multisim_step(
        simulation: Simulation,
        datakeeper_list,
        stop_if_error: bool,
        post_keeper_postproc_list: list | None = None,
        simu_type: str | None = None,
    ):
        """Execute a simulation step of a multi-simulation and run datakeepers

        Parameters
        ----------
        simulation: Simulation
            Simulation to run
        datakeeper_list
            List of datakeeper to run and update results
        stop_if_error: bool
            True: Raises an error if the simulation fails
        post_keeper_postproc_list : list
            list of postprocessing to run after the datakeeper
        simu_type : str
            To adapt the text ex: "Variable Load Results"
        """
        # Change console logger level from a specific layer (if requested)
        if (
            simulation.layer_log_warn is not None
            and simulation.layer >= simulation.layer_log_warn
        ):
            simulation.get_logger().handlers[0].level = WARNING

        # Run the simulation with/without error handling
        if stop_if_error:
            is_error = False
            result = simulation.run()
        else:
            try:
                result = simulation.run()
                is_error = False
            except Exception as err:
                print(err)
                is_error = True
                result = None

        # Revert logger level
        simulation.get_logger().handlers[0].level = CONSOLE_LEVEL

        # Datakeepers
        index = simulation.index
        if is_error:  # Execute error_keeper
            for datakeeper in datakeeper_list:
                if datakeeper.error_keeper is None:
                    value = None
                else:
                    value = datakeeper.error_keeper(simulation)
                if simulation.index is None:  # index == None => ref simu
                    datakeeper.result_ref = value
                else:
                    datakeeper.result[index] = value
        else:  # Execute Normal DataKeeper
            for datakeeper in datakeeper_list:
                # Run and store Datakeeper
                try:
                    value = datakeeper.keeper(result)
                except Exception as e:
                    simulation.get_logger().error(
                        "ERROR while calling DataKeeper "
                        + datakeeper.name
                        + " for simulation "
                        + str(index)
                        + ":\n"
                        + str(e)
                    )
                    if stop_if_error:
                        raise e
                    value = datakeeper.error_keeper(simulation)
                if simulation.index is None:  # index == None => ref simu
                    datakeeper.result_ref = value
                else:
                    datakeeper.result[index] = value
            log_datakeeper_step_result(simulation, datakeeper_list, index, simu_type)

            # Run Post datakeeper post-processings
            if post_keeper_postproc_list is not None:
                for postproc in post_keeper_postproc_list:
                    postproc.run(result)
        return result
