# File generated according to Generator/ClassesRef/Mesh/MeshVTK.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Mesh/MeshVTK"""

import os
import shutil
from os import linesep
from os.path import join
from sys import getsizeof
from typing import Literal, Optional

import numpy as np
import pyvista as pv
from meshio import read
from pyleecan.Classes.ElementMat import ElementMat
from pyleecan.Classes.FPGNSeg import FPGNSeg
from pyleecan.Classes.FPGNTri import FPGNTri
from pyleecan.Classes.Mesh import Mesh
from pyleecan.Classes.MeshMat import MeshMat
from pyleecan.Classes.NodeMat import NodeMat
from pyleecan.Classes.RefLine3 import RefLine3
from pyleecan.Classes.RefQuad9 import RefQuad9
from pyleecan.Classes.RefSegmentP1 import RefSegmentP1
from pyleecan.Classes.RefTriangle3 import RefTriangle3
from pyleecan.Classes.ScalarProductL2 import ScalarProductL2
from pyleecan.Classes._check import check_var

from pyleecan.definitions import RESULT_DIR

from pyleecan.Functions.GUI.log_error import log_error
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


try:
    from vtk import vtkPointSet
except ImportError:
    vtkPointSet = ImportError
try:
    from pyvista.core.pointset import PolyData
except ImportError:
    PolyData = ImportError


class MeshVTK(Mesh):
    """Gather the mesh storage format"""

    VERSION = 1

    # cf Methods.Mesh.MeshVTK.convert
    def convert(
        self,
        meshtype: Literal["MeshVTK", "MeshMat"] = "MeshMat",
        scale: float = 1.0,
    ) -> Mesh:
        """Convert this object to another type of Mesh object.

        Parameters
        ----------
        self : MeshVTK
            a MeshVTK object
        meshtype : str
            a type of Mesh object: MeshVTK or MeshMat
        scale : float
            scale factor

            Returns
        -------
        new_mesh : Mesh
            a Mesh object
        """

        if meshtype == "MeshVTK":
            new_mesh = self.copy()
            new_mesh.node.coordinate *= scale
        elif meshtype == "MeshMat":
            # Avoid circular import
            from pyleecan.Classes.MeshMat import MeshMat

            new_mesh = MeshMat(dimension=self.dimension)

            connect_all = self.get_element()[0]
            nodes = np.array(self.get_node_coordinate())
            nb_node = nodes.shape[0]

            new_mesh.node = NodeMat(
                coordinate=scale * nodes,
                nb_node=nb_node,
                indice=np.arange(nb_node),
            )

            min_indice = 0
            for key in connect_all:
                connect = connect_all[key]
                nb_element = connect.shape[0]
                indices = np.arange(min_indice, min_indice + nb_element)
                min_indice += nb_element

                if key == "line":
                    new_mesh.element_dict["line"] = ElementMat(
                        nb_node_per_element=2,
                        connectivity=connect,
                        nb_element=nb_element,
                        indice=indices,
                        gauss_point=FPGNSeg(),
                        ref_element=RefSegmentP1(),
                        scalar_product=ScalarProductL2(),
                    )
                elif key == "line3":
                    new_mesh.element_dict["line3"] = ElementMat(
                        nb_node_per_element=3,
                        connectivity=connect,
                        nb_element=nb_element,
                        indice=indices,
                        ref_element=RefLine3(),
                        gauss_point=None,  # TODO
                    )
                elif key == "triangle3":
                    new_mesh.element_dict["triangle"] = ElementMat(
                        nb_node_per_element=3,
                        connectivity=connect,
                        nb_element=nb_element,
                        indice=indices,
                        gauss_point=FPGNTri(),
                        ref_element=RefTriangle3(),
                        scalar_product=ScalarProductL2(),
                    )
                elif key == "quad9":
                    new_mesh.element_dict["quad9"] = ElementMat(
                        nb_node_per_element=9,
                        connectivity=connect,
                        nb_element=nb_element,
                        indice=indices,
                        ref_element=RefQuad9(),
                    )
        else:
            raise ValueError(
                f"Wrong meshtype value, expected MeshVTK or MeshMat, got {meshtype}."
            )

        return new_mesh

    # cf Methods.Mesh.MeshVTK.get_element
    def get_element(self, indices=None):
        """Return the elements (connectivities).

        Parameters
        ----------
        self : MeshVTK
            a MeshVTK object
        indices : list
            list of the points to extract (optional)

        Returns
        -------
        dict_connectivity: dict[str, ndarray]
            Dict of connectivity with element names as keys
        nb_element: int
            Number of element in the connectivity
        dict_index: dict
            When apply get_element on a MeshMat :
                Dict of the element element_indices for each ElementMat.
            Not use here, because it as any meanings for a MeshVTK

        """
        # Extract mesh
        mesh = self.get_mesh_pv(indices=indices)

        pv_to_str = {
            pv.CellType.TRIANGLE: "triangle",
            pv.CellType.QUAD: "quad",
            pv.CellType.QUADRATIC_EDGE: "line3",
            pv.CellType.BIQUADRATIC_QUAD: "quad9",
        }

        # Initialize the element dictionary with the keys
        elements = {pv_to_str[cell_type]: [] for cell_type in np.unique(mesh.celltypes)}

        # Get the connectivity of each element
        for cell_type, start_offset, end_offset in zip(
            mesh.celltypes, mesh.offset[:-1], mesh.offset[1:]
        ):
            nodes_indice = mesh.cell_connectivity[start_offset:end_offset]
            elements[pv_to_str[cell_type]].append(nodes_indice)

        # Convert a list of 1D-ndarray into a 2D-ndarray
        for key, value in elements.items():
            elements[key] = np.array(value)

        return elements, mesh.n_cells, {}

    # cf Methods.Mesh.MeshVTK.get_element_area
    def get_element_area(self, indices=None):
        """Return the area of the elements on the outer surface.

        Parameters
        ----------
        self : MeshVTK
            a MeshVTK object
        indices : list
            list of the points to extract (optional)

        Returns
        -------
        areas: ndarray
            Area of the elements
        """

        surf = self.get_surf(indices=indices)

        return surf.compute_element_sizes(area=True)["Area"]

    # cf Methods.Mesh.MeshVTK.get_mesh_pv
    def get_mesh_pv(self, indices=None):
        """Return the pyvista mesh object (or submesh).

        Parameters
        ----------
        self : MeshVTK
            a MeshVTK object
        indices : list
            list of the points to extract (optional)

        Returns
        -------
        mesh : pyvista.core.pointset.UnstructuredGrid
            a pyvista UnstructuredGrid object
        """

        # Already available => Return
        if self.mesh is not None:
            # Extract submesh
            if indices is not None:
                mesh = self.mesh
                mesh["mask"] = np.zeros(mesh.points.shape)
                mesh["mask"][indices] = 1
                mesh.set_active_scalars("mask")
                thresh = mesh.threshold(1)
                mesh = thresh
            else:
                mesh = self.mesh
            return mesh

        # Read mesh file
        else:
            if self.format != "vtk" and self.format != "vtu":
                # Write vtk files with meshio
                # in case replace whitespace in point data keys since vtk doesn't like it
                mesh = read(self.get_path(name=self.name, file_format=self.format))
                mesh.point_data = {
                    k.replace(" ", "_"): v for k, v in mesh.point_data.items()
                }
                mesh.write(self.get_path())
                use_this_format = "vtk"
            else:
                use_this_format = self.format

            # Read .vtk file with pyvista
            mesh = pv.read(self.get_path(name=self.name, file_format=use_this_format))

            # Extract submesh
            if indices is not None:
                mesh = mesh.extract_points(indices)

            if self.is_pyvista_mesh:
                self.mesh = mesh

            return mesh

    # cf Methods.Mesh.MeshVTK.get_node_coordinate
    def get_node_coordinate(
        self, indices: Optional[np.typing.ArrayLike] = None
    ) -> np.ndarray:
        """Return the coordinates of the node with provided indices.
        If indices is not specified, returns every node coordinates

        Parameters
        ----------
        indices : Optional[ArrayLike], optional
            Indices of the targeted nodes. If None, return all.

        Returns
        -------
        np.ndarray
            nodes coordinates
        """

        mesh = self.get_mesh_pv(indices=indices)

        return mesh.points

    # cf Methods.Mesh.MeshVTK.get_normals
    def get_normals(self, indices=None, loc="center"):
        """Return the array of the normals coordinates.

        Parameters
        ----------
        self : MeshVTK
            a MeshVTK object
        indices : list
            list of the points to extract (optional)
        loc : str
            localization of the normals ("center" or "point")

        Returns
        -------
        normals: ndarray
            Normals coordinates
        """

        # Get surfaces
        surf = self.get_surf()

        if loc == "center":
            normals = surf.cell_normals

        elif loc == "point":
            if self.node_normals is None:
                self.surf.compute_normals(
                    cell_normals=False, point_normals=True, inplace=True
                )

                self.node_normals = self.surf["Normals"]

            normals = self.node_normals

        if indices is None:
            return normals

        else:
            return normals[indices, :]

    # cf Methods.Mesh.MeshVTK.get_path
    def get_path(self, name=None, file_format="vtk"):
        """return the path to the file to save the mesh

        Parameters
        ----------
        self : MeshVTK
            MeshVTK Object
        name : str
            Name of the file to use (None: use self.name)
        file_format : str
            extension of the file to use

        Returns
        -------
        path : str
            Full path to the mesh file
        """

        if self.path is None:
            self.path = RESULT_DIR

        if name is None:
            filename = self.name + "." + file_format
        else:
            filename = name + "." + file_format

        return join(self.path, filename).replace("\\", "/")

    # cf Methods.Mesh.MeshVTK.get_surf
    def get_surf(self, indices=None):
        """Return the surf object if it was already extracted, or extracts it from the mesh.

        Parameters
        ----------
        self : MeshVTK
            a MeshVTK object
        indices : list
            list of the points to extract (optional)

        Returns
        -------
        surf : pyvista.core.pointset.PolyData
            a pyvista polydata object
        """

        # Already available => Return
        if self.surf is not None:
            # Extract subsurface
            if indices is not None:
                surf = self.surf.extract_geometry(indices)
            else:
                surf = self.surf
            return surf

        # Extract the outer surface of the mesh
        else:
            mesh = self.get_mesh_pv(indices=indices)
            surf = mesh.extract_geometry()

            if self.is_vtk_surf:
                surf.save(self.surf_path + "/" + self.surf_name + ".vtk")

            self.surf = surf

            return surf

    # cf Methods.Mesh.MeshVTK.perm_coord
    def perm_coord(
        self,
        perm_coord_list=[0, 1, 2],
        path_meshVTK=None,
    ):
        """Returns the current MeshVTK object with permuted coordinates

        Parameters
        ----------
        self : MeshVTK
            a MeshVTK object
        perm_coord_list : list
            list of the coordinates to be permuted
        path_meshVTK : str
            full path to the MeshVTK file

        Returns
        -------
        mesh: MeshVTK
            The MeshVTK object with permuted coordinates

        """
        # convert into MeshMat object
        mesh_mat = self.convert(meshtype="MeshMat", scale=1)

        # extract nodes en elements
        mesh_mat_node = mesh_mat.get_node_coordinate()
        mesh_mat_element = mesh_mat.get_element()

        # swap axis
        mesh_mat_node = mesh_mat_node.T[perm_coord_list].T

        # create new object
        # 1. create NodeMat
        nb_node = len(mesh_mat_node)
        nodemat = NodeMat(coordinate=mesh_mat_node, nb_node=nb_node)

        # 2. create ElementMat
        elementMatDict = dict()

        for key in mesh_mat_element[0]:
            element_mat = ElementMat(
                connectivity=mesh_mat_element[0][key],
                nb_element=len(mesh_mat_element[0][key]),
            )
            elementMatDict[key] = element_mat

        # 3. create MeshMat
        meshmat = MeshMat(element_dict=elementMatDict, node=nodemat)

        # convert and save into vtk
        mesh_pv = meshmat.get_mesh_pv()
        if path_meshVTK is not None:
            mesh_pv.save(path_meshVTK)
        elif self.path is not None:
            mesh_pv.save(self.path + "/" + self.name + ".vtk")

        self.mesh = mesh_pv

        return self

    # cf Methods.Mesh.MeshVTK.save_vtk
    def save_vtk(self, save_path):
        """Copy file vtk use for object meshVTK into path give by save_path

        Parameters
        ----------
        self : MeshVTK
            an MeshVTK object
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None

        """
        # Check if extension file is .vtk
        save_path_L = save_path.split(".")
        if len(save_path_L) == 1:
            save_path = f"{save_path_L[0]}.vtk"
        else:
            if save_path_L[-1] != "vtk":
                err_msg = f"Error save path extension is not .vtk"
                log_error(
                    self,
                    err_msg,
                    self.get_logger(),
                    is_popup=False,
                    is_warning=False,
                )

        # Check if save_path exist
        save_path_2 = os.path.dirname(save_path)

        if not os.path.isdir(save_path_2):
            raise Exception(
                f"Error while saving mesh to vtk, save path doesn't exist: {save_path}"
            )

        shutil.copy(self.path, save_path)

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        mesh=None,
        is_pyvista_mesh=False,
        format="vtk",
        path=None,
        name="mesh",
        surf=None,
        is_vtk_surf=False,
        surf_path="",
        surf_name="",
        node_normals=None,
        dimension=2,
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
            if "mesh" in list(init_dict.keys()):
                mesh = init_dict["mesh"]
            if "is_pyvista_mesh" in list(init_dict.keys()):
                is_pyvista_mesh = init_dict["is_pyvista_mesh"]
            if "format" in list(init_dict.keys()):
                format = init_dict["format"]
            if "path" in list(init_dict.keys()):
                path = init_dict["path"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "surf" in list(init_dict.keys()):
                surf = init_dict["surf"]
            if "is_vtk_surf" in list(init_dict.keys()):
                is_vtk_surf = init_dict["is_vtk_surf"]
            if "surf_path" in list(init_dict.keys()):
                surf_path = init_dict["surf_path"]
            if "surf_name" in list(init_dict.keys()):
                surf_name = init_dict["surf_name"]
            if "node_normals" in list(init_dict.keys()):
                node_normals = init_dict["node_normals"]
            if "dimension" in list(init_dict.keys()):
                dimension = init_dict["dimension"]
        # Set the properties (value check and convertion are done in setter)
        self.mesh = mesh
        self.is_pyvista_mesh = is_pyvista_mesh
        self.format = format
        self.path = path
        self.name = name
        self.surf = surf
        self.is_vtk_surf = is_vtk_surf
        self.surf_path = surf_path
        self.surf_name = surf_name
        self.node_normals = node_normals
        # Call Mesh init
        super(MeshVTK, self).__init__(dimension=dimension)
        # The class is frozen (in Mesh init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        MeshVTK_str = ""
        # Get the properties inherited from Mesh
        MeshVTK_str += super(MeshVTK, self).__str__()
        MeshVTK_str += "mesh = " + str(self.mesh) + linesep + linesep
        MeshVTK_str += "is_pyvista_mesh = " + str(self.is_pyvista_mesh) + linesep
        MeshVTK_str += 'format = "' + str(self.format) + '"' + linesep
        MeshVTK_str += 'path = "' + str(self.path) + '"' + linesep
        MeshVTK_str += 'name = "' + str(self.name) + '"' + linesep
        MeshVTK_str += "surf = " + str(self.surf) + linesep + linesep
        MeshVTK_str += "is_vtk_surf = " + str(self.is_vtk_surf) + linesep
        MeshVTK_str += 'surf_path = "' + str(self.surf_path) + '"' + linesep
        MeshVTK_str += 'surf_name = "' + str(self.surf_name) + '"' + linesep
        MeshVTK_str += (
            "node_normals = "
            + linesep
            + str(self.node_normals).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        return MeshVTK_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Mesh
        if not super(MeshVTK, self).__eq__(other):
            return False
        if other.mesh != self.mesh:
            return False
        if other.is_pyvista_mesh != self.is_pyvista_mesh:
            return False
        if other.format != self.format:
            return False
        if other.path != self.path:
            return False
        if other.name != self.name:
            return False
        if other.surf != self.surf:
            return False
        if other.is_vtk_surf != self.is_vtk_surf:
            return False
        if other.surf_path != self.surf_path:
            return False
        if other.surf_name != self.surf_name:
            return False
        if not np.array_equal(other.node_normals, self.node_normals):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Mesh
        diff_list.extend(
            super(MeshVTK, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.mesh is None and self.mesh is not None) or (
            other.mesh is not None and self.mesh is None
        ):
            diff_list.append(name + ".mesh None mismatch")
        elif self.mesh is not None and self.mesh != other.mesh:
            diff_list.append(name + ".mesh")
        if other._is_pyvista_mesh != self._is_pyvista_mesh:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_pyvista_mesh)
                    + ", other="
                    + str(other._is_pyvista_mesh)
                    + ")"
                )
                diff_list.append(name + ".is_pyvista_mesh" + val_str)
            else:
                diff_list.append(name + ".is_pyvista_mesh")
        if other._format != self._format:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._format)
                    + ", other="
                    + str(other._format)
                    + ")"
                )
                diff_list.append(name + ".format" + val_str)
            else:
                diff_list.append(name + ".format")
        if other._path != self._path:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._path) + ", other=" + str(other._path) + ")"
                )
                diff_list.append(name + ".path" + val_str)
            else:
                diff_list.append(name + ".path")
        if other._name != self._name:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._name) + ", other=" + str(other._name) + ")"
                )
                diff_list.append(name + ".name" + val_str)
            else:
                diff_list.append(name + ".name")
        if (other.surf is None and self.surf is not None) or (
            other.surf is not None and self.surf is None
        ):
            diff_list.append(name + ".surf None mismatch")
        elif self.surf is not None and self.surf != other.surf:
            diff_list.append(name + ".surf")
        if other._is_vtk_surf != self._is_vtk_surf:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_vtk_surf)
                    + ", other="
                    + str(other._is_vtk_surf)
                    + ")"
                )
                diff_list.append(name + ".is_vtk_surf" + val_str)
            else:
                diff_list.append(name + ".is_vtk_surf")
        if other._surf_path != self._surf_path:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._surf_path)
                    + ", other="
                    + str(other._surf_path)
                    + ")"
                )
                diff_list.append(name + ".surf_path" + val_str)
            else:
                diff_list.append(name + ".surf_path")
        if other._surf_name != self._surf_name:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._surf_name)
                    + ", other="
                    + str(other._surf_name)
                    + ")"
                )
                diff_list.append(name + ".surf_name" + val_str)
            else:
                diff_list.append(name + ".surf_name")
        if not np.array_equal(other.node_normals, self.node_normals):
            diff_list.append(name + ".node_normals")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Mesh
        S += super(MeshVTK, self).__sizeof__()
        S += getsizeof(self.mesh)
        S += getsizeof(self.is_pyvista_mesh)
        S += getsizeof(self.format)
        S += getsizeof(self.path)
        S += getsizeof(self.name)
        S += getsizeof(self.surf)
        S += getsizeof(self.is_vtk_surf)
        S += getsizeof(self.surf_path)
        S += getsizeof(self.surf_name)
        S += getsizeof(self.node_normals)
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

        # Get the properties inherited from Mesh
        MeshVTK_dict = super(MeshVTK, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        MeshVTK_dict["mesh"] = None
        MeshVTK_dict["is_pyvista_mesh"] = self.is_pyvista_mesh
        MeshVTK_dict["format"] = self.format
        MeshVTK_dict["path"] = self.path
        MeshVTK_dict["name"] = self.name
        MeshVTK_dict["surf"] = None
        MeshVTK_dict["is_vtk_surf"] = self.is_vtk_surf
        MeshVTK_dict["surf_path"] = self.surf_path
        MeshVTK_dict["surf_name"] = self.surf_name
        if self.node_normals is None:
            MeshVTK_dict["node_normals"] = None
        else:
            if type_handle_ndarray == 0:
                MeshVTK_dict["node_normals"] = self.node_normals.tolist()
            elif type_handle_ndarray == 1:
                MeshVTK_dict["node_normals"] = self.node_normals.copy()
            elif type_handle_ndarray == 2:
                MeshVTK_dict["node_normals"] = self.node_normals
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        MeshVTK_dict["__class__"] = "MeshVTK"
        return MeshVTK_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        mesh_val = None
        is_pyvista_mesh_val = self.is_pyvista_mesh
        format_val = self.format
        path_val = self.path
        name_val = self.name
        surf_val = None
        is_vtk_surf_val = self.is_vtk_surf
        surf_path_val = self.surf_path
        surf_name_val = self.surf_name
        if self.node_normals is None:
            node_normals_val = None
        else:
            node_normals_val = self.node_normals.copy()
        dimension_val = self.dimension
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            mesh=mesh_val,
            is_pyvista_mesh=is_pyvista_mesh_val,
            format=format_val,
            path=path_val,
            name=name_val,
            surf=surf_val,
            is_vtk_surf=is_vtk_surf_val,
            surf_path=surf_path_val,
            surf_name=surf_name_val,
            node_normals=node_normals_val,
            dimension=dimension_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.mesh = None
        self.is_pyvista_mesh = None
        self.format = None
        self.path = None
        self.name = None
        self.surf = None
        self.is_vtk_surf = None
        self.surf_path = None
        self.surf_name = None
        self.node_normals = None
        # Set to None the properties inherited from Mesh
        super(MeshVTK, self)._set_None()

    def _get_mesh(self):
        """getter of mesh"""
        return self._mesh

    def _set_mesh(self, value):
        """setter of mesh"""
        if value == -1:
            value = vtkPointSet()
        check_var("mesh", value, "vtkPointSet")
        self._mesh = value

    mesh = property(
        fget=_get_mesh,
        fset=_set_mesh,
        doc="""Pyvista object of the mesh (optional)

        :Type: vtk.vtkPointSet
        """,
    )

    def _get_is_pyvista_mesh(self):
        """getter of is_pyvista_mesh"""
        return self._is_pyvista_mesh

    def _set_is_pyvista_mesh(self, value):
        """setter of is_pyvista_mesh"""
        check_var("is_pyvista_mesh", value, "bool")
        self._is_pyvista_mesh = value

    is_pyvista_mesh = property(
        fget=_get_is_pyvista_mesh,
        fset=_set_is_pyvista_mesh,
        doc="""Store the pyvista object

        :Type: bool
        """,
    )

    def _get_format(self):
        """getter of format"""
        return self._format

    def _set_format(self, value):
        """setter of format"""
        check_var("format", value, "str")
        self._format = value

    format = property(
        fget=_get_format,
        fset=_set_format,
        doc="""Format in which the mesh is stored

        :Type: str
        """,
    )

    def _get_path(self):
        """getter of path"""
        return self._path

    def _set_path(self, value):
        """setter of path"""
        check_var("path", value, "str")
        self._path = value

    path = property(
        fget=_get_path,
        fset=_set_path,
        doc="""Path where the mesh is stored

        :Type: str
        """,
    )

    def _get_name(self):
        """getter of name"""
        return self._name

    def _set_name(self, value):
        """setter of name"""
        check_var("name", value, "str")
        self._name = value

    name = property(
        fget=_get_name,
        fset=_set_name,
        doc="""Name of the mesh file

        :Type: str
        """,
    )

    def _get_surf(self):
        """getter of surf"""
        return self._surf

    def _set_surf(self, value):
        """setter of surf"""
        if value == -1:
            value = PolyData()
        check_var("surf", value, "PolyData")
        self._surf = value

    surf = property(
        fget=_get_surf,
        fset=_set_surf,
        doc="""Pyvista object of the outer surface

        :Type: pyvista.core.pointset.PolyData
        """,
    )

    def _get_is_vtk_surf(self):
        """getter of is_vtk_surf"""
        return self._is_vtk_surf

    def _set_is_vtk_surf(self, value):
        """setter of is_vtk_surf"""
        check_var("is_vtk_surf", value, "bool")
        self._is_vtk_surf = value

    is_vtk_surf = property(
        fget=_get_is_vtk_surf,
        fset=_set_is_vtk_surf,
        doc="""Save the surface mesh in a vtk file

        :Type: bool
        """,
    )

    def _get_surf_path(self):
        """getter of surf_path"""
        return self._surf_path

    def _set_surf_path(self, value):
        """setter of surf_path"""
        check_var("surf_path", value, "str")
        self._surf_path = value

    surf_path = property(
        fget=_get_surf_path,
        fset=_set_surf_path,
        doc="""Path where the outer surface is stored

        :Type: str
        """,
    )

    def _get_surf_name(self):
        """getter of surf_name"""
        return self._surf_name

    def _set_surf_name(self, value):
        """setter of surf_name"""
        check_var("surf_name", value, "str")
        self._surf_name = value

    surf_name = property(
        fget=_get_surf_name,
        fset=_set_surf_name,
        doc="""Name of the outer surface file

        :Type: str
        """,
    )

    def _get_node_normals(self):
        """getter of node_normals"""
        return self._node_normals

    def _set_node_normals(self, value):
        """setter of node_normals"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("node_normals", value, "ndarray")
        self._node_normals = value

    node_normals = property(
        fget=_get_node_normals,
        fset=_set_node_normals,
        doc="""Array of normals to nodes (element vertices)

        :Type: ndarray
        """,
    )
