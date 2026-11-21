from ....classes_common.logger_context import get_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def run(self) -> Output:
    """Run the simulation and optionnaly its multisimulation

    Returns
    -------
    output: Output
        Contains simulation results
    """
    from ....classes_common.logger_context import logger_context

    # The objects without logger_name use the logger of the simulation
    with logger_context(self):
        # In-function import to avoid ImportError
        from ....Classes_new.output.xoutput import XOutput
        from ....Classes_new.output.output import Output

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
