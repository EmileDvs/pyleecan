# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Import/ImportMeshUnv.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Import/ImportMeshUnv
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.Import import Import

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np, pyuff
from numpy import array as np_array, hstack, newaxis, stack, vstack

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class ImportMeshUnv(Import):
    """Import mesh data from an unv file"""

    VERSION = 1

    # cf Methods.Import.ImportMeshUnv.get_data
    def get_data(self):
        """Return mesh data (nodes and elements) from a .unv file

        Parameters
        ----------
        self : ImportData
            An ImportData object

        Returns
        -------
        nodes: ndarray
            The nodes id and coordinates (one line = id, 3 coordinates)
        elements: dict
            The elements id and connectivity per element type (one line = id, n node ids)

        """

        # Import data from .unv file
        uff_ascii = pyuff.UFF(self.file_path)
        datasets = uff_ascii.read_sets()

        # Scan datasets
        for dataset in datasets:
            # If nodes dataset
            if dataset["type"] == 15:
                nodes = stack(
                    (
                        np_array(dataset["node_nums"], np.int32),
                        dataset["x"],
                        dataset["y"],
                        dataset["z"],
                    ),
                    axis=1,
                )

            # If element dataset
            elif dataset["type"] == 2412:
                # Store connectivities
                elements = dict()
                for elt_type, elt_dict in dataset.items():
                    if (
                        elt_type != "type"
                        and isinstance(elt_type, str)
                        and isinstance(elt_dict, dict)
                    ):
                        elements[elt_type] = hstack(
                            (
                                np_array(elt_dict["element_nums"])[:, newaxis],
                                elt_dict["nodes_nums"],
                            )
                        )

            elif dataset["type"] == 82:
                # Store connectivities
                elements = dict()
                nodes_nums = dataset["nodes"]
                ind = np.where(nodes_nums == 0.0)  ##identify zeros
                nodes_nums = np.delete(nodes_nums, ind)  # delete zeros
                indices = list()  ##indices of duplicated node numbers
                for i in range(1, len(nodes_nums)):
                    if nodes_nums[i] == nodes_nums[i - 1]:
                        indices.append(i)
                nodes_nums = np.delete(nodes_nums, indices)

                indices_node1 = np.arange(
                    4, len(nodes_nums), 5
                )  ##indices of first node of previous element

                nodes_nums = np.delete(nodes_nums, indices_node1)

                ##assuming quad elements 4 nodes per element
                n = int(len(nodes_nums) / 4)
                nodes_nums = np.reshape(nodes_nums, (n, 4))
                element_nums = np.arange(len(nodes_nums))
                elements["quad"] = vstack((element_nums, nodes_nums.T)).T

        return nodes, elements

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, file_path="", init_dict=None, init_str=None):
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
            if "file_path" in list(init_dict.keys()):
                file_path = init_dict["file_path"]
        # Set the properties (value check and convertion are done in setter)
        self.file_path = file_path
        # Call Import init
        super(ImportMeshUnv, self).__init__()
        # The class is frozen (in Import init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        ImportMeshUnv_str = ""
        # Get the properties inherited from Import
        ImportMeshUnv_str += super(ImportMeshUnv, self).__str__()
        ImportMeshUnv_str += 'file_path = "' + str(self.file_path) + '"' + linesep
        return ImportMeshUnv_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Import
        if not super(ImportMeshUnv, self).__eq__(other):
            return False
        if other.file_path != self.file_path:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Import
        diff_list.extend(
            super(ImportMeshUnv, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._file_path != self._file_path:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._file_path)
                    + ", other="
                    + str(other._file_path)
                    + ")"
                )
                diff_list.append(name + ".file_path" + val_str)
            else:
                diff_list.append(name + ".file_path")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Import
        S += super(ImportMeshUnv, self).__sizeof__()
        S += getsizeof(self.file_path)
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

        # Get the properties inherited from Import
        ImportMeshUnv_dict = super(ImportMeshUnv, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        ImportMeshUnv_dict["file_path"] = self.file_path
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        ImportMeshUnv_dict["__class__"] = "ImportMeshUnv"
        return ImportMeshUnv_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        file_path_val = self.file_path
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(file_path=file_path_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.file_path = None
        # Set to None the properties inherited from Import
        super(ImportMeshUnv, self)._set_None()

    def _get_file_path(self):
        """getter of file_path"""
        return self._file_path

    def _set_file_path(self, value):
        """setter of file_path"""
        check_var("file_path", value, "str")
        self._file_path = value

    file_path = property(
        fget=_get_file_path,
        fset=_set_file_path,
        doc="""Path of the file to load

        :Type: str
        """,
    )
