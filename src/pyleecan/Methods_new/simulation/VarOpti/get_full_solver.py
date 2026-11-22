from typing import TYPE_CHECKING
from ....classes_common.parents import container_or_parent
from ....Classes_new.optimization.opti_problem import OptiProblem


if TYPE_CHECKING:
    from ....Classes_new.simulation.simulation import Simulation


def get_full_solver(self, simu: Simulation | None = None):
    """Method to return a fully setted solver

    Parameters
    ----------
    self : VarOpti
        A VarOpti object
    simu : Simulation, optional
        Simulation holding the object (default: the parent)
    """
    simu = container_or_parent(self, simu, "simu")

    # Create reference simulation
    ref_simu = simu.copy()
    ref_simu.var_simu = self.var_simu  # var_simu default is None
    ref_simu.index = None
    ref_simu.layer = simu.layer + 1

    # Creation of the problem
    problem = OptiProblem(
        simu=ref_simu,
        design_var=self.paramexplorer_list,
        obj_func=self.objective_list,
        datakeeper_list=self.datakeeper_list,
        constraint=self.constraint_list,
    )

    # Copy the solver to don't rewrite it and give the problem
    solver = self.solver.copy()
    solver.problem = problem

    return solver
