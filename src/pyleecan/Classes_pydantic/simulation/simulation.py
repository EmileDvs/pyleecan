# Experimental pydantic model generated from Generator/ClassesRef/Simulation/Simulation.csv
"""Generated experimental pydantic model; do not edit by hand."""

import os
from logging.config import dictConfig
from typing import TYPE_CHECKING, ClassVar

from pydantic import Field

from ...classes_common.logger_context import get_logger, logger_context
from ...loggers import DEFAULT_LOG_NAME, gen_logger_config_dict
from .._legacy_model import LegacyModel
from ..machine.machine import Machine
from ..post.post import Post
from .input import Input
from .var_load import VarLoad
from .var_simu import VarSimu

if TYPE_CHECKING:
    import numpy as np

    from ..output.output import Output
    from ..output.xoutput import XOutput


class Simulation(LegacyModel):
    """Abstract class for the simulation

    Attributes
    ----------
    name : str
        Name of the simulation
        Default: ""
    desc : str
        Simulation description
        Default: ""
    machine : Machine or None
        Machine to simulate
        Default: Machine()
    input : Input or None
        Input of the simulation
        Default: Input()
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

    name: str = ""
    """Name of the simulation"""
    desc: str = ""
    """Simulation description"""
    machine: Machine = Field(default_factory=lambda: Machine())
    """Machine to simulate"""
    input: Input = Field(default_factory=lambda: Input())
    """Input of the simulation"""
    logger_name: str = "Pyleecan.Simulation"
    """Name of the logger to use"""
    var_simu: VarSimu | None = None
    """Multi-simulation definition"""
    postproc_list: list[Post] = Field(default_factory=list)
    """List of postprocessings to run on Output after the simulation"""
    index: int | None = Field(default=None, ge=0)
    """Index of the simulation (if part of a multi-simulation)"""
    path_result: str | None = None
    """Path to the Result folder to use (None to use default one)"""
    layer: int | None = Field(default=None, ge=0)
    """Layer of the simulation in a multi-simulation (0 is top simulation)"""
    layer_log_warn: int | None = Field(default=None, ge=0)
    """Enable to set the log console_handler to warning starting from a particular layer. layer_log_warn=2 => layer 0 and 1 info, layer 2 warning"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.Simulation.get_OP_array
    def get_OP_array(self, *arg_list) -> np.ndarray:
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
    def init_logger(self, output: XOutput) -> None:
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
            get_logger(self).debug("###################################")
            get_logger(self).info(msg)

    # Inlined from Methods.Simulation.Simulation.run
    def run(self) -> Output:
        """Run the simulation and optionnaly its multisimulation

        Returns
        -------
        output: Output
            Contains simulation results
        """

        # The objects without logger_name use the logger of the simulation
        with logger_context(self):
            # In-function import to avoid ImportError
            from ..output.output import Output
            from ..output.xoutput import XOutput

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
                        get_logger(self).warning(msg)
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
                self.run_single(output=results)

            if self.index is None and self.layer == 0:
                msg = "End of simulation"
                if self.name not in ["", None]:
                    msg += " " + self.name
                get_logger(self).info(msg)
            return results
