# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/VarLoadVoltage.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/VarLoadVoltage
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .VarLoad import VarLoad

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from .ParamExplorerSet import ParamExplorerSet
from .Simulation import Simulation
from ..Functions.Simulation.VarSimu.get_elec_datakeeper_dict import (
    get_elec_datakeeper_dict,
)
from .InputVoltage import InputVoltage

from numpy import isnan
from ._check import InitUnKnowClassError


class VarLoadVoltage(VarLoad):
    """Generate a multisimulation with InputVoltage at variable operating point"""

    VERSION = 1

    # cf Methods.Simulation.VarLoadVoltage.generate_simulation_list
    def generate_simulation_list(self, ref_simu=None):
        """Generate all the simulation for the multi-simulation

        Parameters
        ----------
        self : VarLoadVoltage
            A VarLoadVoltage object
        ref_simu : Simulation
            Reference simulation to copy / update

        Returns
        -------
        multisim_dict : dict
            dictionary containing the simulation and paramexplorer list
        """

        # Get InputCurrent list
        list_input = self.get_input_list()

        multisim_dict = {
            "paramexplorer_list": [],  # Setter's values
            "simulation_list": [],
        }

        # Create ParamExplorerSet
        #   This version uses a single ParamExplorerSet to define the simulation
        #   Other parameters can be stored in a dedicated ParamExplorerSet if needed
        multisim_dict["paramexplorer_list"].append(
            ParamExplorerSet(
                name="InputVoltage",
                symbol="In",
                unit="-",
                setter="simu.input",
                getter="simu.input",
                value=list_input,
            )
        )

        # Create Simulations 1 per load
        for input_obj in list_input:
            # Generate the simulation
            new_simu = ref_simu.copy()

            # Edit simulation
            new_simu.input = input_obj
            # Add simulation to the list
            multisim_dict["simulation_list"].append(new_simu)

        return multisim_dict

    # cf Methods.Simulation.VarLoadVoltage.get_elec_datakeeper
    def get_elec_datakeeper(self, symbol_list, is_multi=False):
        """Generate DataKeepers to store by default results from electric module
        Parameters
        ----------
        self: VarLoadVoltage
            A VarLoadVoltage object
        symbol_list : list
            List of the existing datakeeper (to avoid duplicate)
        is_multi : bool
            True for multi-simulation of multi-simulation
        Returns
        -------
        dk_list: list
            list of DataKeeper
        """

        dk_dict = get_elec_datakeeper_dict()
        dk_list = []

        if not is_multi:
            quantity_list = ["Ud", "Uq"]
            # Add "U0", "UPhi0" for Async machine
            if (
                self.parent is not None
                and isinstance(self.parent, Simulation)
                and not self.parent.machine.is_synchronous()
            ):
                quantity_list.extend(["U0", "UPhi0"])
            elif (
                self.parent is not None
                and self.parent.parent is not None
                and isinstance(self.parent.parent, Simulation)
                and not self.parent.parent.machine.is_synchronous()
            ):
                quantity_list.extend(["U0", "UPhi0"])
            # Add slip if provided in the OP_matrix
            if self.OP_matrix is not None and self.OP_matrix.has_slip():
                quantity_list.append("slip")
            # Add torque if provided in the OP_matrix
            if self.OP_matrix is not None and self.OP_matrix.has_Tem():
                quantity_list.append("Tem_av_ref")

        # Save Id
        if not is_multi:
            for key in quantity_list:
                if key not in symbol_list:
                    dk_list.append(dk_dict[key])

        return dk_list

    # cf Methods.Simulation.VarLoadVoltage.get_input_list
    def get_input_list(self):
        """Return a list of InputVoltage to set the Operating point"""

        # Check that the object has the correct type
        assert isinstance(self.parent, Simulation)
        ref_simu = self.parent
        assert isinstance(ref_simu.input, InputVoltage)

        OP_list = self.OP_matrix.get_OP_list()
        N_simu = len(OP_list)

        # Generate initial input_list
        ref_input = ref_simu.input.copy()
        input_list = [ref_input.copy() for ii in range(N_simu)]

        # Set default time vector (enforce definition Nt_tot, Nrev)
        if ref_input.Nt_tot is None:
            Nt_tot = len(ref_input.time.get_data())
        else:
            Nt_tot = ref_input.Nt_tot

        # Update OP according to OP_matrix
        for ii in range(N_simu):
            input_list[ii].OP = OP_list[ii]
            # Edit time vector
            input_list[ii].time = None
            input_list[ii].Nt_tot = Nt_tot
            input_list[ii].Nrev = ref_input.Nrev

        return input_list

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        OP_matrix=None,
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
            if "OP_matrix" in list(init_dict.keys()):
                OP_matrix = init_dict["OP_matrix"]
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
        # Call VarLoad init
        super(VarLoadVoltage, self).__init__(
            OP_matrix=OP_matrix,
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
        # The class is frozen (in VarLoad init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        VarLoadVoltage_str = ""
        # Get the properties inherited from VarLoad
        VarLoadVoltage_str += super(VarLoadVoltage, self).__str__()
        return VarLoadVoltage_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from VarLoad
        if not super(VarLoadVoltage, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from VarLoad
        diff_list.extend(
            super(VarLoadVoltage, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from VarLoad
        S += super(VarLoadVoltage, self).__sizeof__()
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

        # Get the properties inherited from VarLoad
        VarLoadVoltage_dict = super(VarLoadVoltage, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        VarLoadVoltage_dict["__class__"] = "VarLoadVoltage"
        return VarLoadVoltage_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.OP_matrix is None:
            OP_matrix_val = None
        else:
            OP_matrix_val = self.OP_matrix.copy()
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
            OP_matrix=OP_matrix_val,
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

        # Set to None the properties inherited from VarLoad
        super(VarLoadVoltage, self)._set_None()
