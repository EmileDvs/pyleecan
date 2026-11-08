# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiGenAlgNsga2Deap.csv
"""Generated experimental dataclass; do not edit by hand."""

import random
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from deap import base, creator, tools
from deap.base import Toolbox
from deap.tools import cxOnePoint, mutPolynomialBounded, selNSGA2

from ..Functions.Optimization.check_cstr import check_cstr
from ..Functions.Optimization.evaluate import evaluate
from ..Functions.Optimization.tournamentDCD import tournamentDCD
from ..Functions.Optimization.update import update
from .data_keeper import DataKeeper
from .opti_design_var_interval import OptiDesignVarInterval
from .opti_design_var_set import OptiDesignVarSet
from .opti_gen_alg import OptiGenAlg
from .opti_objective import OptiObjective
from .output import Output
from .param_explorer_set import ParamExplorerSet
from .var_simu import VarSimu
from .xoutput import XOutput


@dataclass(eq=False)
class OptiGenAlgNsga2Deap(OptiGenAlg):
    """Multi-objectives optimization problem with some constraints

    Attributes
    ----------
    toolbox : deap.base.Toolbox or None
        DEAP toolbox
        Default: None
    """

    toolbox: Toolbox | None = "None"
    """DEAP toolbox"""

    # Inlined from Methods.Optimization.OptiGenAlgNsga2Deap.check_optimization_input
    def check_optimization_input(self):
        """Check optimization parameters before solving the problem

        Parameters
        ----------
        solver : Solver
            solver to perform the genetic algorithm with DEAP
        """

        logger = self.get_logger()

        # Check problem existence
        if self.problem == None:
            raise self.OptimizationAttributeError(
                "The problem has not been defined, please add a problem to OptiGenAlgNsga2Deap."
            )

        # Check population size
        if self.size_pop % 4 > 0:
            mess = "Change population size from {} to {} to fit with the tournament selection".format(
                self.size_pop, self.size_pop + (self.size_pop % 4)
            )
            self.size_pop += self.size_pop % 4

            logger.warning(mess)

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

    # Inlined from Methods.Optimization.OptiGenAlgNsga2Deap.create_toolbox
    def create_toolbox(self):
        """OptiGenAlgNsga2Deap method to create DEAP toolbox
        Parameters
        ----------
        self : OptiGenAlgNsga2Deap

        Returns
        -------
        self : OptiGenAlgNsga2Deap
            OptiGenAlgNsga2Deap with toolbox created
        """

        # Create toolbox
        self.toolbox = base.Toolbox()

        # Create Fitness and individual
        creator.create(
            "FitnessMin", base.Fitness, weights=[-1 for _ in self.problem.obj_func]
        )
        creator.create("Individual", list, typecode="d", fitness=creator.FitnessMin)

        self.toolbox.register("creator", creator.Individual)

        # Create default output
        if isinstance(self.problem.simu.parent, Output):
            output = self.problem.simu.parent
        elif isinstance(
            self.problem.simu.var_simu, VarSimu
        ):  # Optimization of a multi-simulation
            output = XOutput(simu=self.problem.simu.copy())
        else:
            output = Output(simu=self.problem.simu.copy())

        # Register individual and population
        self.toolbox.register(
            "individual",
            self.create_indiv,
            self.toolbox.creator,
            output,
            self.problem.design_var,
        )

        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )

    @staticmethod
    def create_indiv(create, output, design_var_list):
        """Create individual using DEAP tools

        Parameters
        ----------
        creator : function
            function to create the individual
        output : ....Classes.Output
            output of the individual
        design_var_list : list
            Design variables

        Returns:
        --------
        indiv : list
            individual
        """

        # Extract design variables
        var = []

        for design_var in design_var_list:
            # Generate the first value
            value = design_var.get_value(design_var.space)
            design_var.setter(output.simu, value)
            var.append(value)

        ind = create(var)

        # Store the design_var_name_list
        ind.design_var_name_list = [dv.name for dv in design_var_list]

        # Store setters in a list
        ind.setter_list = [dv.setter for dv in design_var_list]

        # Store the design variables
        ind.design_var = design_var_list

        # Store the simulation validity
        ind.is_simu_valid = False

        # Store the number of constraints violations
        ind.cstr_viol = 0

        # Output with the design variables set
        ind.output = type(output)(simu=output.simu.as_dict(keep_function=True))

        return ind

    # Inlined from Methods.Optimization.OptiGenAlgNsga2Deap.cross
    def cross(self, indiv1, indiv2):
        """Perform the crossover (One crossover by default)

        Parameters
        ----------
        self : OptiGenNsga2Deap
            Optimization solver

        indiv1 : individual
            first individual to modify
        indiv2 : individual
            second individual to modify

        Returns
        -------
        is_cross : bool
            True if the crossover append
        """

        if random.random() < self.p_cross:
            if self.crossover == None:
                if cxOnePoint == None:
                    raise ImportError("deap module is needed.")
                else:
                    cxOnePoint(indiv1, indiv2)
            else:
                self.crossover(indiv1, indiv2)

            return True
        else:
            return False

    # Inlined from Methods.Optimization.OptiGenAlgNsga2Deap.delete_toolbox
    def delete_toolbox(self):
        """OptiGenAlgNsga2Deap method to delete DEAP toolbox
        Parameters
        ----------
        self : OptiGenAlgNsga2Deap
        """

        # Delete toolbox
        self.toolbox = None

        # Delete creator classes
        del creator.FitnessMin
        del creator.Individual

    # Inlined from Methods.Optimization.OptiGenAlgNsga2Deap.mutate
    def mutate(self, indiv):
        """Mutate the individual design variables with different strategies according to the variables types :
            - interval : Polynomial Bounded mutation or user defined
            - set : Resampling the variable according to its initialization function
            - pyleecan : Resampling the variable according to its initialization function

        Parameters
        ----------
        solver : Solver
            solver to perform the genetic algorithm with DEAP
        indiv : individual (e.g. OptiGenAlgIndivDeap)
            individual to mutate

        Returns
        -------
        is_mutation : boolean
            True if at least one mutation occured
        """
        is_mutation = False

        for k, design_var in enumerate(indiv.design_var):
            if self.p_mutate < random.random():  # Perform mutation
                is_mutation = True

                if self.mutator == None:
                    if isinstance(
                        design_var, OptiDesignVarInterval
                    ):  # Interval variable
                        # Using polynomial bounded mutation as in Deb and al., "A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II"
                        if isinstance(indiv[k], Iterable):
                            indiv[k] = mutPolynomialBounded(
                                indiv[k], 20, *design_var.space, 1
                            )[0]
                        else:
                            # Function takes list in argument and returns list
                            indiv[k] = mutPolynomialBounded(
                                [indiv[k]], 20, *design_var.space, 1
                            )[0][0]
                    else:  # Uniform mutation
                        indiv[k] = random.choice(design_var.space)
                else:  # User defined mutator
                    if isinstance(
                        design_var, OptiDesignVarInterval
                    ):  # Interval variable
                        indiv[k] = self.mutator(indiv[k])
                    else:
                        # TODO Allow to redefine mutators for set
                        indiv[k] = design_var.function(design_var.space)
        return is_mutation

    # Inlined from Methods.Optimization.OptiGenAlgNsga2Deap.plot_pareto
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
        self : OptiGenAlgNsga2Deap
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

        # Gather fitness results
        data = [
            val.result
            for _, val in self.xoutput.xoutput_dict.items()
            if isinstance(val, OptiObjective)
        ]
        fitness = np.array(data).T

        # Get fitness values and ngen
        is_valid = np.array(self.xoutput["is_valid"].result)
        # ngen = np.array(self["ngen"].result)  # unused

        design_var_list = [pe.value for pe in self.xoutput.paramexplorer_list]
        design_var = np.array(design_var_list).T

        # Keep only valid values
        indx = np.where(is_valid)
        fitness = fitness[indx]
        # ngen = ngen[indx]   # unused
        design_var = design_var[indx]

        # get data and labels
        x_values, x_label = self.xoutput._get_symbol_data_(x_symbol, indx)
        y_values, y_label = self.xoutput._get_symbol_data_(y_symbol, indx)

        # Get pareto front
        pareto = fitness

        # Get dominated values
        idx_non_dom = list(range(len(pareto)))
        N = len(pareto)
        for i in range(N):
            for j in idx_non_dom:
                if all(pareto[j] <= pareto[i]) and any(pareto[j] < pareto[i]):
                    idx_non_dom.remove(i)
                    break

        pareto = pareto[idx_non_dom]
        design_var_values = design_var[idx_non_dom]

        # Write annotations
        legend_annot = []

        design_var_symbols = [pe.symbol for pe in self.xoutput.paramexplorer_list]

        for idx, sim in enumerate(design_var_values.tolist()):
            legend = f"Individual Nr. {indx[0][idx_non_dom[idx]]}\n"
            for ii, symbol in enumerate(design_var_symbols):
                legend += "{:11.10}=".format(symbol)  # sim[d_var])
                if isinstance(sim[ii], float):
                    legend += " {:3.3e}\n".format(sim[ii])
                else:
                    legend += "{:>11.10}\n".format(str(sim[ii]))
            legend_annot.append(legend[:-1])
        if ax is None:
            fig, ax = plt.subplots()
            return_ax = False
        else:
            return_ax = True
            fig = ax.get_figure()

        if c_symbol is None:
            colors = pyleecan_color
        else:
            # get the color data
            c_values, _ = self.xoutput._get_symbol_data_(c_symbol, indx)
            colors = c_values[idx_non_dom][:, np.newaxis]

        if cmap is None:
            cmap = plt.cm.jet

        # Plot Pareto front
        sc = ax.scatter(
            x_values[idx_non_dom][:, np.newaxis],
            y_values[idx_non_dom][:, np.newaxis],
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
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        if grid:
            ax.set_axisbelow(True)
            ax.grid()

        # Add anotations in the plot see https://stackoverflow.com/a/47166787
        annot = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        annot.set_visible(False)

        def update_annot(ind):
            """Update annotation"""
            # Get ind position
            pos = sc.get_offsets()[ind["ind"][0]]
            annot.xy = pos

            # Set the annotation
            annot.set_text(legend_annot[ind["ind"][0]])
            annot.get_bbox_patch().set_facecolor(pyleecan_color)
            annot.get_bbox_patch().set_alpha(0.4)

        def hover(event):
            # Check if annotation is visible
            vis = annot.get_visible()

            if event.inaxes == ax:
                cont, ind = sc.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)

        if is_show_fig:
            fig.show()

        if return_ax:
            return ax
        else:
            fig.show()

    # Inlined from Methods.Optimization.OptiGenAlgNsga2Deap.solve
    def solve(self, xoutput=None):
        """Method to perform NSGA-II using DEAP tools

        Parameters
        ----------
        self : OptiGenAlgNsga2Deap
            Solver to perform NSGA-II

        Returns
        -------
        multi_output : OutputMultiOpti
            class containing the results
        xoutput : XOutput
            class containing the results of the simulations
        """

        logger = self.get_logger()

        # Check input parameters
        self.check_optimization_input()

        # Display information
        try:
            filename = self.get_logger().handlers[0].stream.name
            print(
                "{} Starting optimization... \n\tLog file: {}\n\tNumber of generations: {}\n\tPopulation size: {}\n".format(
                    datetime.now().strftime("%H:%M:%S"),
                    filename,
                    self.nb_gen,
                    self.size_pop,
                )
            )
        except AttributeError, IndexError:
            print(
                "{} Starting optimization...\n\tNumber of generations: {}\n\tPopulation size: {}\n".format(
                    datetime.now().strftime("%H:%M:%S"), self.nb_gen, self.size_pop
                )
            )

        try:
            # Keep number of evalutation to create the shape
            shape = self.size_pop

            # Create the toolbox
            self.create_toolbox()

            # Add the reference output to multi_output
            if xoutput is not None:
                xoutput = xoutput
            else:
                xoutput = XOutput(simu=self.problem.simu.copy())

            self.xoutput = xoutput

            # Fitness symbol
            fitness_symbol = [of.symbol for of in self.problem.obj_func]

            # Set-up output data as list to be changed into ndarray at the end of the optimization
            paramexplorer_value = []
            xoutput.xoutput_dict["ngen"] = DataKeeper(
                name="Generation number", symbol="ngen"
            )
            xoutput.xoutput_dict["is_valid"] = DataKeeper(
                name="Individual validity", symbol="is_valid"
            )
            # Add datakeeper to XOutput to store additionnal values
            for dk in self.problem.datakeeper_list:
                assert dk.symbol not in xoutput.xoutput_dict
                xoutput.xoutput_dict[dk.symbol] = dk

            # Put objective functions in XOutput
            for obj_func in self.problem.obj_func:
                # obj_func is a DataKeeper instance
                xoutput.xoutput_dict[obj_func.symbol] = obj_func

            # Create the first population
            pop = self.toolbox.population(self.size_pop)

            # Evaluate the population
            nb_error = 0
            for i in range(0, self.size_pop):
                time = datetime.now().strftime("%H:%M:%S")
                self.print_gen_simu(time, 0, i, self.size_pop, nb_error, pop)
                nb_error += evaluate(self, pop[i])
                self.print_obj(self.problem.obj_func, pop[i])

            # Check the constraints violation
            nb_infeasible = 0
            if len(self.problem.constraint) > 0:
                time = datetime.now().strftime("%H:%M:%S")
                for indiv in pop:
                    nb_infeasible += check_cstr(self, indiv) == False
            print(
                "\r{}  gen {:>5}: Finished, {:>4} errors,{:>4} infeasible.\n".format(
                    time, 0, nb_error, nb_infeasible
                )
            )

            # Add pop to XOutput
            for indiv in pop:
                # Check that at every fitness values is different from inf
                is_valid = indiv.is_simu_valid and indiv.cstr_viol == 0

                if self.is_keep_all_output:
                    xoutput.output_list.append(indiv.output)

                # is_valid
                xoutput.xoutput_dict["is_valid"].result.append(is_valid)

                # Design variable values
                paramexplorer_value.append(list(indiv))

                # Add fitness values to DataKeeper
                for i, symbol in enumerate(fitness_symbol):
                    xoutput.xoutput_dict[symbol].result.append(indiv.fitness.values[i])

                # ngen
                xoutput.xoutput_dict["ngen"].result.append(0)

            if self.selector == None:
                pop = selNSGA2(pop, self.size_pop)
            else:
                parents = self.selector(pop, self.size_pop)

            ############################
            # LOOP FOR EACH GENERATION #
            ############################
            for ngen in range(1, self.nb_gen):
                # Extracting parents using
                parents = tournamentDCD(pop, self.size_pop)

                # Copy new indivuals
                children = []

                for indiv in parents:
                    child = self.toolbox.individual()
                    for i in range(len(indiv)):
                        child[i] = deepcopy(indiv[i])
                    child.output = indiv.output.copy()
                    child.fitness = deepcopy(indiv.fitness)
                    children.append(child)

                for indiv1, indiv2 in zip(children[::2], children[::-2]):
                    # Crossover
                    is_cross = self.cross(indiv1, indiv2)

                    # Mutation
                    is_mutation = self.mutate(indiv1)
                    if is_cross or is_mutation:
                        update(indiv1)

                    is_mutation = self.mutate(indiv2)
                    if is_cross or is_mutation:
                        update(indiv2)

                # Evaluate the children
                to_eval = []
                for indiv in children:
                    if indiv.fitness.valid == False:
                        to_eval.append(indiv)

                shape += len(to_eval)

                nb_error = 0
                for i in range(len(to_eval)):
                    time = datetime.now().strftime("%H:%M:%S")
                    self.print_gen_simu(time, ngen, i, self.size_pop, nb_error, to_eval)
                    nb_error += evaluate(self, to_eval[i])
                    self.print_obj(self.problem.obj_func, to_eval[i])

                # Check the constraints violation
                nb_infeasible = 0
                if len(self.problem.constraint) > 0:
                    time = datetime.now().strftime("%H:%M:%S")
                    for indiv in to_eval:
                        nb_infeasible += check_cstr(self, indiv) == False
                print(
                    "\r{}  gen {:>5}: Finished, {:>4} errors,{:>4} infeasible.\n".format(
                        time, ngen, nb_error, nb_infeasible
                    )
                )

                # Add pop to XOutput
                for indiv in to_eval:
                    # Check that at every fitness values is different from inf
                    is_valid = indiv.is_simu_valid and indiv.cstr_viol == 0

                    if self.is_keep_all_output:
                        xoutput.output_list.append(indiv.output)

                    # is_valid
                    xoutput.xoutput_dict["is_valid"].result.append(is_valid)

                    # Design variable values
                    paramexplorer_value.append(list(indiv))

                    # Fitness values
                    for i, symbol in enumerate(fitness_symbol):
                        xoutput.xoutput_dict[symbol].result.append(
                            indiv.fitness.values[i]
                        )
                    # ngen
                    xoutput.xoutput_dict["ngen"].result.append(ngen)

                # Sorting the population according to NSGA2
                if self.selector == None:
                    pop = selNSGA2(pop + children, self.size_pop)
                else:
                    pop = self.selector(pop, self.size_pop)

            # Change xoutput variables in ndarray
            paramexplorer_value = np.array(paramexplorer_value)

            # Storing number of simulations
            xoutput.nb_simu = shape

            # Save design variable values in ParamExplorerSet
            for i, param_explorer in enumerate(self.problem.design_var):
                if param_explorer._setter_str is None:
                    setter = param_explorer._setter_func
                else:
                    setter = param_explorer._setter_str
                xoutput.paramexplorer_list.append(
                    ParamExplorerSet(
                        name=param_explorer.name,
                        unit=param_explorer.unit,
                        symbol=param_explorer.symbol,
                        setter=setter,
                        value=paramexplorer_value[:, i].tolist(),
                    )
                )

            # Delete toolbox so that classes created with DEAP remains after the optimization
            self.delete_toolbox()

            return xoutput

        except KeyboardInterrupt:
            # Except keybord interruption to return the results already computed
            logger.info("Interrupted by the user.")
            # Change xoutput variables in ndarray
            paramexplorer_value = np.array(paramexplorer_value)

            # Storing number of simulations
            xoutput.nb_simu = shape

            # Save design variable values in ParamExplorerSet
            for i, param_explorer in enumerate(self.problem.design_var):
                xoutput.paramexplorer_list.append(
                    ParamExplorerSet(
                        name=param_explorer.name,
                        unit=param_explorer.unit,
                        symbol=param_explorer.symbol,
                        setter=param_explorer.setter,
                        value=paramexplorer_value[:, i].tolist(),
                    )
                )

            # Delete toolbox so that classes created with DEAP remains after the optimization
            self.delete_toolbox()

            return xoutput

        except Exception as err:
            logger.error("{}: {}".format(type(err).__name__, err))
            raise err

    @staticmethod
    def print_gen_simu(time, gen_id, simu_id, size_pop, nb_error, to_eval):
        print(
            "\r{}  gen {:>5}: simu {}/{} ({:>5.2f}%), {:>4} errors.".format(
                time,
                gen_id,
                (simu_id + 1),
                size_pop,
                (simu_id) * 100 / size_pop,
                nb_error,
            )
        )
        msg = "Design Variables: "
        for ii in range(len(to_eval[simu_id])):
            msg += (
                to_eval[simu_id].design_var[ii].symbol
                + ": "
                + format(to_eval[simu_id][ii], ".2e")
                + ", "
            )
        print(msg[:-2])

    @staticmethod
    def print_obj(obj_func, indiv):
        msg = "Objectives: "
        for ii in range(len(obj_func)):
            msg += (
                obj_func[ii].symbol
                + ": "
                + format(indiv.fitness.values[ii], ".2e")
                + ", "
            )
        print(msg[:-2] + "\n")

    class OptimizationAttributeError(Exception):
        """Class to Raise an error"""

        def __init__(self, message):
            self.message = message
