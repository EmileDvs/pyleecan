# Experimental dataclass generated from Generator/ClassesRef/Mesh/MeshVTK.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
import shutil
from dataclasses import dataclass, field
from typing import Literal, Optional

import numpy as np
import pyvista as pv
from meshio import read
from vtk import vtkPointSet

from ..definitions import RESULT_DIR
from ..Functions.GUI.log_error import log_error
from .element_mat import ElementMat
from .fpgn_seg import FPGNSeg
from .fpgn_tri import FPGNTri
from .mesh import Mesh
from .mesh_mat import MeshMat
from .node_mat import NodeMat
from .ref_line_3 import RefLine3
from .ref_quad_9 import RefQuad9
from .ref_segment_p_1 import RefSegmentP1
from .ref_triangle_3 import RefTriangle3
from .scalar_product_l2 import ScalarProductL2


@dataclass(eq=False)
class MeshVTK(Mesh):
    """Gather the mesh storage format

    Attributes
    ----------
    mesh : vtk.vtkPointSet or None
        Pyvista object of the mesh (optional)
        Default: None
    is_pyvista_mesh : bool
        Store the pyvista object
        Default: False
    format : str
        Format in which the mesh is stored
        Default: "vtk"
    path : str or None
        Path where the mesh is stored
        Default: None
    name : str
        Name of the mesh file
        Default: "mesh"
    surf : pyvista.core.pointset.PolyData or None
        Pyvista object of the outer surface
        Default: None
    is_vtk_surf : bool
        Save the surface mesh in a vtk file
        Default: False
    surf_path : str or None
        Path where the outer surface is stored
        Default: None
    surf_name : str or None
        Name of the outer surface file
        Default: None
    node_normals : ndarray or None
        Array of normals to nodes (element vertices)
        Default: None
    """

    mesh: vtkPointSet | None = field(default="None", metadata={"as_dict": "1"})
    """Pyvista object of the mesh (optional)"""
    is_pyvista_mesh: bool = False
    """Store the pyvista object"""
    format: str = "vtk"
    """Format in which the mesh is stored"""
    path: str | None = None
    """Path where the mesh is stored"""
    name: str = "mesh"
    """Name of the mesh file"""
    surf: pv.core.pointset.PolyData | None = field(
        default="None", metadata={"as_dict": "1"}
    )
    """Pyvista object of the outer surface"""
    is_vtk_surf: bool = False
    """Save the surface mesh in a vtk file"""
    surf_path: str | None = None
    """Path where the outer surface is stored"""
    surf_name: str | None = None
    """Name of the outer surface file"""
    node_normals: np.ndarray | None = None
    """Array of normals to nodes (element vertices)"""

    # Inlined from Methods.Mesh.MeshVTK.convert
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
            from .mesh_mat import MeshMat

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

    # Inlined from Methods.Mesh.MeshVTK.get_element
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

    # Inlined from Methods.Mesh.MeshVTK.get_element_area
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

    # Inlined from Methods.Mesh.MeshVTK.get_mesh_pv
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

    # Inlined from Methods.Mesh.MeshVTK.get_node_coordinate
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

    # Inlined from Methods.Mesh.MeshVTK.get_normals
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

    # Inlined from Methods.Mesh.MeshVTK.get_path
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

        return os.path.join(self.path, filename).replace("\\", "/")

    # Inlined from Methods.Mesh.MeshVTK.get_surf
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

    # Inlined from Methods.Mesh.MeshVTK.perm_coord
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
        elementMatDict = {}

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

    # Inlined from Methods.Mesh.MeshVTK.save_vtk
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
