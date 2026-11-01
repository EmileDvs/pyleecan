# File generated according to Generator/ClassesRef/Import/ImportMeshMat.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Import/ImportMeshMat"""

from os import linesep
from os.path import splitext
from sys import getsizeof

import numpy as np
from pyleecan.Classes.ImportMeshUnv import ImportMeshUnv
from pyleecan.Classes.MeshMat import MeshMat
from pyleecan.Classes.NodeMat import NodeMat
from pyleecan.Classes.RefQuad4 import RefQuad4
from pyleecan.Classes.RefTriangle3 import RefTriangle3

from pyleecan.Classes._check import check_var
from pyleecan.Classes.ElementMat import ElementMat
from pyleecan.Classes.Import import Import
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class ImportMeshMat(Import):
    """Import mesh as meshMat"""

    VERSION = 1

    # cf Methods.Import.ImportMeshMat.get_data
    def get_data(self):
        """Import mesh and generate MeshMat object

        Parameters
        ----------
        self : ImportData
            An ImportData object

        Returns
        -------
        mesh: MeshMat
            The generated MeshMat object

        """

        # Get mesh data (nodes and elements)
        file_extension = splitext(self.file_path)[1]
        if file_extension == ".unv":
            nodes, elements = ImportMeshUnv(self.file_path).get_data()
        else:
            raise Exception(f"{file_extension} files are not supported")

        # Define MeshMat object
        if min(nodes[:, 0]) == 0 and max(nodes[:, 0]) == len(nodes[:, 0]) - 1:
            is_renum = False
        else:
            is_renum = True

        mesh = MeshMat(_is_renum=is_renum)

        node_indices = nodes[:, 0].astype(np.int32)

        # Node indices must start at 0 and be consecutive
        unique_node_indices = np.unique(node_indices)
        if unique_node_indices.size != node_indices.size:
            raise ValueError("Duplicated node index")

        if (
            unique_node_indices[0] != 0
            or unique_node_indices[-1] != unique_node_indices.size - 1
        ):
            for new_index, old_index in enumerate(unique_node_indices):
                node_indices[node_indices == old_index] = new_index

                # Change indices in element connectivity value
                for element in elements.values():
                    element[:, 1:][element[:, 1:] == old_index] = new_index

        # Define NodeMat object
        mesh.node = NodeMat(
            coordinate=nodes[:, 1:],
            nb_node=nodes.shape[0],
            indice=node_indices,
        )

        # Ensure that element indices are between 0 and nb_element - 1
        element_indices = np.hstack(
            [elt[:, 0].astype(np.int32) for elt in elements.values()]
        )

        unique_element_indices = np.unique(
            element_indices
        )  # Values returned are sorted

        if unique_element_indices.size < element_indices.size:
            raise ValueError("Duplicated element index")

        min_indice = 0
        if (
            unique_element_indices[0] != 0
            or unique_element_indices[-1] != unique_element_indices.size - 1
        ):
            # Refactor indices
            for element in elements.values():
                nb_element = element.shape[0]
                element[:, 0] = np.arange(min_indice, min_indice + nb_element)
                min_indice += nb_element

        # Define ElementMat objects
        for elt_type, elt in elements.items():
            element = ElementMat(
                connectivity=elt[:, 1:],
                nb_element=elt.shape[0],
                nb_node_per_element=elt.shape[1] - 1,
                indice=elt[:, 0].astype(np.int32),
            )
            # Add element of reference using names from pyUFF
            if elt_type == "triangle":
                element.ref_element = RefTriangle3()
            elif elt_type == "quad":
                element.ref_element = RefQuad4()
            else:
                raise ValueError(f"Wrong element type {elt_type}.")

            mesh.element_dict[elt_type] = element

        return mesh

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
        super(ImportMeshMat, self).__init__()
        # The class is frozen (in Import init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        ImportMeshMat_str = ""
        # Get the properties inherited from Import
        ImportMeshMat_str += super(ImportMeshMat, self).__str__()
        ImportMeshMat_str += 'file_path = "' + str(self.file_path) + '"' + linesep
        return ImportMeshMat_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Import
        if not super(ImportMeshMat, self).__eq__(other):
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
            super(ImportMeshMat, self).compare(
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
        S += super(ImportMeshMat, self).__sizeof__()
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
        ImportMeshMat_dict = super(ImportMeshMat, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        ImportMeshMat_dict["file_path"] = self.file_path
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        ImportMeshMat_dict["__class__"] = "ImportMeshMat"
        return ImportMeshMat_dict

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
        super(ImportMeshMat, self)._set_None()

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
