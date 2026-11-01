# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/VarParamSweep.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/VarParamSweep
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - generate_simulation_list: import name 'ParamExplorerSet' refers to different sources (..Methods.Simulation.VarParamSweep.check_param.ParamExplorerSet and .ParamExplorerSet.ParamExplorerSet)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .VarParam import VarParam

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Simulation.VarParamSweep.generate_simulation_list import (
    generate_simulation_list,
)
from ..Methods.Simulation.VarParamSweep.check_param import (
    DataKeeperError,
    ParamExplorerError,
    ParamExplorerSet,
)

from numpy import isnan
from ._check import InitUnKnowClassError


class VarParamSweep(VarParam):
    """Handle multisimulation by varying parameters"""

    VERSION = 1
    NAME = "Parameter Sweep"

    # cf Methods.Simulation.VarParamSweep.check_param
    def check_param(self):
        """Check VarParamSweep parameters validity

        Raises
        ------
        ParamExplorerError: Error in ParamExplorer setting
        VarParamSweepError: Error in VarParamSweep general setting
        DataKeeperError: Error in DataKeeper setting
        """
        # run the base class check first
        super(type(self), self).check_param()

        # Check ParamExplorers
        for paramexplorer in self.paramexplorer_list:
            if paramexplorer.setter is None:
                raise ParamExplorerError("ParamExplorer.setter must be defined")
            elif len(paramexplorer.symbol) == 0:
                raise ParamExplorerError("ParamExplorer.symbol cannot be empty")
            elif (
                isinstance(paramexplorer, ParamExplorerSet)
                and len(paramexplorer.value) == 0
            ):
                raise ParamExplorerError("ParamExplorer.value_list cannot be empty")

        # Default simulation index
        N_simu = self.get_simu_number()

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
                raise DataKeeperError("DataKeeper.symbol cannot be empty")
            elif datakeeper.keeper is None:
                raise DataKeeperError("DataKeeper.keeper must be defined")

    # cf Methods.Simulation.VarParamSweep.generate_simulation_list
    generate_simulation_list = generate_simulation_list

    # cf Methods.Simulation.VarParamSweep.get_simu_number
    def get_simu_number(self):
        """Return the number of simulation defined by the Param Explorer

        Parameters
        ----------
        self : VarParamSweep
            A VarParamSweep object

        Returns
        -------
        nb_simu : int
            number of simulation
        """

        nb_simu = 1
        for paramexplorer in self.paramexplorer_list:
            nb_simu *= paramexplorer.get_N()

        return nb_simu

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        paramexplorer_list=-1,
        name="",
        desc="",
        datakeeper_list=-1,
        is_keep_all_output=False,
        stop_if_error=False,
        var_simu=None,
        nb_simu=0,
        is_reuse_femm_file=True,
        postproc_list=-1,
        pre_keeper_postproc_list=None,
        post_keeper_postproc_list=None,
        is_reuse_LUT=True,
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
            if "paramexplorer_list" in list(init_dict.keys()):
                paramexplorer_list = init_dict["paramexplorer_list"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "desc" in list(init_dict.keys()):
                desc = init_dict["desc"]
            if "datakeeper_list" in list(init_dict.keys()):
                datakeeper_list = init_dict["datakeeper_list"]
            if "is_keep_all_output" in list(init_dict.keys()):
                is_keep_all_output = init_dict["is_keep_all_output"]
            if "stop_if_error" in list(init_dict.keys()):
                stop_if_error = init_dict["stop_if_error"]
            if "var_simu" in list(init_dict.keys()):
                var_simu = init_dict["var_simu"]
            if "nb_simu" in list(init_dict.keys()):
                nb_simu = init_dict["nb_simu"]
            if "is_reuse_femm_file" in list(init_dict.keys()):
                is_reuse_femm_file = init_dict["is_reuse_femm_file"]
            if "postproc_list" in list(init_dict.keys()):
                postproc_list = init_dict["postproc_list"]
            if "pre_keeper_postproc_list" in list(init_dict.keys()):
                pre_keeper_postproc_list = init_dict["pre_keeper_postproc_list"]
            if "post_keeper_postproc_list" in list(init_dict.keys()):
                post_keeper_postproc_list = init_dict["post_keeper_postproc_list"]
            if "is_reuse_LUT" in list(init_dict.keys()):
                is_reuse_LUT = init_dict["is_reuse_LUT"]
        # Set the properties (value check and convertion are done in setter)
        # Call VarParam init
        super(VarParamSweep, self).__init__(
            paramexplorer_list=paramexplorer_list,
            name=name,
            desc=desc,
            datakeeper_list=datakeeper_list,
            is_keep_all_output=is_keep_all_output,
            stop_if_error=stop_if_error,
            var_simu=var_simu,
            nb_simu=nb_simu,
            is_reuse_femm_file=is_reuse_femm_file,
            postproc_list=postproc_list,
            pre_keeper_postproc_list=pre_keeper_postproc_list,
            post_keeper_postproc_list=post_keeper_postproc_list,
            is_reuse_LUT=is_reuse_LUT,
        )
        # The class is frozen (in VarParam init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        VarParamSweep_str = ""
        # Get the properties inherited from VarParam
        VarParamSweep_str += super(VarParamSweep, self).__str__()
        return VarParamSweep_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from VarParam
        if not super(VarParamSweep, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from VarParam
        diff_list.extend(
            super(VarParamSweep, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from VarParam
        S += super(VarParamSweep, self).__sizeof__()
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

        # Get the properties inherited from VarParam
        VarParamSweep_dict = super(VarParamSweep, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        VarParamSweep_dict["__class__"] = "VarParamSweep"
        return VarParamSweep_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.paramexplorer_list is None:
            paramexplorer_list_val = None
        else:
            paramexplorer_list_val = list()
            for obj in self.paramexplorer_list:
                paramexplorer_list_val.append(obj.copy())
        name_val = self.name
        desc_val = self.desc
        if self.datakeeper_list is None:
            datakeeper_list_val = None
        else:
            datakeeper_list_val = list()
            for obj in self.datakeeper_list:
                datakeeper_list_val.append(obj.copy())
        is_keep_all_output_val = self.is_keep_all_output
        stop_if_error_val = self.stop_if_error
        if self.var_simu is None:
            var_simu_val = None
        else:
            var_simu_val = self.var_simu.copy()
        nb_simu_val = self.nb_simu
        is_reuse_femm_file_val = self.is_reuse_femm_file
        if self.postproc_list is None:
            postproc_list_val = None
        else:
            postproc_list_val = list()
            for obj in self.postproc_list:
                postproc_list_val.append(obj.copy())
        if self.pre_keeper_postproc_list is None:
            pre_keeper_postproc_list_val = None
        else:
            pre_keeper_postproc_list_val = list()
            for obj in self.pre_keeper_postproc_list:
                pre_keeper_postproc_list_val.append(obj.copy())
        if self.post_keeper_postproc_list is None:
            post_keeper_postproc_list_val = None
        else:
            post_keeper_postproc_list_val = list()
            for obj in self.post_keeper_postproc_list:
                post_keeper_postproc_list_val.append(obj.copy())
        is_reuse_LUT_val = self.is_reuse_LUT
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            paramexplorer_list=paramexplorer_list_val,
            name=name_val,
            desc=desc_val,
            datakeeper_list=datakeeper_list_val,
            is_keep_all_output=is_keep_all_output_val,
            stop_if_error=stop_if_error_val,
            var_simu=var_simu_val,
            nb_simu=nb_simu_val,
            is_reuse_femm_file=is_reuse_femm_file_val,
            postproc_list=postproc_list_val,
            pre_keeper_postproc_list=pre_keeper_postproc_list_val,
            post_keeper_postproc_list=post_keeper_postproc_list_val,
            is_reuse_LUT=is_reuse_LUT_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from VarParam
        super(VarParamSweep, self)._set_None()
