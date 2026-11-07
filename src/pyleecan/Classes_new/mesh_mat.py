# Experimental dataclass generated from Generator/ClassesRef/Mesh/MeshMat.csv
"""Generated experimental dataclass; do not edit by hand."""

import copy
import os
from dataclasses import dataclass
from itertools import repeat
from typing import Dict, List, Literal, Optional, Tuple, Union

import meshio
import numpy as np
import pyvista as pv

from ..definitions import RESULT_DIR
from ..Functions.GUI.log_error import log_error
from .element_mat import ElementMat
from .fpgn_seg import FPGNSeg
from .mesh import Mesh
from .node_mat import NodeMat
from .ref_quad_4 import RefQuad4
from .ref_quad_9 import RefQuad9
from .ref_segment_p_1 import RefSegmentP1
from .ref_triangle_3 import RefTriangle3
from .ref_triangle_6 import RefTriangle6


@dataclass(eq=False)
class MeshMat(Mesh):
    """Gather the mesh storage format

    Attributes
    ----------
    element_dict : {ElementMat} or None
        Storing connectivity
        Default: None
    node : NodeMat or None
        Storing nodes
        Default: None
    _is_renum : bool
        True if renumering the nodes and elements is useful when renum method is called (saving calculation time)
        Default: False
    sym : int
        Spatial symmetry factor
        Default: 1
    is_antiper_a : bool
        True if there is a spatial antiperiod
        Default: False
    """

    element_dict: dict[str, ElementMat] | None = None
    """Storing connectivity"""
    node: NodeMat | None = None
    """Storing nodes"""
    _is_renum: bool = False
    """True if renumering the nodes and elements is useful when renum method is called (saving calculation time)"""
    sym: int = 1
    """Spatial symmetry factor"""
    is_antiper_a: bool = False
    """True if there is a spatial antiperiod"""

    # Inlined from Methods.Mesh.MeshMat.add_element
    def add_element(
        self, node_indices: np.typing.ArrayLike, element_type: str
    ) -> Union[int, None]:
        """Add a new element defined by node indices and element type.

        Parameters
        ----------
        self : MeshMat
            a MeshMat object
        node_indices : ndarray or list of int
            a ndarray of nodes indices (length must match element.nb_node_per_element)
        element_type : str
            Define the type of element to add (key of self.element_dict)

        Returns
        -------
        new_index : int
            indice of the newly created element. None if the element already exists.
        """

        # The element index must be unique for all element type
        new_index = self.get_element_nb()  # index start at 0 (last index = nb-1)

        is_created = self.element_dict[element_type].add_element(
            node_indices, new_index
        )

        if is_created:
            return new_index
        else:
            return None

    # Inlined from Methods.Mesh.MeshMat.clear_element
    def clear_element(self):
        """Remove non-used elements based on node indices.

        Parameters
        ----------
        self : MeshMat
            an Mesh object

        Returns
        -------

        """

        # TODO
        raise NotImplementedError("The clear_element method is not yet implemented")

    # Inlined from Methods.Mesh.MeshMat.clear_node
    def clear_node(self):
        """Remove non-used nodes based on elements connectivity.

        Parameters
        ----------
        self : MeshMat
            an Mesh object

        Returns
        -------

        """

        coord_init = self.get_node_coordinate()
        node_indice_init = self.get_node_indice()
        connect_dict, *_ = self.get_element()

        # Extract index of use nodes in elements
        node_indice = np.unique(
            [np.unique(connectivity) for connectivity in connect_dict.values()]
        )

        common, _, index2 = np.intersect1d(
            node_indice, node_indice_init, return_indices=True
        )

        if not np.array_equal(node_indice, common):
            raise ValueError("")

        self.node = NodeMat(
            coordinate=coord_init[index2, :],
            nb_node=len(index2),
            indice=node_indice,
        )

    # Inlined from Methods.Mesh.MeshMat.convert
    def convert(
        self,
        meshtype: Literal["MeshVTK", "MeshMat"] = "MeshMat",
        scale: float = 1.0,
    ) -> Mesh:
        """Convert the MeshMat to another type of Mesh object.

        Parameters
        ----------
        self : MeshMat
            a MeshMat object
        meshtype : str
            a type of Mesh object: MeshVTK or MeshMat
        scale : float
            scale factor

            Returns
        -------
        Mesh
            a Mesh object
        """

        if meshtype not in ["MeshMat", "MeshVTK"]:
            raise ValueError(
                f'Wrong meshtype value "{meshtype}", expected value: {", ".join(["MeshMat", "MeshVTK"])}.'
            )

        if meshtype == "MeshMat":
            new_mesh = self.copy()
            new_mesh.node.coordinate *= scale
            return new_mesh

        # Avoiding circular import
        from .mesh_vtk import MeshVTK

        elements_ = []
        element_types = []

        # Map between pyleecan and pyvista element type
        element_types_dict = {
            RefTriangle3: pv.CellType.TRIANGLE,
            RefTriangle6: pv.CellType.QUADRATIC_TRIANGLE,
            RefQuad4: pv.CellType.QUAD,
            RefQuad9: pv.CellType.QUADRATIC_QUAD,
        }

        # Construct the element connectivity and element type vector to create the pyvista unstructured grid
        # https://docs.pyvista.org/version/stable/examples/00-load/create-unstructured-surface.html#creating-an-unstructured-grid
        for element in self.element_dict.values():
            connectivity = element.connectivity
            nb_element = connectivity.shape[0]
            element_types.extend(
                list(
                    repeat(
                        element_types_dict[type(element.ref_element)],
                        nb_element,
                    )
                )
            )

            elements_.append(
                np.hstack(
                    [
                        connectivity.shape[1]
                        * np.ones((nb_element, 1), dtype=np.int32),
                        connectivity,
                    ]
                )
                .flatten()
                .astype(np.int32)
            )

        elements = np.hstack(elements_).astype(np.int32)

        pv_mesh = pv.UnstructuredGrid(
            elements, element_types, self.node.coordinate * scale
        )
        mesh_vtk = MeshVTK(mesh=pv_mesh, is_pyvista_mesh=True)

        return mesh_vtk

    # Inlined from Methods.Mesh.MeshMat.find_element
    def find_element(self, points, normal_t=None):
        """Return the elements containing the target point(s)

        Parameters
        ----------
        self : MeshMat
            an MeshMat object
        points : ndarray
            2D array containing the coordinates of the target point(s)
        normal_t normal direction to the target element

        Returns
        -------
        element_list: list
            A list of selected elements

        """

        if points.ndim != 2:
            raise ValueError(
                "points must have two dimensions, namely the number of points and the points coordinates."
            )

        # nmax_search = 3
        element_list = []
        element_prop_list = []

        nodes = self.node
        point_coord = nodes.coordinate
        nb_mesh_point = nodes.nb_node

        for point in points:
            # Find the closest node to the given point
            point_rep = np.tile(
                point[: self.dimension], (nb_mesh_point, 1)
            )  # /!\ if the mesh is in 2D, exclude z coordinate
            dist_node = np.linalg.norm(point_coord - point_rep, axis=1, keepdims=True)
            idx_closest_node = dist_node.argmin(axis=0)

            for key in self.element_dict:
                elements = self.element_dict[key]
                ref_element = elements.ref_element
                connect = elements.connectivity

                # All selected nodes from the closest to the farthest are tested
                # get elements that contain the closest node and test if point is inside
                idx_closest_elements = np.nonzero(connect == idx_closest_node)[0]
                nb_closest_elem = len(idx_closest_elements)
                a, b = np.zeros(nb_closest_elem), np.zeros(nb_closest_elem)
                element_idx = []
                element_prop = []
                for k, idx_closest_elem in enumerate(idx_closest_elements):
                    vert = self.get_element_coordinate(
                        idx_closest_elem, element_name=key
                    )[key]
                    (is_inside, a[k], b[k]) = ref_element.is_inside(
                        vert, point[: self.dimension], normal_t
                    )
                    if is_inside:
                        # dontstop = False
                        element_prop.append(key)
                        element_idx.append(idx_closest_elem)

                # if no element was found, give it a second try
                # TODO first check if outside mesh
                if len(element_prop) == 0:
                    # test all elements (sorted by center, i.e. mean of element vertices coordinate)
                    element_center = point_coord[connect].mean(axis=1)

                    dist_element_cent = np.linalg.norm(
                        element_center - point[np.newaxis], axis=1, keepdims=True
                    )

                    idx_sorted_dist = np.argsort(dist_element_cent, axis=0)[:, 0]
                    for i in range(elements.nb_element):
                        vert = self.get_element_coordinate(idx_sorted_dist[i])[key]
                        is_inside, a, *_ = ref_element.is_inside(
                            vert, point[: self.dimension], normal_t
                        )
                        if is_inside:
                            element_prop = [key]
                            element_idx = [idx_sorted_dist[i]]
                            break

                # No element contain the point atleast (only possible if point is outside mesh)
                if len(element_prop) == 0:
                    element_prop_list.append(None)
                    element_list.append(None)

                # one element found
                elif len(element_prop) == 1:
                    element_prop_list.extend(element_prop)
                    element_list.extend(element_idx)
                # more than one elements found -> find the closest element
                elif len(element_prop) > 1:
                    index = np.nonzero(np.min(a) == a)[0]
                    if len(index > 1):
                        logger = self.get_logger()
                        logger.warning(
                            f"The target point {point} belongs to more than one element, it may be on an edge. The method returns only one element."
                        )

                    element_prop_list.append(element_prop[index[0]])
                    element_list.append(element_idx[index[0]])

        return element_prop_list, element_list

    # Inlined from Methods.Mesh.MeshMat.get_element
    def get_element(
        self,
        element_indices: Optional[Union[int, List[int]]] = None,
        element_name: Union[List[str], str] = [],
    ) -> Tuple[Dict[str, np.ndarray], int, Dict[str, np.ndarray]]:
        """Return the connectivity for one selected element

        Parameters
        ----------
        self : MeshMat
            an MeshMat object
        element_indices: list
            list of element index. If None, return all.
        element_name : list
            list of element names to extract the connectivity. If None, return every element_names

        Returns
        -------
        dict_connectivity: dict[str, ndarray]
            Dict of connectivity with element names as keys
        nb_element: int
            Number of element in the connectivity
        dict_index: dict
            Dict of the element element_indices for each ElementMat
        """

        if isinstance(element_indices, (int, np.integer)):
            element_indices = (element_indices,)

        element_name = self._check_element_name(
            element_mat_dict=self.element_dict, element_name=element_name
        )

        dict_connectivity = {}
        dict_index = {}
        nb_element = 0
        # Extract full connectivity matrix and element element_indices
        if element_indices is None:
            for key in element_name:
                element = self.element_dict[key]
                dict_connectivity[key] = element.get_connectivity()
                dict_index[key] = element.indice
                nb_element += element.nb_element

        # Extract element connectivity and index for each element
        else:
            for key in element_name:
                element = self.element_dict[key]
                list_connectivity = [
                    element.get_connectivity(index) for index in element_indices
                ]
                # Extract connectivity if the element index is present
                dict_connectivity[key] = np.array(
                    [
                        connectivity
                        for connectivity in list_connectivity
                        if connectivity.size
                    ]
                ).squeeze()

                # Extract index if the element index is present
                dict_index[key] = [
                    index
                    for index, connectivity in zip(element_indices, list_connectivity)
                    if connectivity.size
                ]

        return dict_connectivity, nb_element, dict_index

    @staticmethod
    def _check_element_name(
        element_mat_dict: Dict[str, ElementMat], element_name: Union[List[str], str]
    ) -> List[str]:
        """Check if the element names provided are in the element dictionnary

        Parameters
        ----------
        element_mat_dict : Dict[str, ElementMat]
            Dict of elements
        element_name : Union[List[str], str]
            name of elements

        Returns
        -------
        List[str]
            Name of elements processed

        Raises
        ------
        ValueError
            A provided name is not in the dictionnary
        """
        if isinstance(element_name, str):
            element_name = [element_name]
        elif len(element_name) == 0:
            return list(element_mat_dict.keys())

        all_element_names = element_mat_dict.keys()
        for elem_name in element_name:
            if elem_name not in all_element_names:
                raise ValueError(
                    f'Wrong element_name value, "{elem_name}" not in {list(all_element_names)}'
                )
        return element_name

    # Inlined from Methods.Mesh.MeshMat.get_element_area
    def get_element_area(
        self,
        element_indices: Optional[List[int]] = None,
        element_name: Union[List[str], str] = [],
    ) -> np.ndarray:
        """
        Return the area of the elements on the outer surface.
        #TODO address multiple element type issue, i.e. distracted indices
        Parameters
        ----------
        self : MeshMat
            a MeshMat object
        element_indices : list
            list of the element indices to extract (optional)
        element_name : list | str
            Name(s) of the element to extract
        Returns
        -------
        areas: ndarray
            Area of the elements
        """
        logger = self.get_logger()
        area = []

        element_name = self._check_element_name(
            element_mat_dict=self.element_dict, element_name=element_name
        )

        element_coordinate_dict = self.get_element_coordinate(
            element_indices=element_indices, element_name=element_name
        )

        for element_name, element_coordinate in element_coordinate_dict.items():
            if len(element_coordinate) != 0:
                try:
                    A = self.element_dict[element_name].ref_element.get_element_area(
                        element_coordinate
                    )

                except AttributeError, NotImplementedError:
                    logger.warning(
                        (
                            f'MeshMat: Reference element for "{element_name}" of type "{type(self.element_dict[element_name])}" not found. ',
                            "Respective area set to zero.",
                        )
                    )
                    A = repeat(0, element_coordinate.shape[0])

                area.extend(A)

        return np.array(area)

    # Inlined from Methods.Mesh.MeshMat.get_element_coordinate
    def get_element_coordinate(
        self,
        element_indices: Optional[List[int]] = None,
        element_name: Union[List[str], str] = [],
    ) -> Dict[str, np.ndarray]:
        """Return a connectivity matrix where the nodes indices are replaced by their coordinates.

        Parameters
        ----------
        self : MeshMat
            an MeshMat object
        element_indices : list
            list of the element indices to extract (optional)
        element_name : list | str
            One or several element names to be returned

        Returns
        -------
        node_coordinates: Dict[str, ndarray]
            Nodes coordinates of each selected element

        """

        element_name = self._check_element_name(
            element_mat_dict=self.element_dict, element_name=element_name
        )

        element_connectivity_dict, *_ = self.get_element(
            element_indices=element_indices, element_name=element_name
        )
        node_coordinates = {}
        for key, connectivity in element_connectivity_dict.items():
            if connectivity.ndim > 1:
                node_coordinates[key] = np.array(
                    [self.get_node_coordinate(nodes) for nodes in connectivity]
                )
            else:
                node_coordinates[key] = self.get_node_coordinate(connectivity)

        return node_coordinates

    # Inlined from Methods.Mesh.MeshMat.get_element_nb
    # -*- coding: utf-8 -*-
    def get_element_nb(self) -> int:
        """Return the total number of element of all kind

        Parameters
        ----------
        self : MeshMat
            A MeshMat object

        Returns
        -------
        nb_element : int
            total number of element of all kind
        """

        nb_element = sum([element.nb_element for element in self.element_dict.values()])

        return nb_element

    # Inlined from Methods.Mesh.MeshMat.get_mesh_pv
    def get_mesh_pv(
        self, path: str = f"{RESULT_DIR}/temp.vtk", indices: Optional[List[int]] = None
    ) -> pv.core.pointset.UnstructuredGrid:
        """Return the pyvista mesh object (or submesh).

        Parameters
        ----------
        self : MeshMat
            a MeshMat object
        indices : list
            list of the nodes to extract (optional)

        Returns
        -------
        mesh : pyvista.core.pointset.UnstructuredGrid
            a pyvista UnstructuredGrid object
        """

        # Numbering and indices compatible with pyvista
        mesh_renum = self.copy()
        mesh_renum.renum()

        nodes = mesh_renum.get_node_coordinate()
        cells, _, _ = mesh_renum.get_element()

        cells_meshio = []
        for key in cells:
            cells_meshio.append((key, cells[key]))
            # Write .vtk file using meshio

        # Make sure that the file exists
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        meshio.write_points_cells(filename=path, points=nodes, cells=cells_meshio)

        # Read .vtk file with pyvista
        mesh = pv.read(path)

        # Extract submesh
        if indices is not None:
            mesh = mesh.extract_points(indices)

        os.remove(path)

        return mesh

    # Inlined from Methods.Mesh.MeshMat.get_node2element
    def get_node2element(self, node_indice: int) -> np.ndarray:
        """Return all element indices of elements containing a node.

        Parameters
        ----------
        self : MeshMat
            an MeshMat object
        node_indice : int
            a node indice

        Returns
        -------
        element_indices: ndarray
            Indices of elements containing the node

        """
        element_indices = np.concatenate(
            [
                element.get_node2element(node_indice)
                for element in self.element_dict.values()
            ]
        )

        return element_indices

    # Inlined from Methods.Mesh.MeshMat.get_node_coordinate
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
        if indices is None:
            return self.node.coordinate
        else:
            return self.node.get_coord(indices)

    # Inlined from Methods.Mesh.MeshMat.get_node_indice
    def get_node_indice(
        self, coordinates: Optional[np.typing.ArrayLike] = None
    ) -> np.typing.ArrayLike:
        """Return a matrix of nodes coordinates.

        Parameters
        ----------
        self : Mesh
            an Mesh object
        coordinates: ndarray
            nodes coordinates

        Returns
        -------
        indices : ndarray
            nodes indices

        """

        if coordinates is None:
            return self.node.get_indice()
        else:
            raise NotImplementedError("Providing coordinates is not supported yet.")

    # Inlined from Methods.Mesh.MeshMat.interface
    def interface(self, other_mesh: "MeshMat") -> "MeshMat":
        """Define a MeshMat object corresponding to the exact intersection between two meshes (nodes must be in both meshes).

        Parameters
        ----------
        self : MeshMat
            a Mesh object
        other_mesh : Mesh
            an other Mesh object

            Returns
        -------
        """

        # Dynamic import
        new_mesh = self.copy()
        new_mesh._is_renum = True

        new_mesh.element_dict = {
            "line": ElementMat(
                nb_node_per_element=2, gauss_point=FPGNSeg(), ref_element=RefSegmentP1()
            )
        }

        for key in self.element_dict:
            # Developer info: IDK if this code works with other than triangle elements. To be checked.
            if self.element_dict[key].nb_node_per_element == 3:  # Triangle case
                connect = self.element_dict[key].get_connectivity()
                connect2 = other_mesh.element_dict[key].get_connectivity()

                nb_elem_mesh1 = self.element_dict[key].nb_node_per_element
                nb_elem_mesh2 = other_mesh.element_dict[key].nb_node_per_element

                nodes_tags = np.unique(connect)
                other_nodes_tags = np.unique(connect2)

                # Find the nodes on the interface (they are in both in and out)
                interface_nodes_tags = np.intersect1d(nodes_tags, other_nodes_tags)

                # Extract elements which may belong to the interface
                is_interface_node_mesh1 = np.isin(connect, interface_nodes_tags)
                is_interface_node_mesh2 = np.isin(connect2, interface_nodes_tags)
                idx_elem_mesh1 = np.nonzero(is_interface_node_mesh1.sum(axis=1) >= 2)
                idx_elem_mesh2 = np.nonzero(is_interface_node_mesh2.sum(axis=1) >= 2)

                element_mesh1 = connect[idx_elem_mesh1]
                element_mesh2 = connect2[idx_elem_mesh2]

                # Compute the edges connectivity of the selected elements by extracting
                # (node[0],node[1]), (node[1],node[2]), ..., (node[-2],node[-1]), (node[-1], node[0])
                line_connect_mesh1 = np.vstack(
                    [
                        *[
                            element_mesh1[:, k : k + 2]
                            for k in range(nb_elem_mesh1 - 1)
                        ],
                        element_mesh1[:, (-1, 0)],
                    ]
                )
                line_connect_mesh2 = np.vstack(
                    [
                        *[
                            element_mesh2[:, k : k + 2]
                            for k in range(nb_elem_mesh2 - 1)
                        ],
                        element_mesh2[:, (-1, 0)],
                    ]
                )

                # Iterate on mesh1 lines to check if the edge is also in mesh2
                for line in line_connect_mesh1:
                    if np.any(np.all(np.isin(line_connect_mesh2, line), axis=1)):
                        new_mesh.add_element(line, "line")

        return new_mesh

    # Inlined from Methods.Mesh.MeshMat.renum
    def renum(self):
        """Restart point indices from 0, and update connectivity. Indices of elements stay the same.

        Parameters
        ----------
        self : MeshMat
            an Mesh object
        """

        if self._is_renum:
            coord_init = self.get_node_coordinate()
            node_indice = self.get_node_indice()
            connect_dict, *_ = self.get_element()

            if max(node_indice) != len(node_indice) - 1:
                connect_dict, *_ = self.get_element()

                nb_node_new = len(node_indice)
                node_indice_new = np.linspace(
                    0, nb_node_new - 1, nb_node_new, dtype=int
                )
                connect_dict_new = copy.deepcopy(connect_dict)
                for inode in range(nb_node_new):
                    for key in connect_dict:
                        connect_dict_new[key][
                            connect_dict[key] == node_indice[inode]
                        ] = node_indice_new[inode]

                self.node.indice = node_indice_new

                for key in connect_dict:
                    self.element_dict[key] = ElementMat(
                        connectivity=connect_dict_new[key],
                        nb_element=len(connect_dict_new[key]),
                        nb_node_per_element=self.element_dict[key].nb_node_per_element,
                        indice=self.element_dict[key].indice,
                        ref_element=self.element_dict[key].ref_element,
                        gauss_point=self.element_dict[key].gauss_point,
                        scalar_product=self.element_dict[key].scalar_product,
                    )

            if len(coord_init) != len(node_indice):
                self.clear_node()

            self._is_renum = False

    # Inlined from Methods.Mesh.MeshMat.save_vtk
    def save_vtk(self, save_path):
        """Save mesh to a .vtk file

        Parameters
        ----------
        self : Mesh
            an Mesh object
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
        self.get_mesh_pv().save(save_path)
