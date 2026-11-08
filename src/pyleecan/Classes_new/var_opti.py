# Experimental dataclass generated from Generator/ClassesRef/Simulation/VarOpti.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from ..Functions.Load.import_class import import_class
from .opti_constraint import OptiConstraint
from .opti_objective import OptiObjective
from .opti_problem import OptiProblem
from .opti_solver import OptiSolver
from .var_param import VarParam


@dataclass(eq=False)
class VarOpti(VarParam):
    """Handle Optimization multisimulation by varying parameters

    Attributes
    ----------
    objective_list : [OptiObjective] or None
        List containing OptiObjective objects
        Default: None
    constraint_list : [OptiConstraint] or None
        List containing OptiConstraint objects
        Default: None
    solver : OptiSolver or None
        Object that solve an OptiProblem
        Default: None
    """

    NAME: ClassVar = "Optimization"
    objective_list: list[OptiObjective] | None = None
    """List containing OptiObjective objects"""
    constraint_list: list[OptiConstraint] | None = None
    """List containing OptiConstraint objects"""
    solver: OptiSolver | None = None
    """Object that solve an OptiProblem"""

    # Inlined from Methods.Simulation.VarOpti.check
    def check(self):
        """Check VarOpti parameters validity"""

        Simu1 = import_class("pyleecan.Classes", "Simu1")
        OptiDesignVarSet = import_class("pyleecan.Classes", "OptiDesignVarSet")
        OptiBayesAlgSmoot = import_class("pyleecan.Classes", "OptiBayesAlgSmoot")
        OptiGenAlgNsga2Deap = import_class("pyleecan.Classes", "OptiGenAlgNsga2Deap")
        OptiDesignVarInterval = import_class(
            "pyleecan.Classes", "OptiDesignVarInterval"
        )

        # Check that VarOpti is always in the first layer of var_simu
        if not isinstance(self.parent, Simu1):
            raise self.VarOptiError(
                "VarOpti object must be the very first layer in var_simu"
            )

        # Check objectives
        if self.objective_list == -1 or not isinstance(self.objective_list, list):
            raise self.VarOptiError("VarOpti object must have a list in objective_list")
        elif len(self.objective_list) == 0:
            raise self.VarOptiError(
                "VarOpti object must have at least one objective in objective_list"
            )
        else:
            for objective in self.objective_list:
                if not isinstance(objective, OptiObjective):
                    raise self.VarOptiError(
                        "VarOpti object must have only OptiObjective objects in objective_list"
                    )
                elif objective.symbol in ["", None]:
                    raise self.VarOptiObjectiveError(
                        "OptiObjective.symbol cannot be empty"
                    )
                elif objective.keeper is None:
                    raise self.VarOptiObjectiveError(
                        "OptiObjective.keeper must be defined"
                    )

        # Check constraints
        if self.constraint_list == -1 or not isinstance(self.constraint_list, list):
            raise self.VarOptiError(
                "VarOpti object must have a list in constraint_list"
            )
        elif not len(self.constraint_list) == 0:
            for constraint in self.constraint_list:
                if not isinstance(constraint, OptiConstraint):
                    raise self.VarOptiError(
                        "VarOpti object must have only OptiConstraint objects in constraint_list"
                    )
                elif constraint.value in ["", None]:
                    raise self.VarOptiConstraintError(
                        "OptiConstraint.symbol cannot be empty"
                    )
                elif constraint.keeper is None:
                    raise self.VarOptiConstraintError(
                        "OptiConstraint.keeper must be defined"
                    )

        # Check design variables
        if self.paramexplorer_list == -1 or not isinstance(
            self.paramexplorer_list, list
        ):
            raise self.VarOptiError(
                "VarOpti object must have a list in paramexplorer_list"
            )
        elif len(self.paramexplorer_list) == 0:
            raise self.VarOptiError(
                "VarOpti object must have at least one objective in paramexplorer_list"
            )
        else:
            for design_var in self.paramexplorer_list:
                if not isinstance(design_var, OptiDesignVarInterval) and not isinstance(
                    design_var, OptiDesignVarSet
                ):
                    raise self.VarOptiError(
                        "VarOpti object must have only OptiDesignVarInterval or OptiDesignVarSet objects in paramexplorer_list"
                    )
                elif design_var.symbol in ["", None]:
                    raise self.VarOptiDesignVarError(
                        "OptiDesignVarSet.symbol or OptiDesignVarInterval.symbol cannot be empty"
                    )
                elif design_var.setter is None:
                    raise self.VarOptiDesignVarError(
                        "OptiDesignVarSet.setter or OptiDesignVarInterval.setter must be defined"
                    )

        # Keep every output if there is no DataKeeper defined
        if len(self.datakeeper_list) == 0 and self.is_keep_all_output is False:
            logger = self.get_logger()
            logger.warning(
                "No datakeeper has been define in VarParamSweep, setting is_keep_all_output as True."
            )
            self.is_keep_all_output = True

        # Check DataKeepers
        for datakeeper in self.datakeeper_list:
            if datakeeper.symbol in ["", None]:
                raise self.VarOptiDataKeeperError("DataKeeper.symbol cannot be empty")
            elif datakeeper.keeper is None:
                raise self.VarOptiDataKeeperError("DataKeeper.keeper must be defined")

        # Check solver
        if self.solver is None:
            raise self.VarOptiSolverError("VarOpti object must have a solver")
        elif not isinstance(self.solver, OptiGenAlgNsga2Deap) and not isinstance(
            self.solver, OptiBayesAlgSmoot
        ):
            raise self.VarOptiSolverError(
                "VarOpti object must have only a solver of type OptiGenAlgNsga2Deap or OptiBayesAlgSmoot"
            )

        solver = self.get_full_solver()
        solver.check_optimization_input()

    # Inlined from Methods.Simulation.VarOpti.get_full_solver
    def get_full_solver(self):
        """Method to return a fully setted solver"""

        # Create reference simulation
        ref_simu = self.parent.copy()
        ref_simu.var_simu = self.var_simu  # var_simu default is None
        ref_simu.index = None
        ref_simu.layer = self.parent.layer + 1

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
    def run(self):
        """Run method for VarOpti to solve the problem"""

        solver = self.get_full_solver()

        # Launch simulations
        xoutput = solver.solve(xoutput=self.parent.parent)

        return xoutput

    class VarOptiConstraintError(Exception):
        pass

    class VarOptiDataKeeperError(Exception):
        pass

    class VarOptiDesignVarError(Exception):
        pass

    class VarOptiError(Exception):
        pass

    class VarOptiObjectiveError(Exception):
        pass

    class VarOptiSolverError(Exception):
        pass
