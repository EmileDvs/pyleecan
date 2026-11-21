from ....classes_common.logger_context import get_logger
from . import _execute


def solve_FEA(self, output) -> None:
    """Solve the FEA simulation

    Parameters
    ----------


    Return
    ------


    """
    cwd = self.get_path_save_fea(output)  # current working dir

    logger = get_logger(self)

    for info in _execute("ElmerSolver", cwd, logger):
        print(info, end="")
