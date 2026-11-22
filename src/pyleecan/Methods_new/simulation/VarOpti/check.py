from ....classes_common.logger_context import get_logger


class VarOptiError(Exception):
    pass


class VarOptiObjectiveError(Exception):
    pass


class VarOptiConstraintError(Exception):
    pass


class VarOptiDesignVarError(Exception):
    pass


class VarOptiSolverError(Exception):
    pass


class VarOptiDataKeeperError(Exception):
    pass


def check(self) -> None:
    """Check VarOpti parameters validity"""

    # Local import: avoids circular imports
    from ....Classes_new.simulation.simu_1 import Simu1
    from ....Classes_new.optimization.opti_objective import OptiObjective
    from ....Classes_new.optimization.opti_constraint import OptiConstraint
    from ....Classes_new.optimization.opti_design_var_set import OptiDesignVarSet
    from ....Classes_new.optimization.opti_bayes_alg_smoot import OptiBayesAlgSmoot
    from ....Classes_new.optimization.opti_gen_alg_nsga_2_deap import OptiGenAlgNsga2Deap
    from ....Classes_new.optimization.opti_design_var_interval import OptiDesignVarInterval


    # Check that VarOpti is always in the first layer of var_simu
    if not isinstance(self.parent, Simu1):
        raise VarOptiError("VarOpti object must be the very first layer in var_simu")

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
                raise VarOptiConstraintError("OptiConstraint.symbol cannot be empty")
            elif constraint.keeper is None:
                raise VarOptiConstraintError("OptiConstraint.keeper must be defined")

    # Check design variables
    if self.paramexplorer_list == -1 or not isinstance(self.paramexplorer_list, list):
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

    solver = self.get_full_solver()
    solver.check_optimization_input()
