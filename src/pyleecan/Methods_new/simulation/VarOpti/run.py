from typing import TYPE_CHECKING
from ....classes_common.parents import container_or_parent
if TYPE_CHECKING:
    from ....Classes_new.simulation.simulation import Simulation
    from ....Classes_new.output.xoutput import XOutput


def run(self, simu: Simulation | None = None, xoutput: XOutput | None = None):
    """Run method for VarOpti to solve the problem

    Parameters
    ----------
    self : VarOpti
        A VarOpti object
    simu : Simulation, optional
        Simulation holding the object (default: the parent)
    xoutput : XOutput, optional
        Output of the multi-simulation (default: the parent of the simulation)
    """
    xoutput = container_or_parent(self, xoutput, "xoutput", depth=2)

    solver = self.get_full_solver(simu=simu)

    # Launch simulations
    xoutput = solver.solve(xoutput=xoutput)

    return xoutput
