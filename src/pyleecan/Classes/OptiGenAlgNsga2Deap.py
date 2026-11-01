# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Optimization/OptiGenAlgNsga2Deap.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Optimization/OptiGenAlgNsga2Deap
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - cross: module contains unsupported top-level Try statements

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.OptiGenAlg import OptiGenAlg

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Optimization.OptiGenAlgNsga2Deap.cross import cross
from pyleecan.Methods.Optimization.OptiGenAlgNsga2Deap.check_optimization_input import (
    OptimizationAttributeError,
)
from pyleecan.Classes.OptiObjective import OptiObjective
from pyleecan.Classes.OptiDesignVarSet import OptiDesignVarSet
from pyleecan.Classes.OptiDesignVarInterval import OptiDesignVarInterval
from pyleecan.Methods.Optimization.OptiGenAlgNsga2Deap.create_toolbox import (
    create_indiv,
)
from deap import base, creator, tools
from pyleecan.Classes.Output import Output
from pyleecan.Classes.XOutput import XOutput
from pyleecan.Classes.VarSimu import VarSimu
import random, numpy as np, matplotlib.pyplot as plt
from collections.abc import Iterable
from deap.tools import mutPolynomialBounded, selNSGA2
from pyleecan.Methods.Output.XOutput import _get_symbol_data_
from pyleecan.Methods.Optimization.OptiGenAlgNsga2Deap.solve import (
    print_gen_simu,
    print_obj,
)
from copy import deepcopy
from datetime import datetime
from pyleecan.Classes.DataKeeper import DataKeeper
from pyleecan.Classes.ParamExplorerSet import ParamExplorerSet
from pyleecan.Functions.Optimization.evaluate import evaluate
from pyleecan.Functions.Optimization.update import update
from pyleecan.Functions.Optimization.check_cstr import check_cstr
from pyleecan.Functions.Optimization.tournamentDCD import tournamentDCD

from ntpath import basename
from os.path import isfile
from pyleecan.Classes._check import CheckTypeError

import random

from cloudpickle import dumps, loads
from pyleecan.Classes._check import CheckTypeError

try:
    from deap.base import Toolbox
except ImportError:
    Toolbox = ImportError
from pyleecan.Classes._check import InitUnKnowClassError


class OptiGenAlgNsga2Deap(OptiGenAlg):
    """Multi-objectives optimization problem with some constraints"""

    VERSION = 1

    # cf Methods.Optimization.OptiGenAlgNsga2Deap.check_optimization_input
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
            raise OptimizationAttributeError(
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
            raise OptimizationAttributeError(
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
                    raise OptimizationAttributeError(mess)

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
                raise OptimizationAttributeError(mess)

        # Check the problem contains at least one objective function
        if self.problem.design_var == None or (
            isinstance(self.problem.design_var, list)
            and len(self.problem.design_var) == 0
        ):
            raise OptimizationAttributeError(
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
                    raise OptimizationAttributeError(mess)
                elif design_var.symbol in [None, ""]:
                    mess = "The design variable '{}' has no symbol.".format(
                        design_var.name
                    )
                    raise OptimizationAttributeError(mess)
                elif not callable(design_var.get_value):
                    mess = "OptiDesignVar '{}' get_value is not callable.".format(
                        design_var.name
                    )
                    raise OptimizationAttributeError(mess)
                elif not callable(design_var.setter):
                    mess = "OptiDesignVar '{}' setter is not callable.".format(
                        design_var.name
                    )
                    raise OptimizationAttributeError(mess)

        # Check constraints type
        if self.problem.constraint != None:
            for cstr in self.problem.constraint:
                # Check type of constraint
                if cstr.type_const not in ["<=", "<", "==", "=", ">=", ">"]:
                    mess = "The constraint '{}' has a wrong type: expected one of {} received '{}'.".format(
                        cstr.name, ["<=", "<", "==", "=", ">=", ">"], cstr.type_const
                    )
                    raise OptimizationAttributeError(mess)
                # Check getter
                elif not callable(cstr.keeper):
                    mess = (
                        "The constraint '{}' function keeper is not callable.".format(
                            cstr.name
                        )
                    )
                    raise OptimizationAttributeError(mess)

    # cf Methods.Optimization.OptiGenAlgNsga2Deap.create_toolbox
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
            create_indiv,
            self.toolbox.creator,
            output,
            self.problem.design_var,
        )

        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )

    # cf Methods.Optimization.OptiGenAlgNsga2Deap.cross
    cross = cross

    # cf Methods.Optimization.OptiGenAlgNsga2Deap.delete_toolbox
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

    # cf Methods.Optimization.OptiGenAlgNsga2Deap.mutate
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

    # cf Methods.Optimization.OptiGenAlgNsga2Deap.plot_pareto
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
        x_values, x_label = _get_symbol_data_(self.xoutput, x_symbol, indx)
        y_values, y_label = _get_symbol_data_(self.xoutput, y_symbol, indx)

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
            c_values, _ = _get_symbol_data_(self.xoutput, c_symbol, indx)
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

    # cf Methods.Optimization.OptiGenAlgNsga2Deap.solve
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
        except (AttributeError, IndexError):
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
                print_gen_simu(time, 0, i, self.size_pop, nb_error, pop)
                nb_error += evaluate(self, pop[i])
                print_obj(self.problem.obj_func, pop[i])

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
                    print_gen_simu(time, ngen, i, self.size_pop, nb_error, to_eval)
                    nb_error += evaluate(self, to_eval[i])
                    print_obj(self.problem.obj_func, to_eval[i])

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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        toolbox=None,
        selector=None,
        crossover=None,
        mutator=None,
        p_cross=0.9,
        p_mutate=0.1,
        size_pop=40,
        nb_gen=100,
        problem=-1,
        xoutput=-1,
        logger_name="Pyleecan.OptiSolver",
        is_keep_all_output=False,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "toolbox" in list(init_dict.keys()):
                toolbox = init_dict["toolbox"]
            if "selector" in list(init_dict.keys()):
                selector = init_dict["selector"]
            if "crossover" in list(init_dict.keys()):
                crossover = init_dict["crossover"]
            if "mutator" in list(init_dict.keys()):
                mutator = init_dict["mutator"]
            if "p_cross" in list(init_dict.keys()):
                p_cross = init_dict["p_cross"]
            if "p_mutate" in list(init_dict.keys()):
                p_mutate = init_dict["p_mutate"]
            if "size_pop" in list(init_dict.keys()):
                size_pop = init_dict["size_pop"]
            if "nb_gen" in list(init_dict.keys()):
                nb_gen = init_dict["nb_gen"]
            if "problem" in list(init_dict.keys()):
                problem = init_dict["problem"]
            if "xoutput" in list(init_dict.keys()):
                xoutput = init_dict["xoutput"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
            if "is_keep_all_output" in list(init_dict.keys()):
                is_keep_all_output = init_dict["is_keep_all_output"]
        # Set the properties (value check and convertion are done in setter)
        self.toolbox = toolbox
        # Call OptiGenAlg init
        super(OptiGenAlgNsga2Deap, self).__init__(
            selector=selector,
            crossover=crossover,
            mutator=mutator,
            p_cross=p_cross,
            p_mutate=p_mutate,
            size_pop=size_pop,
            nb_gen=nb_gen,
            problem=problem,
            xoutput=xoutput,
            logger_name=logger_name,
            is_keep_all_output=is_keep_all_output,
        )
        # The class is frozen (in OptiGenAlg init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        OptiGenAlgNsga2Deap_str = ""
        # Get the properties inherited from OptiGenAlg
        OptiGenAlgNsga2Deap_str += super(OptiGenAlgNsga2Deap, self).__str__()
        OptiGenAlgNsga2Deap_str += "toolbox = " + str(self.toolbox) + linesep + linesep
        return OptiGenAlgNsga2Deap_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from OptiGenAlg
        if not super(OptiGenAlgNsga2Deap, self).__eq__(other):
            return False
        if other.toolbox != self.toolbox:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from OptiGenAlg
        diff_list.extend(
            super(OptiGenAlgNsga2Deap, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.toolbox is None and self.toolbox is not None) or (
            other.toolbox is not None and self.toolbox is None
        ):
            diff_list.append(name + ".toolbox None mismatch")
        elif self.toolbox is not None and self.toolbox != other.toolbox:
            diff_list.append(name + ".toolbox")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from OptiGenAlg
        S += super(OptiGenAlgNsga2Deap, self).__sizeof__()
        S += getsizeof(self.toolbox)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from OptiGenAlg
        OptiGenAlgNsga2Deap_dict = super(OptiGenAlgNsga2Deap, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        if self.toolbox is None:
            OptiGenAlgNsga2Deap_dict["toolbox"] = None
        else:
            # Store serialized data (using cloudpickle) and str
            # to read it in json save files
            OptiGenAlgNsga2Deap_dict["toolbox"] = {
                "__class__": str(type(self._toolbox)),
                "__repr__": str(self._toolbox.__repr__()),
                "serialized": dumps(self._toolbox).decode("ISO-8859-2"),
            }
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        OptiGenAlgNsga2Deap_dict["__class__"] = "OptiGenAlgNsga2Deap"
        return OptiGenAlgNsga2Deap_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.toolbox is None:
            toolbox_val = None
        else:
            toolbox_val = self.toolbox.copy()
        if self._selector_str is not None:
            selector_val = self._selector_str
        else:
            selector_val = self._selector_func
        if self._crossover_str is not None:
            crossover_val = self._crossover_str
        else:
            crossover_val = self._crossover_func
        if self._mutator_str is not None:
            mutator_val = self._mutator_str
        else:
            mutator_val = self._mutator_func
        p_cross_val = self.p_cross
        p_mutate_val = self.p_mutate
        size_pop_val = self.size_pop
        nb_gen_val = self.nb_gen
        if self.problem is None:
            problem_val = None
        else:
            problem_val = self.problem.copy()
        if self.xoutput is None:
            xoutput_val = None
        else:
            xoutput_val = self.xoutput.copy()
        logger_name_val = self.logger_name
        is_keep_all_output_val = self.is_keep_all_output
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            toolbox=toolbox_val,
            selector=selector_val,
            crossover=crossover_val,
            mutator=mutator_val,
            p_cross=p_cross_val,
            p_mutate=p_mutate_val,
            size_pop=size_pop_val,
            nb_gen=nb_gen_val,
            problem=problem_val,
            xoutput=xoutput_val,
            logger_name=logger_name_val,
            is_keep_all_output=is_keep_all_output_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.toolbox = None
        # Set to None the properties inherited from OptiGenAlg
        super(OptiGenAlgNsga2Deap, self)._set_None()

    def _get_toolbox(self):
        """getter of toolbox"""
        return self._toolbox

    def _set_toolbox(self, value):
        """setter of toolbox"""
        if value == -1:
            value = Toolbox()
        check_var("toolbox", value, "Toolbox")
        self._toolbox = value

    toolbox = property(
        fget=_get_toolbox,
        fset=_set_toolbox,
        doc="""DEAP toolbox

        :Type: deap.base.Toolbox
        """,
    )
