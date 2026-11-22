# Experimental pydantic model generated from Generator/ClassesRef/Simulation/VarOpti.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

from pydantic import Field

from ...classes_common.errors import (
    VarOptiConstraintError,
    VarOptiDataKeeperError,
    VarOptiDesignVarError,
    VarOptiError,
    VarOptiObjectiveError,
    VarOptiSolverError,
)
from ...classes_common.logger_context import get_logger
from ...classes_common.parents import container_or_parent
from ..optimization.opti_constraint import OptiConstraint
from ..optimization.opti_objective import OptiObjective
from ..optimization.opti_problem import OptiProblem
from ..optimization.opti_solver import OptiSolver
from .var_param import VarParam

if TYPE_CHECKING:
    from ..output.xoutput import XOutput
    from .simulation import Simulation


class VarOpti(VarParam):
    """Handle Optimization multisimulation by varying parameters

    Attributes
    ----------
    objective_list : [OptiObjective] or None
        List containing OptiObjective objects
        Default: []
    constraint_list : [OptiConstraint] or None
        List containing OptiConstraint objects
        Default: []
    solver : OptiSolver or None
        Object that solve an OptiProblem
        Default: None
    """

    NAME: ClassVar = "Optimization"

    objective_list: list[OptiObjective] = Field(default_factory=list)
    """List containing OptiObjective objects"""
    constraint_list: list[OptiConstraint] = Field(default_factory=list)
    """List containing OptiConstraint objects"""
    solver: OptiSolver | None = None
    """Object that solve an OptiProblem"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.VarOpti.check
    def check(self, simu: Simulation | None = None) -> None:
        """Check VarOpti parameters validity

        Parameters
        ----------
        self : VarOpti
            A VarOpti object
        simu : Simulation, optional
            Simulation holding the object (default: the parent)
        """
        simu = container_or_parent(self, simu, "simu")

        # Local import: avoids circular imports
        from ..optimization.opti_bayes_alg_smoot import OptiBayesAlgSmoot
        from ..optimization.opti_design_var_interval import OptiDesignVarInterval
        from ..optimization.opti_design_var_set import OptiDesignVarSet
        from ..optimization.opti_gen_alg_nsga_2_deap import OptiGenAlgNsga2Deap
        from .simu_1 import Simu1

        # Check that VarOpti is always in the first layer of var_simu
        if not isinstance(simu, Simu1):
            raise VarOptiError(
                "VarOpti object must be the very first layer in var_simu"
            )

        # Check objectives
        if self.objective_list == -1 or not isinstance(self.objective_list, list):
            raise VarOptiError("VarOpti object must have a list in objective_list")
        elif len(self.objective_list) == 0:
            raise VarOptiError(
                "VarOpti object must have at least one objective in objective_list"
            )
        else:
            for objective in self.objective_list:
                if not isinstance(objective, OptiObjective):
                    raise VarOptiError(
                        "VarOpti object must have only OptiObjective objects in objective_list"
                    )
                elif objective.symbol in ["", None]:
                    raise VarOptiObjectiveError("OptiObjective.symbol cannot be empty")
                elif objective.keeper is None:
                    raise VarOptiObjectiveError("OptiObjective.keeper must be defined")

        # Check constraints
        if self.constraint_list == -1 or not isinstance(self.constraint_list, list):
            raise VarOptiError("VarOpti object must have a list in constraint_list")
        elif not len(self.constraint_list) == 0:
            for constraint in self.constraint_list:
                if not isinstance(constraint, OptiConstraint):
                    raise VarOptiError(
                        "VarOpti object must have only OptiConstraint objects in constraint_list"
                    )
                elif constraint.value in ["", None]:
                    raise VarOptiConstraintError(
                        "OptiConstraint.symbol cannot be empty"
                    )
                elif constraint.keeper is None:
                    raise VarOptiConstraintError(
                        "OptiConstraint.keeper must be defined"
                    )

        # Check design variables
        if self.paramexplorer_list == -1 or not isinstance(
            self.paramexplorer_list, list
        ):
            raise VarOptiError("VarOpti object must have a list in paramexplorer_list")
        elif len(self.paramexplorer_list) == 0:
            raise VarOptiError(
                "VarOpti object must have at least one objective in paramexplorer_list"
            )
        else:
            for design_var in self.paramexplorer_list:
                if not isinstance(design_var, OptiDesignVarInterval) and not isinstance(
                    design_var, OptiDesignVarSet
                ):
                    raise VarOptiError(
                        "VarOpti object must have only OptiDesignVarInterval or OptiDesignVarSet objects in paramexplorer_list"
                    )
                elif design_var.symbol in ["", None]:
                    raise VarOptiDesignVarError(
                        "OptiDesignVarSet.symbol or OptiDesignVarInterval.symbol cannot be empty"
                    )
                elif design_var.setter is None:
                    raise VarOptiDesignVarError(
                        "OptiDesignVarSet.setter or OptiDesignVarInterval.setter must be defined"
                    )

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
                raise VarOptiDataKeeperError("DataKeeper.symbol cannot be empty")
            elif datakeeper.keeper is None:
                raise VarOptiDataKeeperError("DataKeeper.keeper must be defined")

        # Check solver
        if self.solver is None:
            raise VarOptiSolverError("VarOpti object must have a solver")
        elif not isinstance(self.solver, OptiGenAlgNsga2Deap) and not isinstance(
            self.solver, OptiBayesAlgSmoot
        ):
            raise VarOptiSolverError(
                "VarOpti object must have only a solver of type OptiGenAlgNsga2Deap or OptiBayesAlgSmoot"
            )

        solver = self.get_full_solver(simu=simu)
        solver.check_optimization_input()

    # Inlined from Methods.Simulation.VarOpti.get_full_solver
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

    # Inlined from Methods.Simulation.VarOpti.run
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
