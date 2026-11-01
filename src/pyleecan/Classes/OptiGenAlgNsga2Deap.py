# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Optimization/OptiGenAlgNsga2Deap.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Optimization/OptiGenAlgNsga2Deap
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - cross: module contains unsupported top-level Try statements
# - delete_toolbox: import name 'creator' refers to different sources (..Methods.Optimization.OptiGenAlgNsga2Deap.create_toolbox.creator and deap.creator)
# - mutate: import name 'OptiDesignVarInterval' refers to different sources (..Methods.Optimization.OptiGenAlgNsga2Deap.check_optimization_input.OptiDesignVarInterval and .OptiDesignVarInterval.OptiDesignVarInterval)
# - plot_pareto: import name 'OptiObjective' refers to different sources (..Methods.Optimization.OptiGenAlgNsga2Deap.check_optimization_input.OptiObjective and .OptiObjective.OptiObjective)
# - solve: import name 'XOutput' refers to different sources (..Methods.Optimization.OptiGenAlgNsga2Deap.create_toolbox.XOutput and ..Methods.Optimization.OptiGenAlgNsga2Deap.solve.XOutput)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .OptiGenAlg import OptiGenAlg

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Optimization.OptiGenAlgNsga2Deap.cross import cross
from ..Methods.Optimization.OptiGenAlgNsga2Deap.delete_toolbox import delete_toolbox
from ..Methods.Optimization.OptiGenAlgNsga2Deap.mutate import mutate
from ..Methods.Optimization.OptiGenAlgNsga2Deap.plot_pareto import plot_pareto
from ..Methods.Optimization.OptiGenAlgNsga2Deap.solve import solve
from ..Methods.Optimization.OptiGenAlgNsga2Deap.check_optimization_input import (
    OptiDesignVarInterval,
    OptiDesignVarSet,
    OptiObjective,
    OptimizationAttributeError,
)
from ..Methods.Optimization.OptiGenAlgNsga2Deap.create_toolbox import (
    Output,
    VarSimu,
    XOutput,
    base,
    create_indiv,
    creator,
    tools,
)

from ntpath import basename
from os.path import isfile
from ._check import CheckTypeError
import numpy as np
import random
from numpy import isnan
from cloudpickle import dumps, loads
from ._check import CheckTypeError

try:
    from deap.base import Toolbox
except ImportError:
    Toolbox = ImportError
from ._check import InitUnKnowClassError


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
    delete_toolbox = delete_toolbox
    # cf Methods.Optimization.OptiGenAlgNsga2Deap.mutate
    mutate = mutate
    # cf Methods.Optimization.OptiGenAlgNsga2Deap.plot_pareto
    plot_pareto = plot_pareto
    # cf Methods.Optimization.OptiGenAlgNsga2Deap.solve
    solve = solve
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
            **kwargs
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
