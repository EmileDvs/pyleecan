# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Optimization/OptiBayesAlgSmoot.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Optimization/OptiBayesAlgSmoot
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - solve: import name 'np' refers to different sources (numpy as np and ..Methods.Optimization.OptiBayesAlgSmoot.solve.np)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .OptiBayesAlg import OptiBayesAlg

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Optimization.OptiBayesAlgSmoot.solve import solve
from ..Methods.Optimization.OptiBayesAlgSmoot.check_optimization_input import (
    OptiDesignVarInterval,
    OptiDesignVarSet,
    OptiObjective,
    OptimizationAttributeError,
)
import numpy as np, matplotlib.pyplot as plt

from numpy import isnan
from ._check import InitUnKnowClassError


class OptiBayesAlgSmoot(OptiBayesAlg):
    """Multi-objectives optimization problem with some constraints"""

    VERSION = 1

    # cf Methods.Optimization.OptiBayesAlgSmoot.check_optimization_input
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
            raise OptimizationAttributeError(
                "The problem has not been defined, please add a problem to OptiGenAlgNsga2Deap."
            )

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

    # cf Methods.Optimization.OptiBayesAlgSmoot.eval_const
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

    # cf Methods.Optimization.OptiBayesAlgSmoot.evaluate
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

    # cf Methods.Optimization.OptiBayesAlgSmoot.plot_pareto
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

    # cf Methods.Optimization.OptiBayesAlgSmoot.solve
    solve = solve
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        size_pop=40,
        nb_gen=100,
        nb_iter=15,
        nb_start=300,
        criterion="PI",
        kernel=0,
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
            if "size_pop" in list(init_dict.keys()):
                size_pop = init_dict["size_pop"]
            if "nb_gen" in list(init_dict.keys()):
                nb_gen = init_dict["nb_gen"]
            if "nb_iter" in list(init_dict.keys()):
                nb_iter = init_dict["nb_iter"]
            if "nb_start" in list(init_dict.keys()):
                nb_start = init_dict["nb_start"]
            if "criterion" in list(init_dict.keys()):
                criterion = init_dict["criterion"]
            if "kernel" in list(init_dict.keys()):
                kernel = init_dict["kernel"]
            if "problem" in list(init_dict.keys()):
                problem = init_dict["problem"]
            if "xoutput" in list(init_dict.keys()):
                xoutput = init_dict["xoutput"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
            if "is_keep_all_output" in list(init_dict.keys()):
                is_keep_all_output = init_dict["is_keep_all_output"]
        # Set the properties (value check and convertion are done in setter)
        self.size_pop = size_pop
        self.nb_gen = nb_gen
        # Call OptiBayesAlg init
        super(OptiBayesAlgSmoot, self).__init__(
            nb_iter=nb_iter,
            nb_start=nb_start,
            criterion=criterion,
            kernel=kernel,
            problem=problem,
            xoutput=xoutput,
            logger_name=logger_name,
            is_keep_all_output=is_keep_all_output,
        )
        # The class is frozen (in OptiBayesAlg init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        OptiBayesAlgSmoot_str = ""
        # Get the properties inherited from OptiBayesAlg
        OptiBayesAlgSmoot_str += super(OptiBayesAlgSmoot, self).__str__()
        OptiBayesAlgSmoot_str += "size_pop = " + str(self.size_pop) + linesep
        OptiBayesAlgSmoot_str += "nb_gen = " + str(self.nb_gen) + linesep
        return OptiBayesAlgSmoot_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from OptiBayesAlg
        if not super(OptiBayesAlgSmoot, self).__eq__(other):
            return False
        if other.size_pop != self.size_pop:
            return False
        if other.nb_gen != self.nb_gen:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from OptiBayesAlg
        diff_list.extend(
            super(OptiBayesAlgSmoot, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._size_pop != self._size_pop:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._size_pop)
                    + ", other="
                    + str(other._size_pop)
                    + ")"
                )
                diff_list.append(name + ".size_pop" + val_str)
            else:
                diff_list.append(name + ".size_pop")
        if other._nb_gen != self._nb_gen:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._nb_gen)
                    + ", other="
                    + str(other._nb_gen)
                    + ")"
                )
                diff_list.append(name + ".nb_gen" + val_str)
            else:
                diff_list.append(name + ".nb_gen")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from OptiBayesAlg
        S += super(OptiBayesAlgSmoot, self).__sizeof__()
        S += getsizeof(self.size_pop)
        S += getsizeof(self.nb_gen)
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

        # Get the properties inherited from OptiBayesAlg
        OptiBayesAlgSmoot_dict = super(OptiBayesAlgSmoot, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        OptiBayesAlgSmoot_dict["size_pop"] = self.size_pop
        OptiBayesAlgSmoot_dict["nb_gen"] = self.nb_gen
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        OptiBayesAlgSmoot_dict["__class__"] = "OptiBayesAlgSmoot"
        return OptiBayesAlgSmoot_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        size_pop_val = self.size_pop
        nb_gen_val = self.nb_gen
        nb_iter_val = self.nb_iter
        nb_start_val = self.nb_start
        criterion_val = self.criterion
        kernel_val = self.kernel
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
            size_pop=size_pop_val,
            nb_gen=nb_gen_val,
            nb_iter=nb_iter_val,
            nb_start=nb_start_val,
            criterion=criterion_val,
            kernel=kernel_val,
            problem=problem_val,
            xoutput=xoutput_val,
            logger_name=logger_name_val,
            is_keep_all_output=is_keep_all_output_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.size_pop = None
        self.nb_gen = None
        # Set to None the properties inherited from OptiBayesAlg
        super(OptiBayesAlgSmoot, self)._set_None()

    def _get_size_pop(self):
        """getter of size_pop"""
        return self._size_pop

    def _set_size_pop(self, value):
        """setter of size_pop"""
        check_var("size_pop", value, "int", Vmin=1)
        self._size_pop = value

    size_pop = property(
        fget=_get_size_pop,
        fset=_set_size_pop,
        doc="""Number of individuals for each generation

        :Type: int
        :min: 1
        """,
    )

    def _get_nb_gen(self):
        """getter of nb_gen"""
        return self._nb_gen

    def _set_nb_gen(self, value):
        """setter of nb_gen"""
        check_var("nb_gen", value, "int", Vmin=1)
        self._nb_gen = value

    nb_gen = property(
        fget=_get_nb_gen,
        fset=_set_nb_gen,
        doc="""Number of generations for the genetic part

        :Type: int
        :min: 1
        """,
    )
