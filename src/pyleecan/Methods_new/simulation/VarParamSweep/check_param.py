from typing import TYPE_CHECKING
from ....classes_common.logger_context import get_logger
from ....Classes_new.simulation.param_explorer_set import ParamExplorerSet


class ParamExplorerError(Exception):
    pass


class VarParamSweepError(Exception):
    pass


class DataKeeperError(Exception):
    pass


if TYPE_CHECKING:
    from ....Classes_new.simulation.simulation import Simulation


def check_param(self, simu: Simulation | None = None) -> None:
    """Check VarParamSweep parameters validity

    Parameters
    ----------
    self : VarParamSweep
        A VarParamSweep object
    simu : Simulation, optional
        Simulation holding the object (default: the parent)

    Raises
    ------
    ParamExplorerError: Error in ParamExplorer setting
    VarParamSweepError: Error in VarParamSweep general setting
    DataKeeperError: Error in DataKeeper setting
    """
    # run the base class check first
    super(type(self), self).check_param(simu=simu)

    # Check ParamExplorers
    for paramexplorer in self.paramexplorer_list:
        if paramexplorer.setter is None:
            raise ParamExplorerError("ParamExplorer.setter must be defined")
        elif len(paramexplorer.symbol) == 0:
            raise ParamExplorerError("ParamExplorer.symbol cannot be empty")
        elif (
            isinstance(paramexplorer, ParamExplorerSet)
            and len(paramexplorer.value) == 0
        ):
            raise ParamExplorerError("ParamExplorer.value_list cannot be empty")

    # Default simulation index
    N_simu = self.get_simu_number()

    # Keep every output if there is no DataKeeper defined
    if len(self.datakeeper_list) == 0 and self.is_keep_all_output is False:
        logger = get_logger(self)
        logger.warning(
            "No datakeeper has been define in VarParamSweep, setting is_keep_all_output as True."
        )
        self.is_keep_all_output = True

    # Check DataKeepers
    for datakeeper in self.datakeeper_list:
        if datakeeper.symbol in ["", None]:
            raise DataKeeperError("DataKeeper.symbol cannot be empty")
        elif datakeeper.keeper is None:
            raise DataKeeperError("DataKeeper.keeper must be defined")
