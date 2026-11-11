# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiBayesAlgSmoot.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

from ._smoot.smoot import MOO
from .data_keeper import DataKeeper
from .opti_bayes_alg import OptiBayesAlg
from .opti_design_var_interval import OptiDesignVarInterval
from .opti_design_var_set import OptiDesignVarSet
from .opti_objective import OptiObjective
from .output import Output
from .xoutput import XOutput


@dataclass(eq=False)
class OptiBayesAlgSmoot(OptiBayesAlg):
    """Multi-objectives optimization problem with some constraints

    Attributes
    ----------
    size_pop : int
        Number of individuals for each generation
        Default: 40; Minimum: 1
    nb_gen : int
        Number of generations for the genetic part
        Default: 100; Minimum: 1
    """

    size_pop: int = 40
    """Number of individuals for each generation"""
    nb_gen: int = 100
    """Number of generations for the genetic part"""

    # Inlined from Methods.Optimization.OptiBayesAlgSmoot.check_optimization_input
    def check_optimization_input(self):
        """Check optimization parameters before solving the problem

        Parameters
        ----------
        solver : Solver
            solver to perform the bayesian algorithm with SMT
        """

        logger = self.get_logger()

        # Check problem existence
        if self.problem == None:
            raise self.OptimizationAttributeError(
                "The problem has not been defined, please add a problem to OptiGenAlgNsga2Deap."
            )

        # Check the problem contains at least one design variable
        if self.problem.obj_func == None or (
            isinstance(self.problem.obj_func, dict) and len(self.problem.obj_func) == 0
        ):
            raise self.OptimizationAttributeError(
                "Optimization problem must contain at least one objective function"
            )

        else:
            for obj_func in self.problem.obj_func:
                if not isinstance(obj_func, OptiObjective):
                    raise TypeError(
                        "Wrong obj_func type: OptiObjective expected, got {}".format(
                            type(obj_func).__name__
                        )
                    )
                elif not callable(obj_func.keeper):
                    mess = "The objective function '{}' is not callable, please define the attribute 'keeper'.".format(
                        obj_func.name
                    )
                    raise self.OptimizationAttributeError(mess)

            # Check if objectives and other datakeepers have different symbol
            if isinstance(self.problem.datakeeper_list, list):
                symbol_list = [of.symbol for of in self.problem.obj_func] + [
                    dk.symbol for dk in self.problem.datakeeper_list
                ]
            else:
                symbol_list = [of.symbol for of in self.problem.obj_func]

            if len(symbol_list) != len(set(symbol_list)):
                mess = (
                    "Every objective function and datakeeper must have a unique symbol."
                )
                raise self.OptimizationAttributeError(mess)

        # Check the problem contains at least one objective function
        if self.problem.design_var == None or (
            isinstance(self.problem.design_var, list)
            and len(self.problem.design_var) == 0
        ):
            raise self.OptimizationAttributeError(
                "Optimization problem must contain at least one design variable"
            )
        else:
            for design_var in self.problem.design_var:
                if not isinstance(design_var, OptiDesignVarInterval) and not isinstance(
                    design_var, OptiDesignVarSet
                ):
                    mess = "The design variable '{}' is expected to be an OptiDesignVarSet or an OptiDesignVarInterval.".format(
                        design_var.name
                    )
                    raise self.OptimizationAttributeError(mess)
                elif design_var.symbol in [None, ""]:
                    mess = "The design variable '{}' has no symbol.".format(
                        design_var.name
                    )
                    raise self.OptimizationAttributeError(mess)
                elif not callable(design_var.get_value):
                    mess = "OptiDesignVar '{}' get_value is not callable.".format(
                        design_var.name
                    )
                    raise self.OptimizationAttributeError(mess)
                elif not callable(design_var.setter):
                    mess = "OptiDesignVar '{}' setter is not callable.".format(
                        design_var.name
                    )
                    raise self.OptimizationAttributeError(mess)

        # Check constraints type
        if self.problem.constraint != None:
            for cstr in self.problem.constraint:
                # Check type of constraint
                if cstr.type_const not in ["<=", "<", "==", "=", ">=", ">"]:
                    mess = "The constraint '{}' has a wrong type: expected one of {} received '{}'.".format(
                        cstr.name, ["<=", "<", "==", "=", ">=", ">"], cstr.type_const
                    )
                    raise self.OptimizationAttributeError(mess)
                # Check getter
                elif not callable(cstr.keeper):
                    mess = (
                        "The constraint '{}' function keeper is not callable.".format(
                            cstr.name
                        )
                    )
                    raise self.OptimizationAttributeError(mess)

    # Inlined from Methods.Optimization.OptiBayesAlgSmoot.eval_const
    def eval_const(self, constraint, input_x):
        """
        Evaluate the constraint at given points x
        """
        constraint_values = []

        for x in input_x:
            i = 0
            for var in self.problem.design_var:
                var.setter(self.xoutput.simu, x[i])
                i += 1

            const_value = constraint.keeper(self.xoutput)
            if constraint.type_const == "<=":
                constraint_values.append(const_value - constraint.value)
            elif constraint.type_const == ">=":
                constraint_values.append(constraint.value - const_value)

        return constraint_values

    # Inlined from Methods.Optimization.OptiBayesAlgSmoot.evaluate
    def evaluate(solver, input_x):
        # Clean previous obj value
        for obj in solver.problem.obj_func:
            obj.result.clear()

        for x in input_x:
            # Add simulation input value
            i = 0
            for var in solver.problem.design_var:
                var.setter(solver.problem.simu, x[i])
                i += 1

            # Start the simulation
            if solver.problem.eval_func == None:
                solver.problem.simu.run()
            else:
                solver.problem.eval_func(solver.xoutput)

            for obj in solver.problem.obj_func:
                obj.result.append(obj.keeper(solver.xoutput))

        # Get the requested result value(s)
        result = np.atleast_2d([obj.result for obj in solver.problem.obj_func])

        return result.T

    # Inlined from Methods.Optimization.OptiBayesAlgSmoot.plot_pareto
    def plot_pareto(
        self,
        x_symbol,
        y_symbol,
        c_symbol=None,
        cmap=None,
        ax=None,
        title=None,
        grid=False,
        is_show_fig=True,
        save_path=None,
    ):
        """Plot the pareto front for 2 objective functions

        Parameters
        ----------
        self : OptiBayesAlgSmoot
        x_symbol : str
            symbol of the first objective function
        y_symbol: str
            symbol of the second objective function
        c_symbol: str
            optional symbol to set the plot colors
        cmap: colormap
            optional colormap
        is_show_fig : bool
            True to show figure after plot
        save_path : str
            full path of the png file where the figure is saved if save_path is not None
        """

        # Pyleecan colors
        pyleecan_color = (230 / 255, 175 / 255, 0)

        # Get the correct objectives
        idx = 0
        idy = 0
        for i in range(len(self.problem.obj_func)):
            if self.problem.obj_func[i].symbol == x_symbol:
                idx = i
            if self.problem.obj_func[i].symbol == y_symbol:
                idy = i

        x_values = [
            self.xoutput["y_opt"].result[i][idx]
            for i in range(len(self.xoutput["y_opt"].result))
        ]
        y_values = [
            self.xoutput["y_opt"].result[i][idy]
            for i in range(len(self.xoutput["y_opt"].result))
        ]

        colors = pyleecan_color

        if cmap is None:
            cmap = plt.cm.jet

        if ax is None:
            fig, ax = plt.subplots()
            return_ax = False
        else:
            return_ax = True
            fig = ax.get_figure()

        # Plot Pareto front
        sc = ax.scatter(
            x_values,
            y_values,
            # facecolors=colors,
            c=colors,
            edgecolors=(0.35, 0.35, 0.35),
            label="Pareto Front",
            cmap=cmap,
        )
        # Add legend
        if c_symbol is not None:
            legend1 = ax.legend(
                *sc.legend_elements(), loc="upper right", title=c_symbol
            )
            ax.add_artist(legend1)

        ax.autoscale(1, 1)

        ax.set_title("Pareto Front")
        ax.set_xlabel(x_symbol)
        ax.set_ylabel(y_symbol)

        if grid:
            ax.set_axisbelow(True)
            ax.grid()

        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)

        if is_show_fig:
            fig.show()

        if return_ax:
            return ax
        else:
            fig.show()

    # Inlined from Methods.Optimization.OptiBayesAlgSmoot.solve
    def solve(self):
        """Method to perform Bayesian optimization using Smoot tools

        Parameters
        ----------
        self : OptiBayesAlgSmoot
            Solver to perform Bayesian model creation, then use a genetic algorithm

        Returns
        -------
        multi_output : OutputMultiOpti
            class containing the results
        """

        logger = self.get_logger()

        # Check input parameters
        self.check_optimization_input()

        # Display information
        try:
            filename = self.get_logger().handlers[0].stream.name
            print(
                "{} Starting optimization... \n\tLog file: {}\n\tNumber of generations: {}\n\tPopulation size: {}\n".format(
                    datetime.now().strftime("%H:%M:%S"), filename, self.nb_iter
                )
            )
        except AttributeError, IndexError:
            print(
                "{} Starting optimization...\n\tNumber of iterations: {}\n\t".format(
                    datetime.now().strftime("%H:%M:%S"), self.nb_iter
                )
            )

        try:
            # Add the reference output to multi_output
            if isinstance(self.problem.simu.parent, Output):
                xoutput = XOutput(
                    init_dict=self.problem.simu.parent.as_dict(keep_function=True)
                )
            else:
                xoutput = XOutput(simu=self.problem.simu)

            self.xoutput = xoutput

            # Set-up output data as list to be changed into ndarray at the end of the optimization
            paramexplorer_value = []
            xoutput.xoutput_dict["n_iter"] = DataKeeper(
                name="Generation number", symbol="n_iter"
            )

            xoutput.xoutput_dict["x_opt"] = (
                DataKeeper(  # need to put a better name here
                    name="x opt", symbol="x_opt"
                )
            )
            xoutput.xoutput_dict["y_opt"] = (
                DataKeeper(  # need to put a better name here
                    name="y opt", symbol="y_opt"
                )
            )

            # Add datakeeper to XOutput to store additionnal values
            for dk in self.problem.datakeeper_list:
                assert dk.symbol not in xoutput.xoutput_dict
                xoutput.xoutput_dict[dk.symbol] = dk

            # Put objective functions in XOutput
            for obj_func in self.problem.obj_func:
                # obj_func is a DataKeeper instance
                xoutput.xoutput_dict[obj_func.symbol] = obj_func

            n_iter = self.nb_iter
            xlimits = np.array([var.space for var in self.problem.design_var])

            const = [
                lambda x, i=i: self.eval_const(self.problem.constraint[i], x)
                for i in range(len(self.problem.constraint))
            ]

            time = datetime.now()

            moo = MOO(
                n_iter=self.nb_iter,
                criterion=self.criterion,
                n_start=self.nb_start,
                xlimits=xlimits,
                # const=const,
                verbose=True,
                n_gen=self.nb_gen,
                pop_size=self.size_pop,
            )

            moo.optimize(fun=self.evaluate)

            final_time = datetime.now() - time

            print(
                "{} End of optimization, solved in {}.\n".format(
                    datetime.now().strftime("%H:%M:%S"), final_time
                )
            )
            res = moo.result

            xoutput.xoutput_dict["x_opt"].result = res.X.tolist()
            xoutput.xoutput_dict["y_opt"].result = res.F.tolist()

            return xoutput

        except KeyboardInterrupt:
            # Except keybord interruption to return the results already computed
            logger.info("Interrupted by the user.")
            # Change xoutput variables in ndarray

            return xoutput

        except Exception as err:
            logger.error("{}: {}".format(type(err).__name__, err))
            raise err

    class OptimizationAttributeError(Exception):
        """Class to Raise an error"""

        def __init__(self, message):
            self.message = message
