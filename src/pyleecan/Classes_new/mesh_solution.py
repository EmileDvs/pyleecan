# Experimental dataclass generated from Generator/ClassesRef/Mesh/MeshSolution.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from collections.abc import ItemsView, KeysView, ValuesView
from dataclasses import dataclass, field
from typing import Any, Hashable, Iterator, Optional

import numpy as np
from scipy.io import savemat

from ..definitions import config_dict
from ..Functions.GUI.log_error import log_error
from ..Functions.Plot.Pyvista.configure_plot import configure_plot
from ..Functions.Plot.Pyvista.plot_glyph_pv import plot_glyph_pv
from ..Functions.Plot.Pyvista.plot_mesh_field import plot_mesh_field
from ..Functions.Plot.Pyvista.plot_surf_deflection import plot_surf_deflection
from ..Functions.Structural.conversions import DimError, cart2pol, pol2cart
from ._pyleecan_class import PyleecanClass
from .element_mat import ElementMat
from .mesh import Mesh
from .mesh_mat import MeshMat
from .mesh_vtk import MeshVTK
from .node_mat import NodeMat
from .out_force import OutForce
from .out_mag import OutMag
from .out_struct import OutStruct
from .solution import Solution
from .solution_vector import SolutionVector


@dataclass(eq=False)
class MeshSolution(PyleecanClass):
    """Abstract class to associate a mesh with one or several solutions

    Attributes
    ----------
    label : str or None
        (Optional) Descriptive name of the mesh
        Default: None
    mesh : Mesh or None
        A Mesh object.
        Default: None
    solution_dict : {Solution} or None
        A dictionary of Solution objects
        Default: None
    group : dict or None
        Dict sorted by groups name with list of elements indices.
        Default: {}
    dimension : int
        Dimension of the physical problem
        Default: 2; Minimum: 1; Maximum: 3
    path : str or None
        Path where the MeshSolution is stored as a file
        Default: None
    """

    COLOR_MAP = config_dict["PLOT"]["COLOR_DICT"]["COLOR_MAP"]
    FONT_FAMILY_PYVISTA = config_dict["PLOT"]["FONT_FAMILY_PYVISTA"]
    label: str | None = None
    """(Optional) Descriptive name of the mesh"""
    mesh: Mesh | None = None
    """A Mesh object. """
    solution_dict: dict[str, Solution] | None = None
    """A dictionary of Solution objects"""
    group: dict[str, Any] | None = field(default_factory=dict)
    """Dict sorted by groups name with list of elements indices. """
    dimension: int = 2
    """Dimension of the physical problem"""
    path: str | None = None
    """Path where the MeshSolution is stored as a file"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                OutForce,
                OutMag,
                OutStruct,
            ),
        ):
            raise TypeError(
                "MeshSolution parent must be an instance of OutForce or OutMag or OutStruct, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Mesh.MeshSolution.__getitem__
    def __getitem__(self, label: Hashable) -> Solution:
        """Mimic dict behaviour

        Parameters
        ----------
        label : str
            label of the solution

        Returns
        -------
        Solution
            solution stored in solution_dict
        """
        try:
            return self.solution_dict[label]
        except KeyError:
            keys = list(self.keys())
            if keys:
                raise KeyError(
                    f'Wrong solution label "{label}", please use one of the following values: {keys}.'
                )
            else:
                raise KeyError(
                    f'Wrong solution label "{label}", the MeshSolution is empty.'
                )

    # Inlined from Methods.Mesh.MeshSolution.__iter__
    def __iter__(self) -> Iterator[str]:
        """Mimic dict behaviour"""
        return iter(self.solution_dict)

    # Inlined from Methods.Mesh.MeshSolution.__setitem__
    def __setitem__(self, label: Hashable, solution: Solution) -> None:
        """Mimic dict behaviour self[__key] = __value"""
        if label in self.solution_dict:
            self.replace_solution(solution, label)
        else:
            self.add_solution(solution, label)

    # Inlined from Methods.Mesh.MeshSolution.add_solution
    def add_solution(self, solution: Solution, label: Optional[str] = "") -> None:
        """Add a solution to its solution_dict

        Parameters
        ----------
        solution : Solution
            solution to add
        label : Optional[str], optional
            label of the solution, by default ""

        Raises
        ------
        ValueError
            The solution label must be unique
        """
        if not label:
            label = solution.label

        if label in self.keys():
            raise ValueError(
                f'A solution with label "{label}" is already in MeshSolution.'
            )

        self.solution_dict[label] = solution

    # Inlined from Methods.Mesh.MeshSolution.export_to_mat
    def export_to_mat(self, save_path):
        """Save mesh and all solutions to a .mat file

        Parameters
        ----------
        self : MeshSolution
            an MeshSolution object
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None

        """
        # Check if extension file is .mat
        save_path_L = save_path.split(".")
        if len(save_path_L) == 1:
            save_path = f"{save_path_L[0]}.mat"
        else:
            if save_path_L[-1] != "mat":
                err_msg = f"Error save path extension is not .mat"
                log_error(
                    self,
                    err_msg,
                    self.mesh.get_logger(),
                    is_popup=False,
                    is_warning=False,
                )

        # Check if save_path exist
        save_path_2 = os.path.dirname(save_path)

        if not os.path.isdir(save_path_2):
            raise Exception(
                f"Error while saving mesh solution, save path doesn't exist: {save_path}"
            )

        # dict to save
        mesh_dict = {}
        mesh_dict["mesh"] = {}
        mesh_dict["mesh"]["points_coordinates"] = self.mesh.get_mesh_pv().points
        mesh_dict["mesh"]["cells_connectivity"] = self.mesh.get_mesh_pv().cells

        mesh_dict["solution"] = {}
        for key in self.solution_dict:
            mesh_dict["solution"][key] = self.solution_dict[f"{key}"].as_dict()

        # To save meshsolution in file .mat, dict mesh_dict must not have value = None and value = {} (empty dict)
        mesh_dict["solution"] = self.del_value_None(mesh_dict["solution"])
        # Save result
        savemat(save_path, mesh_dict)

    @staticmethod
    def del_value_None(mesh_dict):
        """Delate value set at None in dict

        Parameters
        ----------
        mesh_dict : dict
            dict Mesh Solution

        """
        for key, value in mesh_dict.items():
            if isinstance(value, dict):
                if len(mesh_dict[key]) == 0:
                    mesh_dict.pop(key)
                    MeshSolution.del_value_None(mesh_dict)
                    break

                else:
                    MeshSolution.del_value_None(mesh_dict[key])

            elif isinstance(value, list):
                for ele in value:
                    if isinstance(ele, dict):
                        MeshSolution.del_value_None(ele)

            elif value == None:
                del mesh_dict[key]
                MeshSolution.del_value_None(mesh_dict)
                break

        return mesh_dict

    # Inlined from Methods.Mesh.MeshSolution.get_deflection
    def get_deflection(self, *args, label, indices, field_name):
        """Get the vector field, the field name and the corresponding pyvista mesh in format adapted to a glyph plot.

        Parameters
        ----------
        self : MeshSolution
            a MeshSolution object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        label : str
            a label
        indices : list
            list of the points to extract (optional)
        field_name : str
            title of the field to display on plot

        Returns
        -------
        vect_field : ndaray
            vector field to plot
        field_normal_amp : ndarray
            scalar field which is the normal/radial component of vect_field (to adjust the colormap)
        field_name : str
            name of the field
        mesh_pv : UnstructuredGrid
            pyvista mesh to plot
        """
        # Get mesh_pv and field

        # Try to get normal field, else use radial
        try:
            mesh_pv, field_normal_amp, field_name = self.get_mesh_field_pv(
                *args,
                label=label,
                indices=indices,
                field_name=field_name,
                is_normal=True,
            )
        except:
            mesh_pv, field_normal_amp, field_name = self.get_mesh_field_pv(
                *args,
                label=label,
                indices=indices,
                field_name=field_name,
                is_radial=True,
            )

        _, vect_field, _ = self.get_mesh_field_pv(
            *args,
            label=label,
            indices=indices,
            field_name=field_name,
        )

        solution = self.get_solution(
            label=label,
        )

        axes_list = solution.get_axes_list(*args)

        # Add third dimension if needed
        ind = axes_list[0].index("component")
        if axes_list[1][ind] == 2:
            vect_field = np.hstack((vect_field, np.zeros((vect_field.shape[0], 1))))

        if field_name is None:
            field_name = label if label is not None else "Field"

        return vect_field, field_normal_amp, field_name, mesh_pv

    # Inlined from Methods.Mesh.MeshSolution.get_field
    def get_field(
        self,
        *args_list,
        label=None,
        indices=None,
        is_rthetaz=False,
        is_pol2cart=False,
        is_radial=False,
        is_normal=False,
        is_rms=False,
        is_center=False,
        is_surf=False,
        is_squeeze=True,
    ):
        """Return the solution corresponding to a label.

        Parameters
        ----------
        self : MeshSolution
            an MeshSolution object
        *args_list: list of strings
            List of axes requested by the user, their units and values (optional)
        label : str
            label of the solution
        indices : list
            list of indices to extract from mesh and field
        is_rthetaz : bool
            cylindrical coordinates
        is_radial : bool
            radial component only
        is_normal : bool
            normal component only (on nodes or centers)
        is_rms : bool
            rms over surface sum((F.n)**2 dS)/S
        is_center : bool
            field at element centers
        is_surf : bool
            field over outer surface
        is_squeeze : bool
            squeeze the output result

        Returns
        -------
        result : ndarray
            field

        """
        # if len(args_list) == 1 and type(args_list[0]) == tuple:
        #     args_list = args_list[0]  # if called from another script with *arg_list

        # Get field
        solution = self.get_solution(label=label)

        axes_list = solution.get_axes_list(*args_list)
        ax_names = axes_list[0]

        field = solution.get_field(
            *args_list, is_squeeze=False
        )  # Don't use is_squeeze = is_squeeze here!

        if (
            isinstance(solution, SolutionVector)
            and "comp_x" not in solution.field.components
        ):
            is_pol2cart = True

        # Enforce indice from those contained in MeshSolution if not None

        if self.group is not None and "output_nodes" in self.group and indices is None:
            indices_normals = self.group["output_nodes"]
        else:
            indices_normals = indices

        # Check dimensions
        shape = field.shape
        is_other_dim = False

        ## Check the existing axes and put indice and component in first position to ease transformation.
        if axes_list[0] is not None:
            # Swap axis indice position
            if "indice" in axes_list[0]:
                ind_indices0 = axes_list[0].index("indice")
                axes_list[0][0], axes_list[0][ind_indices0] = (
                    axes_list[0][ind_indices0],
                    axes_list[0][0],
                )  # names swap
                axes_list[1][0], axes_list[1][ind_indices0] = (
                    axes_list[1][ind_indices0],
                    axes_list[1][0],
                )  # length swap
                field = np.swapaxes(field, 0, ind_indices0)  # field axis swap
                ind_indices = 0

            else:
                raise Exception(
                    "ERROR, MeshSolution axes list should contain 'indice' axis"
                )

            if "component" in axes_list[0]:
                # Index of component axis (degree of freedom)
                ind_component0 = axes_list[0].index("component")
                axes_list[0][1], axes_list[0][ind_component0] = (
                    axes_list[0][ind_component0],
                    axes_list[0][1],
                )  # names swap
                axes_list[1][1], axes_list[1][ind_component0] = (
                    axes_list[1][ind_component0],
                    axes_list[1][1],
                )  # length swap
                field = np.swapaxes(field, 1, ind_component0)  # field axis swap
                ind_component = 1
            else:
                ind_component = None

            # Init list of indices of axes that are not "component", "indice",
            ind_otherdim = [i for i in range(len(axes_list[1]))]
            ind_otherdim.pop(ind_indices)
            if ind_component is not None:
                ind_otherdim.pop(ind_component - 1)

        ## Define the type of transformation
        is_recursive = False  # If there is at least one transformation, switch to true.

        if indices is not None:
            is_recursive = True

        if is_radial:
            is_rthetaz = True
            is_recursive = True

        if is_rms:
            is_center = True
            is_normal = True
            is_recursive = True
        # if is_normal:
        #     is_surf = True
        if is_rthetaz or is_normal:
            if ind_component is None:
                raise DimError("The field should be a vector field")

        # Get mesh if necessary
        if is_center or is_normal or is_rthetaz or is_surf or is_pol2cart:
            is_recursive = True
            # Get the mesh
            mesh = self.mesh
            mesh_pv = mesh.get_mesh_pv(indices=indices_normals)
            if isinstance(mesh, MeshMat):
                mesh = MeshVTK(mesh=mesh_pv, is_pyvista_mesh=True)
        else:
            mesh, mesh_pv = None, None
        # Get nodes coordinates if necessary
        if is_rthetaz or is_pol2cart:
            is_recursive = True
            points = mesh.get_node_coordinate(indices=indices)
        else:
            points = None
        # Get normals if necessary
        if is_normal and is_center:
            is_recursive = True
            # Get normals
            normals = mesh.get_normals(indices=indices_normals)
        elif is_normal:
            is_recursive = True
            normals = mesh.get_normals(indices=indices_normals, loc="point")
        else:
            normals = None
        # Get element area if necessary
        if is_rms:
            cell_area = mesh.get_element_area(indices=indices)
        else:
            cell_area = None

        ## Perform the transformation
        shape_result = axes_list[1]

        if is_recursive:
            if is_center:
                shape_result[ind_indices] = mesh_pv.n_cells
            elif indices_normals is not None:
                shape_result[ind_indices] = len(indices_normals)

            if is_rms:
                shape_result[ind_indices] = 1

            if is_radial or is_rms or is_normal:
                shape_result[ind_component] = 1

            shape_otherdim = [shape_result[ii] for ii in ind_otherdim]

            result = self.apply_normal_center_surf_vectorfield(
                field,
                ind_otherdim,
                shape_otherdim,
                is_center,
                is_normal,
                is_surf,
                is_rms,
                is_rthetaz,
                is_radial,
                is_pol2cart,
                mesh_pv,
                normals,
                points,
                cell_area,
                shape_result,
                field.dtype,
                indices,
                ind_indices,
            )
        else:
            result = field  # No transformation

        # Reverse axes swaps (to match with get_axes_list)
        if ind_component is not None:
            result = np.swapaxes(result, 1, ind_component0)
        result = np.swapaxes(result, 0, ind_indices0)

        if is_squeeze:
            result = np.squeeze(result)
            if shape_result[ind_indices] == 1:
                # Re add node dimension which has been squeezed if there is only one node
                result = result[None, ...]

        return result

    @staticmethod
    def apply_normal_center_surf_vectorfield(
        field,
        ind_otherdim,
        shape_otherdim,
        is_center,
        is_normal,
        is_surf,
        is_rms,
        is_rthetaz,
        is_radial,
        is_pol2cart,
        mesh_pv,
        normals,
        points,
        cell_area,
        shape_result,
        dtype,
        indices,
        ind_indices,
    ):
        """Perform the required operation on the input field by performing a recursive call on all axes.
        This function is necessary as pyvista operators require field with only indice axis (and component axis).

        Parameters
        ----------
        field : ndarray
            a vector field
        is_center : bool
            field at element centers
        indices : list
            list of indices to extract from mesh and field
        is_rthetaz : bool
            cylindrical coordinates
        is_radial : bool
            radial component only
        is_normal : bool
            normal component only (on nodes or centers)
        is_rms : bool
            rms over surface sum((F.n)**2 dS)/S

        is_surf : bool
            field over outer surface

        Returns
        -------
        result : ndarray
            field

        """

        new_ind_otherdim = list(ind_otherdim)

        if len(ind_otherdim) == 0:
            # Reduce field to requested indices
            if indices is not None:
                field = field.take(indices, axis=ind_indices)

            if is_center:
                # Add field to mesh
                if field.dtype == float:
                    mesh_pv["real"] = field
                else:
                    mesh_pv["real"] = np.real(field)
                    mesh_pv["imag"] = np.imag(field)
                if is_center:
                    # Points to centers
                    mesh_cell = mesh_pv.point_data_to_cell_data()
                else:
                    mesh_cell = mesh_pv
            if is_surf:
                # Extract surface
                surf = mesh_cell.extract_geometry()
                if field.dtype == float:
                    field = surf["real"]
                else:
                    field = surf["real"] + 1j * surf["imag"]
            elif is_center:
                if field.dtype == float:
                    field = mesh_cell["real"]
                else:
                    field = mesh_cell["real"] + 1j * mesh_cell["imag"]

            # Project on normals if necessary
            if is_normal:
                field = np.einsum("ij,ij->i", normals, field)
            # rms computation
            if is_rms:
                field = np.sqrt(
                    np.sum(np.abs(field**2) * cell_area) / np.sum(cell_area)
                )
            # Coordinates
            if is_rthetaz:
                field = cart2pol(field, points)
            if is_radial:
                field = field[:, 0]
            if is_pol2cart and not is_radial:
                field = pol2cart(field, points)

            field = np.reshape(field, shape_result)

            return field

        else:
            result = np.zeros(shape_result, dtype=dtype)

            for i in range(shape_otherdim[-1]):
                field_i = field.take((i), axis=new_ind_otherdim[-1])

                ind_other_dim_i = list(new_ind_otherdim)
                ind_other_dim_i.pop()
                shape_otherdim_i = list(shape_otherdim)
                shape_otherdim_i.pop()
                shape_result_i = list(shape_result)
                shape_result_i.pop(new_ind_otherdim[-1])

                result[..., i] = MeshSolution.apply_normal_center_surf_vectorfield(
                    field_i,
                    ind_other_dim_i,
                    shape_otherdim_i,
                    is_center,
                    is_normal,
                    is_surf,
                    is_rms,
                    is_rthetaz,
                    is_radial,
                    is_pol2cart,
                    mesh_pv,
                    normals,
                    points,
                    cell_area,
                    shape_result_i,
                    dtype,
                    indices,
                    ind_indices,
                )

            return result

    # Inlined from Methods.Mesh.MeshSolution.get_glyph
    def get_glyph(self, *args, label, indices, field_name):
        """Get the vector field, the field name and the corresponding pyvista mesh in format adapted to a glyph plot.

        Parameters
        ----------
        self : MeshSolution
            a MeshSolution object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        label : str
            a label
        indices : list
            list of the points to extract (optional)
        field_name : str
            title of the field to display on plot

        Returns
        -------
        vect_field : ndaray
            field to plot
        field_name : str
            name of the field
        mesh_pv : UnstructuredGrid
            pyvista mesh to plot
        """
        # Get mesh_pv and field

        # Get the mesh
        mesh_pv, vect_field, _ = self.get_mesh_field_pv(
            *args,
            label=label,
            indices=indices,
            field_name=field_name,
        )

        solution = self.get_solution(
            label=label,
        )

        axes_list = solution.get_axes_list(*args)

        # Add third dimension if needed
        ind = axes_list[0].index("component")
        if axes_list[1][ind] == 2:
            vect_field = np.hstack((vect_field, np.zeros((vect_field.shape[0], 1))))
            is_2D = True
        else:
            is_2D = False

        if field_name is None:
            field_name = label if label is not None else "Field"
            # if self.dimension:
            #     p.view_xy()

        return vect_field, field_name, mesh_pv, is_2D

    # Inlined from Methods.Mesh.MeshSolution.get_group
    def get_group(self, group_names):
        """Return all attributes of a MeshSolution object with only the elements, nodes
        and corresponding solutions of the group.

        Parameters
        ----------
        self : MeshSolution
            an MeshSolution object
        group_name : [str]
            list of the name of the group(s) (e.g. ["stator"])

        Returns
        -------
        meshsol_grp: MeshSolution
            a new MeshSolution object which is subpart of self
        """

        dimension = self.dimension

        group_indices = []
        meshsolution_label = ""
        is_interface = False

        # 1) get the indices of all targeted element corresponding to group(s)
        sep_list = []
        if isinstance(group_names, list):
            for grp in group_names:
                if grp == "/":
                    # The groups before and after "/" are stored in different lists
                    # to perform the interface.
                    is_interface = True
                    group_indices_init = group_indices.copy()
                    group_indices = []
                    sep_list.append(group_indices_init)
                else:
                    group_indices.extend(self.group[grp])
                    meshsolution_label += f"{grp}_"
        elif isinstance(group_names, str):
            if group_names not in self.group:
                raise KeyError(
                    group_names
                    + " group doesn't exist (available groups: "
                    + str(list(self.group.keys()))
                    + ")"
                )
            group_indices.extend(self.group[group_names])
            meshsolution_label += group_names

        sep_list.append(np.sort(group_indices))

        # 2) extract the corresponding connectivity and create a new mesh
        mesh_init = self.mesh
        mesh_list = []
        for sep in sep_list:
            connect_dict, nb_element, indice_dict = mesh_init.get_element(sep)

            node_indice = []
            mesh_new = MeshMat(
                _is_renum=True, sym=mesh_init.sym, is_antiper_a=mesh_init.is_antiper_a
            )
            for key in connect_dict:
                node_indice.extend(np.unique(connect_dict[key]))
                mesh_new.element_dict[key] = ElementMat(
                    connectivity=connect_dict[key],
                    nb_element=len(connect_dict[key]),
                    nb_node_per_element=mesh_init.element_dict[key].nb_node_per_element,
                    indice=indice_dict[key],
                    ref_element=mesh_init.element_dict[key].ref_element,
                    gauss_point=mesh_init.element_dict[key].gauss_point,
                    scalar_product=mesh_init.element_dict[key].scalar_product,
                )
            node_indice = np.unique(node_indice)

            mesh_new.node = NodeMat(init_dict=mesh_init.node.as_dict())

            mesh_list.append(mesh_new)

        # 3) if interface, create the corresponding new mesh (e.g. with triangle mesh,
        #    it creates only segment elements)
        if is_interface:
            mesh_interface = mesh_list[0].interface(mesh_list[1])
            connect_interface, *_ = mesh_interface.get_element()

            node_indice_interf = []
            for key in connect_interface:
                node_indice_interf.extend(np.unique(connect_interface[key]))

            node_indice = np.unique(node_indice_interf)

        # 4) select the corresponding solutions
        solution_dict = {}
        for key, solution in self.items():
            type_element_sol = solution.type_element

            new_sol = None
            if type_element_sol == "node":
                new_sol = solution.get_solution(indice=node_indice.tolist())
            elif not is_interface:  # Interface is only available for node solution.
                new_sol = solution.get_solution(indice=indice_dict[type_element_sol])

            if new_sol is not None:
                solution_dict[key] = new_sol

        # 5) Create the corresponding MeshSolution object
        if is_interface:
            mesh_interface.clear_node()
            mesh = mesh_interface
        else:
            mesh_new.clear_node()
            mesh = mesh_new

        meshsol_grp = self.copy()
        meshsol_grp.label = meshsolution_label
        meshsol_grp.mesh = mesh
        meshsol_grp.solution_dict = solution_dict
        meshsol_grp.dimension = dimension
        meshsol_grp.group = self.group

        return meshsol_grp

    # Inlined from Methods.Mesh.MeshSolution.get_mesh_field_pv
    def get_mesh_field_pv(
        self,
        *args,
        label=None,
        indices=None,
        is_surf=False,
        is_radial=False,
        is_center=False,
        is_normal=False,
        field_name=None,
        itimefreq=0,
    ):
        """Return the mesh and field adapted to pyvista plots.

        Parameters
        ----------
        self : MeshSolution
            an MeshSolution object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        label : str
            label of the solution
        indices : list
            list of indices
        is_radial : bool
            radial component only
        is_center : bool
            field at element centers
        field_name : str
            label of the field to return
        itimefreq : int
            if the field depends has a time/freqs axis, return the timefreq-th slice.

        Returns
        -------
        mesh_pv: vtk.vtkPointSet
            a pyvista mesh object
        field : ndarray
            an extracted field
        field_name : str
            name of the extracted field (useful if not specified as input)

        """

        new_mesh = self.mesh.copy()

        if not isinstance(new_mesh, MeshVTK):
            new_mesh.renum()

        mesh_pv = new_mesh.get_mesh_pv()

        solution = self.get_solution(
            label=label,
        )

        args_list = []
        if len(args) > 0:
            for a in args:
                args_list.append(a)
        args_list.append("indice")
        if isinstance(solution, SolutionVector):
            args_list.append("components")

        field = self.get_field(
            *args_list,
            label=label,
            indices=indices,
            is_surf=is_surf,
            is_radial=is_radial,
            is_center=is_center,
            is_normal=is_normal,
        )

        if field_name is None:
            field_name = label if label is not None else "Field"

        return mesh_pv, field, field_name

    # Inlined from Methods.Mesh.MeshSolution.get_solution
    def get_solution(self, label: Optional[str] = None) -> Solution:
        """Return the solution corresponding to label or the first solution by default.

        Parameters
        ----------
        self : MeshSolution
            an MeshSolution object
        label : str
            solution label

        Returns
        -------
        solution: Solution
            a Solution object

        """

        # Return first solution
        if label is None:
            return next(iter(self.values()))

        # Search for the desired solution
        try:
            return self[label]
        except KeyError:
            raise KeyError(
                f'Wrong solution label "{label}", please use one of the following values: {list(self.keys())}.'
            )

    # Inlined from Methods.Mesh.MeshSolution.items
    def items(self) -> ItemsView:
        """Return the keys and values of the solution_dict

        Returns
        -------
        _type_
            _description_
        """
        return self.solution_dict.items()

    # Inlined from Methods.Mesh.MeshSolution.keys
    def keys(self) -> KeysView:
        """Return the keys of the solution_dict

        Returns
        -------
        _type_
            _description_
        """
        return self.solution_dict.keys()

    # Inlined from Methods.Mesh.MeshSolution.perm_coord
    def perm_coord(
        self,
        perm_coord_list=[0, 1, 2],
    ):
        """Permute coordinates of Mesh Solution in place

        Parameters
        ----------
        self : MeshSolution
            a MeshSolution object
        perm_coord_list : list
            list of the coordinates to be permuted

        """
        len_perm_coord_list = len(perm_coord_list)

        # swap mesh solution
        for solution in self.values():
            # swap modal shapes
            meshsol_field = solution.field
            if len_perm_coord_list != meshsol_field.shape[-1]:
                raise ValueError(
                    f"Wrong permutation list size, expected {meshsol_field.shape[-1]}, got {len_perm_coord_list}."
                )
            meshsol_field = meshsol_field[..., perm_coord_list]
            solution.field = meshsol_field

        # swap mesh VTK
        self.mesh = self.mesh.perm_coord(perm_coord_list=perm_coord_list)

    # Inlined from Methods.Mesh.MeshSolution.plot_contour
    def plot_contour(
        self,
        *args,
        label=None,
        indices=None,
        is_surf=False,
        is_radial=False,
        is_center=False,
        clim=None,
        field_name=None,
        save_path=None,
        is_show_fig=True,
        win_title=None,
        is_animated=False,
        title="",
        pv_plotter=None,
        colormap=None,
    ):
        """Plot the contour of a field on a mesh using pyvista plotter.

        Parameters
        ----------
        self : MeshSolution
            a MeshSolution object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        label : str
            a label
        indices : list
            list of the points to extract (optional)
        is_surf : bool
            field over outer surface
        is_radial : bool
            radial component only
        is_center : bool
            field at element-centers
        clim : list
            a list of 2 elements for the limits of the colorbar
        field_name : str
            title of the field to display on plot
        save_path : str
            path to save the figure
        is_show_fig : bool
            To call show at the end of the method
        win_title : str
            Name of the window
        is_animated : bool
            True to animate magnetic flux density
        title : str
            Name of the figure
        pv_plotter : pyvista.BasePlotter
            Pyvista plotter
        colormap : str
            Name of the colormap to use (default is from config_dict)

        Returns
        -------

        """

        # Init figure
        if pv_plotter is None:
            if title != "" and win_title == "":
                win_title = title
            elif win_title != "" and title == "":
                title = win_title

            pv_plotter, sargs = configure_plot(
                pv_plotter=pv_plotter, win_title=win_title
            )

            pv_plotter.add_text(
                title,
                position="upper_edge",
                color="black",
                font_size=10,
                font=self.FONT_FAMILY_PYVISTA,
            )

        # Get the mesh_pv and field
        mesh_pv, field, field_name = self.get_mesh_field_pv(
            *args,
            label=label,
            indices=indices,
            is_surf=is_surf,
            is_radial=is_radial,
            is_center=is_center,
            field_name=field_name,
        )

        # Add field to mesh
        # if is_surf:
        #     surf = mesh_pv.get_surf(indices=indices)
        #     surf[field_name] = real(field)
        #     mesh_field = surf
        # else:
        #     mesh_pv[field_name] = real(field)
        #     mesh_field = mesh_pv
        if clim is None:
            clim = [np.min(np.real(field)), np.max(np.real(field))]
            if abs((clim[1] - clim[0]) / clim[1]) < 0.01:
                clim[0] = -abs(clim[1])
                clim[1] = abs(clim[1])

        plot_mesh_field(
            pv_plotter,
            sargs,
            field_name,
            clim=clim,
            mesh_pv=mesh_pv,
            field=field,
            colormap=colormap,
        )

        if self.dimension:
            # 2D view
            pv_plotter.view_xy()

        ###########
        # Internal animation (cannot be combined with other plots)
        if is_animated:
            pv_plotter.add_text(
                'Adjust 3D view and press "Q"',
                position="lower_edge",
                color="gray",
                font_size=10,
                font="arial",
            )
            pv_plotter.show(auto_close=False)

            pv_plotter.open_gif(save_path)
            pv_plotter.clear()

            if len(args) == 0 or "time" in args:
                mesh_pv_B, field_B, field_name_B = self.get_mesh_field_pv("time")
                nframe = len(field_B)
                is_time = True
            else:
                nframe = 25
                mesh_pv_B, field_B, field_name_B = self.get_mesh_field_pv(args)
                is_time = False
                t = np.linspace(0.0, 1.0, nframe + 1)[:nframe]

            for i in range(nframe):
                # Compute colorbar boundaries

                if is_time:
                    field = field_B[i, :]
                    phase = 1
                else:
                    field = field_B
                    phase = np.exp(1j * 2 * np.pi * t[i])
                # Compute pyvista object
                plot_mesh_field(
                    pv_plotter,
                    sargs,
                    field_name_B,
                    clim=clim,
                    mesh_pv=mesh_pv_B,
                    field=field,
                    phase=phase,
                )

                pv_plotter.add_text(
                    title,
                    position="upper_edge",
                    color="black",
                    font_size=10,
                    font="arial",
                )
                pv_plotter.write_frame()
                pv_plotter.clear()
            pv_plotter.close()

        else:
            # Save figure
            if save_path is None and is_show_fig:
                pv_plotter.show()
            elif save_path is not None:
                pv_plotter.show(interactive=False, screenshot=save_path)

    plot_contour.__kwdefaults__["colormap"] = COLOR_MAP

    # Inlined from Methods.Mesh.MeshSolution.plot_deflection
    def plot_deflection(
        self,
        *args,
        label=None,
        indices=None,
        clim=None,
        factor=None,
        field_name=None,
        save_path=None,
        title="",
        win_title="",
        is_surf=True,
        is_show_fig=True,
        pv_plotter=None,
        sargs=None,
        is_animated=False,
        phase=1,
        is_return_plot_args=False,
    ):
        """Plot the operational deflection shape using pyvista plotter.

        Parameters
        ----------
        self : MeshSolution
            a MeshSolution object
        label : str
            solution label
        indices : list
            list of the points to extract (optional)
        clim : list
            a list of 2 elements for the limits of the colorbar
        factor : float
            factor to multiply vector field
        field_name : str
            title of the field to display on plot
        is_show_fig : bool
            To call show at the end of the method
        pv_plotter=None,
        meshsol_list=[],
        plot_list=[],

        Returns
        -------
        """
        # Init figure
        if pv_plotter is None:
            if title != "" and win_title == "":
                win_title = title
            elif win_title != "" and title == "":
                title = win_title

            pv_plotter, sargs = configure_plot(
                pv_plotter=pv_plotter, win_title=win_title
            )

            pv_plotter.add_text(
                title,
                position="upper_edge",
                color="black",
                font_size=10,
                font=self.FONT_FAMILY_PYVISTA,
            )

        # Get deflection
        vect_field, field_normal_amp, field_name, mesh_pv = self.get_deflection(
            *args,
            label=label,
            indices=indices,
            field_name=field_name,
        )

        # Compute colorbar boundaries
        if clim is None:
            clim = [
                np.min(np.real(field_normal_amp)),
                np.max(np.real(field_normal_amp)),
            ]
            if (clim[1] - clim[0]) / clim[1] < 0.01:
                clim[0] = -abs(clim[1])
                clim[1] = abs(clim[1])

        # Compute deformation factor
        if factor is None:
            factor = 0.2 * np.max(np.abs(mesh_pv.bounds)) / np.max(np.abs(vect_field))

        field_name += (
            " \n(x " + format(factor, ".3g") + " [" + self.get_solution().unit + "])"
        )

        # # Plot mesh only
        # pv_plotter.add_mesh(
        #     mesh_pv, color="grey", opacity=0.7, show_edges=True, edge_color="white"
        # )

        # Extract surface
        mesh = MeshVTK(mesh=mesh_pv, is_pyvista_mesh=True)
        if is_surf:
            surf_pv = mesh.get_surf()
        else:
            surf_pv = mesh.get_mesh_pv()

        # Plot deflection surface
        plot_surf_deflection(
            surf_pv=surf_pv,
            vect_field=vect_field,
            field=field_normal_amp,
            field_name=field_name,
            pv_plotter=pv_plotter,
            sargs=sargs,
            clim=clim,
            factor=factor,
            phase=phase,
        )

        # Internal animation (cannot be combined with other plots)
        if is_animated:
            pv_plotter.add_text(
                'Adjust 3D view and press "Q"',
                position="lower_edge",
                color="gray",
                font_size=10,
                font=self.FONT_FAMILY_PYVISTA,
            )
            pv_plotter.show(auto_close=False)

            nframe = 25
            pv_plotter.open_gif(save_path)
            pv_plotter.clear()
            for t in np.linspace(0.0, 1.0, nframe, endpoint=False):
                phase = np.exp(1j * 2 * np.pi * t)

                # Compute pyvista object
                plot_surf_deflection(
                    surf_pv=surf_pv,
                    vect_field=vect_field,
                    field=field_normal_amp,
                    field_name=field_name,
                    pv_plotter=pv_plotter,
                    sargs=sargs,
                    clim=clim,
                    factor=factor,
                    phase=phase,
                )

                pv_plotter.add_text(
                    title,
                    position="upper_edge",
                    color="black",
                    font_size=10,
                    font=self.FONT_FAMILY_PYVISTA,
                )
                pv_plotter.write_frame()
                pv_plotter.clear()

            pv_plotter.close()

        else:
            # Save figure
            if save_path is None and is_show_fig:
                pv_plotter.show()
            elif save_path is not None:
                pv_plotter.show(interactive=False, screenshot=save_path)

        if is_return_plot_args:
            return (
                pv_plotter,
                sargs,
                surf_pv,
                vect_field,
                field_normal_amp,
                field_name,
                clim,
                factor,
                phase,
            )
        else:
            return pv_plotter

    # Inlined from Methods.Mesh.MeshSolution.plot_glyph
    def plot_glyph(
        self,
        *args,
        label=None,
        indices=None,
        factor=None,
        field_name=None,
        save_path=None,
        is_point_arrow=False,
        is_show_fig=True,
        pv_plotter=None,
        win_title="",
        title="",
        is_animated=False,
        phase=1,
        is_return_plot_args=False,
    ):
        """Plot the vector field as a glyph (or quiver) over the mesh.

        Parameters
        ----------
        self : MeshSolution
            a MeshSolution object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        label : str
            label of the solution to plot
        indices : list
            list of the points to extract (optional)
        clim : list
            a list of 2 elements for the limits of the colorbar
        factor : float
            factor to multiply vector field
        field_name : str
            title of the field to display on plot
        save_path : str
            path to save the plot into an image
        is_point_arrow : bool
            to plot a nodal field (point-wise solution required)
        pv_plotter : pyvista
            a pyvista object
        enforced_mesh : Mesh
            enforced Mesh object


        Returns
        -------
        """
        # Init figure
        if pv_plotter is None:
            if title != "" and win_title == "":
                win_title = title
            elif win_title != "" and title == "":
                title = win_title

            pv_plotter, _ = configure_plot(pv_plotter=pv_plotter, win_title=win_title)

            pv_plotter.add_text(
                title,
                position="upper_edge",
                color="black",
                font_size=10,
                font=self.FONT_FAMILY_PYVISTA,
            )

        # Get glyph field
        vect_field, field_name, mesh_pv, is_2D = self.get_glyph(
            *args,
            label=label,
            indices=indices,
            field_name=field_name,
        )

        # Compute factor
        if factor is None:
            factor = 0.2 * np.max(np.abs(mesh_pv.bounds)) / np.max(np.abs(vect_field))

        # Plot mesh
        pv_plotter.add_mesh(
            mesh_pv, color="grey", opacity=0.7, show_edges=True, edge_color="white"
        )

        # Add field to mesh
        plot_glyph_pv(
            pv_plotter=pv_plotter,
            mesh_pv=mesh_pv,
            vect_field=vect_field,
            is_point_arrow=is_point_arrow,
            factor=factor,
            phase=phase,
        )

        if is_2D:
            pv_plotter.view_xy()

        # Internal animation (cannot be combined with other plots)
        if is_animated:
            pv_plotter.add_text(
                'Adjust 3D view and press "Q"',
                position="lower_edge",
                color="gray",
                font_size=10,
                font=self.FONT_FAMILY_PYVISTA,
            )
            pv_plotter.show(auto_close=False)

            nframe = 25
            pv_plotter.open_gif(save_path)
            pv_plotter.clear()
            for t in np.linspace(0.0, 1.0, nframe, endpoint=False):
                phase = np.exp(1j * 2 * np.pi * t)

                pv_plotter.add_mesh(
                    mesh_pv,
                    color="grey",
                    opacity=0.7,
                    show_edges=True,
                    edge_color="white",
                )

                # Compute pyvista object
                plot_glyph_pv(
                    pv_plotter=pv_plotter,
                    mesh_pv=mesh_pv,
                    vect_field=vect_field,
                    is_point_arrow=is_point_arrow,
                    factor=factor,
                    phase=phase,
                )

                pv_plotter.add_text(
                    title,
                    position="upper_edge",
                    color="black",
                    font_size=10,
                    font=self.FONT_FAMILY_PYVISTA,
                )
                pv_plotter.write_frame()
                pv_plotter.clear()

            pv_plotter.close()
        else:
            if save_path is None and is_show_fig:
                pv_plotter.show()
            elif save_path is not None:
                pv_plotter.show(interactive=False, screenshot=save_path)

        if is_return_plot_args:
            return pv_plotter, mesh_pv, vect_field, is_point_arrow, factor, phase
        else:
            return pv_plotter

    # Inlined from Methods.Mesh.MeshSolution.plot_mesh
    def plot_mesh(
        self,
        pv_plotter=None,
        indices=None,
        save_path=None,
        is_show_axes=False,
        is_show_fig=True,
        is_show_grid=False,
        win_title=None,
    ):
        """Plot the mesh using pyvista plotter.

        Parameters
        ----------
        self : MeshSolution
            a MeshSolution object
        pv_plotter : a pyvista(qt) object, optional
            a pyvista object which will be used for the plot
        indices : list
            list of the nodes to extract (optional)
        save_path : str
            Path to a file where to save the figure
        is_show_axes : bool
            True to show axes
        is_show_fig : bool
            To call show at the end of the method
        is_show_grid : bool
            True to show grid
        win_title : str
            To set the name of the plot window

        Returns
        -------
        """

        if pv_plotter is None:
            pv_plotter, _ = configure_plot(
                pv_plotter=pv_plotter, win_title=win_title, is_show_axes=is_show_axes
            )
        else:
            is_show_fig = False

        # Get the mesh
        mesh_obj = self.mesh
        if isinstance(mesh_obj, MeshMat):
            new_mesh = mesh_obj.copy()
            new_mesh.renum()
            mesh = new_mesh.get_mesh_pv(indices=indices)
        else:
            mesh = mesh_obj.get_mesh_pv(indices=indices)

        pv_plotter.add_mesh(
            mesh,
            color="grey",
            opacity=1,
            show_edges=True,
            edge_color="white",
            line_width=1,
        )

        if is_show_grid:
            pv_plotter.show_grid()
        if self.dimension == 2:
            # 2D view
            pv_plotter.view_xy()
        else:
            # isometric view with z towards left
            pv_plotter.view_isometric()
            pv_plotter.camera_position = [
                pv_plotter.camera_position[0],
                (
                    pv_plotter.camera_position[1][0],
                    pv_plotter.camera_position[1][2],
                    pv_plotter.camera_position[1][0],
                ),
                (
                    pv_plotter.camera_position[2][1],
                    pv_plotter.camera_position[2][2],
                    pv_plotter.camera_position[2][0],
                ),
            ]
        if save_path is None and is_show_fig:
            pv_plotter.show()
        elif save_path is not None:  # and is_show_fig:
            pv_plotter.show(interactive=False, screenshot=save_path)

        return pv_plotter

    # Inlined from Methods.Mesh.MeshSolution.pop_solution
    def pop_solution(self, label: str) -> Solution:
        """Pop a solution from its solution_dict

        Parameters
        ----------
        solution : Solution
            solution to add
        label : Optional[str], optional
            label of the solution, by default ""

        Raises
        ------
        ValueError
            The solution label must be unique
        """

        return self.solution_dict.pop(label)

    # Inlined from Methods.Mesh.MeshSolution.replace_solution
    def replace_solution(self, solution: Solution, label: Optional[str] = ""):
        """Replace the solution in the solution_didct

        Parameters
        ----------
        solution : Solution
            solution to insert
        label : Optional[str], optional
            label of the solution corresponding , by default ""
        """
        if not label:
            label = solution.label

        self[label] = solution

    # Inlined from Methods.Mesh.MeshSolution.values
    def values(self) -> ValuesView:
        """Return the solutions of the solution_dict

        Returns
        -------
        _type_
            _description_
        """
        return self.solution_dict.values()
