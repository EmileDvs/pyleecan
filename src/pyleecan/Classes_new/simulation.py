# Experimental dataclass generated from Generator/ClassesRef/Simulation/Simulation.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from dataclasses import dataclass
from logging.config import dictConfig

from ..loggers import DEFAULT_LOG_NAME, gen_logger_config_dict
from ._pyleecan_class import PyleecanClass
from .electrical import Electrical
from .input import Input
from .machine import Machine
from .opti_problem import OptiProblem
from .output import Output
from .post import Post
from .var_load import VarLoad
from .var_simu import VarSimu


@dataclass(eq=False)
class Simulation(PyleecanClass):
    """Abstract class for the simulation

    Attributes
    ----------
    name : str or None
        Name of the simulation
        Default: None
    desc : str or None
        Simulation description
        Default: None
    machine : Machine or None
        Machine to simulate
        Default: None
    input : Input or None
        Input of the simulation
        Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Simulation"
    var_simu : VarSimu or None
        Multi-simulation definition
        Default: None
    postproc_list : [Post]
        List of postprocessings to run on Output after the simulation
        Default: []
    index : int or None
        Index of the simulation (if part of a multi-simulation)
        Default: None; Minimum: 0
    path_result : str or None
        Path to the Result folder to use (None to use default one)
        Default: None
    layer : int or None
        Layer of the simulation in a multi-simulation (0 is top simulation)
        Default: None; Minimum: 0
    layer_log_warn : int or None
        Enable to set the log console_handler to warning starting from a particular layer. layer_log_warn=2 => layer 0 and 1 info, layer 2 warning
        Default: None; Minimum: 0
    """

    name: str | None = None
    """Name of the simulation"""
    desc: str | None = None
    """Simulation description"""
    machine: Machine | None = None
    """Machine to simulate"""
    input: Input | None = None
    """Input of the simulation"""
    logger_name: str = "Pyleecan.Simulation"
    """Name of the logger to use"""
    var_simu: VarSimu | None = None
    """Multi-simulation definition"""
    postproc_list: list[Post] = []
    """List of postprocessings to run on Output after the simulation"""
    index: int | None = None
    """Index of the simulation (if part of a multi-simulation)"""
    path_result: str | None = None
    """Path to the Result folder to use (None to use default one)"""
    layer: int | None = None
    """Layer of the simulation in a multi-simulation (0 is top simulation)"""
    layer_log_warn: int | None = None
    """Enable to set the log console_handler to warning starting from a particular layer. layer_log_warn=2 => layer 0 and 1 info, layer 2 warning"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                Electrical,
                OptiProblem,
                Output,
            ),
        ):
            raise TypeError(
                "Simulation parent must be an instance of Electrical or OptiProblem or Output, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Simulation.Simulation.get_OP_array
    def get_OP_array(self, *arg_list):
        """Return the OP matrix of the simulation
        Single speed simulation return a single line matrix

        Parameters
        ----------
        self : Simulation
            A Simulation object
        *arg_list : list of str
            arguments to select the OP_matrix columns name (N0, Id, Id, Tem...)

        Returns
        -------
        OP_matrix : ndarray
            Operating Points matrix (N_OP, len(arg_list))
        """

        var_load = self.get_var_load()
        if var_load is None:  # Single speed
            return self.input.OP.get_OP_array(arg_list)
        else:
            return var_load.get_OP_array(arg_list)

    # Inlined from Methods.Simulation.Simulation.get_var_load
    def get_var_load(self):
        """Return the VarLoad object from var_simu or var_simu.var_simu

        Parameters
        ----------
        self : Simulation
            A Simulation object
        """

        if self.var_simu is None:
            return None
        if isinstance(self.var_simu, VarLoad):
            return self.var_simu
        if isinstance(self.var_simu.var_simu, VarLoad):
            return self.var_simu.var_simu
        return None

    # Inlined from Methods.Simulation.Simulation.init_logger
    def init_logger(self, output):
        """Create all the logger for the simulation

        Parameters
        ----------
        self : Simulation
            A Simulation object
        output : XOuput
            XOutput or Output object
        """

        if self.name in [None, ""]:
            log_name = DEFAULT_LOG_NAME
        else:
            log_name = self.name

        if self.layer == 0:  # Create logger only once for top simulation
            log_dict = gen_logger_config_dict(log_name)

            # Update log file
            log_path = os.path.join(output.get_path_result(), log_name + ".log")
            log_dict["handlers"]["file_handler"]["filename"] = log_path
            # Create the loggers
            dictConfig(log_dict)

        # Set the logger in the simulation
        self.logger_name = log_name
        self.machine.logger_name = log_name + ".Machine"
        if self.elec is not None:
            self.elec.logger_name = log_name + ".Electrical"
        if self.mag is not None:
            self.mag.logger_name = log_name + ".Magnetics"
        if self.force is not None:
            self.force.logger_name = log_name + ".Force"
        if self.struct is not None:
            self.struct.logger_name = log_name + ".Structural"
        # Set the logger in the Output
        output.logger_name = log_name
        output.elec.logger_name = log_name + ".Electrical"
        output.mag.logger_name = log_name + ".Magnetics"
        output.force.logger_name = log_name + ".Force"
        output.struct.logger_name = log_name + ".Structural"

        if self.layer == 0:
            # Display start of top simulation
            msg = "Starting running simulation"
            if self.name not in ["", None]:
                msg += " " + self.name
            if self.machine.name not in ["", None]:
                msg += " (machine=" + self.machine.name + ")"
            self.get_logger().debug("###################################")
            self.get_logger().info(msg)

    # Inlined from Methods.Simulation.Simulation.run
    def run(self):
        """Run the simulation and optionnaly its multisimulation

        Returns
        -------
        output: Output
            Contains simulation results
        """
        # In-function import to avoid ImportError
        from .xoutput import XOutput
        from .output import Output

        if self.layer is None:
            self.layer = 0  # Top simulation

        # Multi-simulation
        if self.var_simu is not None:
            # make sure simulation output is of class XOutput
            if self.parent is None:
                results = XOutput(simu=self)
            else:
                if not isinstance(self.parent, XOutput):
                    msg = (
                        "Simulation.run: A multisimulation has been defined, "
                        + "type XOutput expected for simu.parent, "
                        + f"got {type(self.parent).__name__}. "
                        + "Setting new parent XOutput for simu."
                    )
                    self.get_logger().warning(msg)
                    results = XOutput(simu=self)
                else:
                    results = self.parent

            # Logger setup
            self.init_logger(results)

            # Compute the multisimulation
            self.var_simu.run()

        # 'normal' simulation
        else:
            # Output initialization
            if self.parent is None:
                results = Output(simu=self)
            else:
                results = self.parent

            # Logger setup
            self.init_logger(results)

            # Compute the simulation
            self.run_single()

        if self.index is None and self.layer == 0:
            msg = "End of simulation"
            if self.name not in ["", None]:
                msg += " " + self.name
            self.get_logger().info(msg)
        return results
