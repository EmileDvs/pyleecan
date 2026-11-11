# Experimental dataclass generated from Generator/ClassesRef/Simulation/MagFEMM.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from dataclasses import dataclass, field
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from shutil import copyfile
from typing import Any

import numpy as np

from ..definitions import MAIN_DIR
from ..Functions_new.FEMM import FEMM_GROUPS
from ..Functions_new.FEMM.comp_femm_phi_wind import comp_FEMM_Phi_wind
from ..Functions_new.FEMM.comp_femm_torque import comp_FEMM_torque
from ..Functions_new.FEMM.draw_femm import draw_FEMM
from ..Functions_new.FEMM.update_femm_simulation import update_FEMM_simulation
from ..Functions_new.labels import STATOR_LAB
from ..Functions_new.MeshSolution.build_meshsolution import build_meshsolution
from ..Functions_new.MeshSolution.build_solution_data import build_solution_data
from ..Functions_new.MeshSolution.build_solution_vector import build_solution_vector
from ._femm_handler import _FEMMHandler
from .data_1d import Data1D
from .dxf_import import DXFImport
from .element_mat import ElementMat
from .fpgn_tri import FPGNTri
from .magnetics import Magnetics
from .mesh_mat import MeshMat
from .node_mat import NodeMat
from .out_mag_femm import OutMagFEMM
from .ref_triangle_3 import RefTriangle3
from .scalar_product_l2 import ScalarProductL2


@dataclass(eq=False)
class MagFEMM(Magnetics):
    """Magnetic module: Finite Element model with FEMM

    Attributes
    ----------
    Kmesh_fineness : float
        global coefficient to adjust mesh fineness in FEMM (1 : default , > 1 : finner , < 1 : less fine)
        Default: 1
    Kgeo_fineness : float
        global coefficient to adjust geometry fineness in FEMM (1 : default , > 1 : finner , < 1 : less fine)
        Default: 1
    type_calc_leakage : int
        0 no leakage calculation /  1 calculation using single slot
        Default: 0; Minimum: 0; Maximum: 1
    file_name : str or None
        Name of the file to save the FEMM model
        Default: None
    FEMM_dict_enforced : dict or None
        To enforce user-defined values for FEMM main parameters
        Default: {}
    is_get_meshsolution : bool
        To save FEA and mesh for latter post-procesing
        Default: False
    is_save_meshsolution_as_file : bool
        To save FEA and mesh as h5 files to save memory
        Default: False
    is_sliding_band : bool
        False to desactivate the sliding band
        Default: True
    transform_list : list
        List of dictionary to apply transformation on the machine surfaces. Key: label (to select the surface), type (rotate or translate), value (alpha or delta)
        Default: []
    rotor_dxf : DXFImport or None
        To use a dxf version of the rotor instead of build_geometry
        Default: None
    stator_dxf : DXFImport or None
        To use a dxf version of the rotor instead of build_geometry
        Default: None
    import_file : str or None
        To import an existing femm file
        Default: None
    is_close_femm : bool
        To close femm automatically after the simulation
        Default: True
    nb_worker : int
        To run FEMM in parallel (the parallelization is on the time loop)
        Default: 1
    Rag_enforced : float or None
        To enforce a different radius value for air-gap outputs
        Unit: m; Default: None
    is_set_previous : bool
        True set previous .ans result file in current .fem to use it as initialization and speed up calculation time
        Default: True
    is_fast_draw : bool
        True to use the symetry of the lamination to draw the machine faster
        Default: True
    is_calc_torque_energy : bool
        True to calculate torque from integration of energy derivate over rotor elements
        Default: True
    """

    Kmesh_fineness: float = 1
    """global coefficient to adjust mesh fineness in FEMM (1 : default , > 1 : finner , < 1 : less fine)"""
    Kgeo_fineness: float = 1
    """global coefficient to adjust geometry fineness in FEMM (1 : default , > 1 : finner , < 1 : less fine)"""
    type_calc_leakage: int = 0
    """0 no leakage calculation /  1 calculation using single slot """
    file_name: str | None = None
    """Name of the file to save the FEMM model"""
    FEMM_dict_enforced: dict[str, Any] | None = field(default_factory=dict)
    """To enforce user-defined values for FEMM main parameters """
    is_get_meshsolution: bool = False
    """To save FEA and mesh for latter post-procesing """
    is_save_meshsolution_as_file: bool = False
    """To save FEA and mesh as h5 files to save memory"""
    is_sliding_band: bool = True
    """False to desactivate the sliding band"""
    transform_list: list[Any] = field(default_factory=list)
    """List of dictionary to apply transformation on the machine surfaces. Key: label (to select the surface), type (rotate or translate), value (alpha or delta)"""
    rotor_dxf: DXFImport | None = field(
        default=None, metadata={"default_class": "DXFImport"}
    )
    """To use a dxf version of the rotor instead of build_geometry"""
    stator_dxf: DXFImport | None = field(
        default=None, metadata={"default_class": "DXFImport"}
    )
    """To use a dxf version of the rotor instead of build_geometry"""
    import_file: str | None = None
    """To import an existing femm file"""
    is_close_femm: bool = True
    """To close femm automatically after the simulation"""
    nb_worker: int = 1
    """To run FEMM in parallel (the parallelization is on the time loop)"""
    Rag_enforced: float | None = None
    """To enforce a different radius value for air-gap outputs"""
    is_set_previous: bool = True
    """True set previous .ans result file in current .fem to use it as initialization and speed up calculation time"""
    is_fast_draw: bool = True
    """True to use the symetry of the lamination to draw the machine faster"""
    is_calc_torque_energy: bool = True
    """True to calculate torque from integration of energy derivate over rotor elements"""

    # Inlined from Methods.Simulation.MagFEMM.build_MS_sliced
    def build_MS_sliced(self, MS_sliced, MS, axes_dict, Nslices, ii):
        """Build and solve FEMM model to calculate and store magnetic quantities

        Parameters
        ----------
        self : MagFEMM
            a MagFEMM object
        output : Output
            an Output object
        axes_dict: {Data}
            Dict of axes used for magnetic calculation
        delta_xy: ndarray
            Rotor center position function of time

        Returns
        -------
        out_dict: dict
            Dict containing the following quantities:
                Br : ndarray
                    Airgap radial flux density (Nt,Na) [T]
                Bt : ndarray
                    Airgap tangential flux density (Nt,Na) [T]
                Tem : ndarray
                    Electromagnetic torque over time (Nt,) [Nm]
                Phi_wind_stator : ndarray
                    Stator winding flux (qs,Nt) [Wb]
                Phi_wind : dict
                    Dict of winding fluxlinkage with respect to Machine.get_lam_list_label (qs,Nt) [Wb]
                meshsolution: MeshSolution
                    MeshSolution object containing magnetic quantities B, H, mu for each time step
        """

        solution_dict = {}

        for key, solution in MS_sliced.items():
            # Define axis
            name, _ = solution.get_axes_list()

            if hasattr(solution.field, "components"):
                comp_x = solution.field.components["comp_x"]
                field_x = comp_x.values
                comp_y = solution.field.components["comp_y"]
                field_y = comp_y.values
                field = np.concatenate(
                    (field_x[..., None], field_y[..., None]), axis=-1
                )

                axes_list = comp_x.axes

                new_solution = MS.get_solution(label=solution.label)
                new_comp_x = new_solution.field.components["comp_x"]
                new_field_x = new_comp_x.values
                new_comp_y = new_solution.field.components["comp_y"]
                new_field_y = new_comp_y.values
                new_field = np.concatenate(
                    (new_field_x[..., None], new_field_y[..., None]), axis=-1
                )
            else:
                data = solution.field
                axes_list = data.axes
                field = data.values

                new_solution = MS.get_solution(label=solution.label)
                new_field = new_solution.field.values

            if "z" in name:
                axis_slice = axes_list[2].copy()
                axis_slice.values = np.append(axis_slice.values, ii)
                new_field = np.concatenate((field, new_field[:, :, None]), axis=2)
            else:
                axis_slice = Data1D(name="z", values=[ii - 1, ii])
                new_field = np.concatenate(
                    (field[:, :, None], new_field[:, :, None]), axis=2
                )

            if ii == Nslices:
                axis_slice = axes_dict["z"]

            new_axis_list = [axes_list[0], axes_list[1], axis_slice]

            if hasattr(solution.field, "components"):
                new_sol = build_solution_vector(
                    field=new_field,
                    axis_list=new_axis_list,
                    name=comp_x.name,
                    symbol=solution.field.symbol,
                    unit=comp_x.unit,
                    type_element=solution.type_element,
                )
            else:
                new_sol = build_solution_data(
                    field=new_field,
                    axis_list=new_axis_list,
                    name=data.name,
                    symbol=data.symbol,
                    unit=data.unit,
                    type_element=solution.type_element,
                )

            solution_dict[key] = new_sol

        MS_sliced_new = build_meshsolution(
            solution_dict=solution_dict,
            label=MS_sliced.label,
            mesh=MS_sliced.mesh,
            group=MS_sliced.group,
        )

        return MS_sliced_new

    # Inlined from Methods.Simulation.MagFEMM.comp_flux_airgap
    def comp_flux_airgap(self, output, axes_dict, Is_val=None, Ir_val=None):
        """Build and solve FEMM model to calculate and store magnetic quantities

        Parameters
        ----------
        self : MagFEMM
            a MagFEMM object
        output : Output
            an Output object
        axes_dict: {Data}
            Dict of axes used for magnetic calculation

        Returns
        -------
        out_dict: dict
            Dict containing the following quantities:
                Br : ndarray
                    Airgap radial flux density (Nt,Na) [T]
                Bt : ndarray
                    Airgap tangential flux density (Nt,Na) [T]
                Tem : ndarray
                    Electromagnetic torque over time (Nt,) [Nm]
                Phi_wind_stator : ndarray
                    Stator winding flux (qs,Nt) [Wb]
                Phi_wind : dict
                    Dict of winding fluxlinkage with respect to Machine.get_lam_list_label (qs,Nt) [Wb]
                meshsolution: MeshSolution
                    MeshSolution object containing magnetic quantities B, H, mu for each time step
        """

        logger = self.get_logger()

        # Init output
        out_dict = {}
        if output.mag.internal is None:
            output.mag.internal = OutMagFEMM()

        # Get time and angular axes
        Angle = axes_dict["angle"]
        Time = axes_dict["time"]

        # Set the angular symmetry factor according to the machine and check if it is anti-periodic
        sym, is_antiper_a = Angle.get_periodicity()

        # Import angular vector from Data object
        angle = Angle.get_values(
            is_oneperiod=self.is_periodicity_a,
            is_antiperiod=is_antiper_a and self.is_periodicity_a,
        )
        Na = angle.size

        # Check if the time axis is anti-periodic
        _, is_antiper_t = Time.get_periodicity()

        # Number of time steps
        time = Time.get_values(
            is_oneperiod=self.is_periodicity_t,
            is_antiperiod=is_antiper_t and self.is_periodicity_t,
        )
        Nt = time.size

        # Get rotor angular position
        angle_rotor = output.get_angle_rotor()[0:Nt]

        # Setup the FEMM simulation
        # Geometry building and assigning property in FEMM
        # Instanciate a new FEMM
        femm = _FEMMHandler()
        output.mag.internal.handler_list.append(femm)
        if self.import_file is None:
            path_femm = self.get_path_save_fem(output)
            logger.debug("Drawing machine in FEMM at " + path_femm)
            FEMM_dict = draw_FEMM(
                femm,
                output,
                is_mmfr=self.is_mmfr,
                is_mmfs=self.is_mmfs,
                sym=sym,
                is_antiper=is_antiper_a,
                type_calc_leakage=self.type_calc_leakage,
                is_remove_ventS=self.is_remove_ventS,
                is_remove_ventR=self.is_remove_ventR,
                is_remove_slotS=self.is_remove_slotS,
                is_remove_slotR=self.is_remove_slotR,
                type_BH_stator=self.type_BH_stator,
                type_BH_rotor=self.type_BH_rotor,
                kgeo_fineness=self.Kgeo_fineness,
                kmesh_fineness=self.Kmesh_fineness,
                user_FEMM_dict=self.FEMM_dict_enforced,
                path_save=path_femm,
                is_sliding_band=self.is_sliding_band,
                transform_list=self.transform_list,
                rotor_dxf=self.rotor_dxf,
                stator_dxf=self.stator_dxf,
                is_fast_draw=self.is_fast_draw,
                T_mag=self.T_mag,
            )
        else:
            logger.debug("Reusing the FEMM file: " + self.import_file)
            if output.mag.internal.FEMM_dict is not None:
                FEMM_dict = output.mag.internal.FEMM_dict
            else:
                FEMM_dict = self.FEMM_dict_enforced

        # Init flux arrays in out_dict
        out_dict["B_{rad}"] = np.zeros((Nt, Na))
        out_dict["B_{circ}"] = np.zeros((Nt, Na))
        if self.is_calc_torque_energy:
            # Init torque array in out_dict
            out_dict["Tem"] = np.zeros(Nt)
        # Init lamination winding flux list of arrays in out_dict
        machine = output.simu.machine
        out_dict["Phi_wind"] = {}
        axes_dict_elec = output.elec.axes_dict
        for label in machine.get_lam_list_label():
            if "phase_" + label in axes_dict_elec:
                qs = axes_dict_elec["phase_" + label].get_length(is_smallestperiod=True)
                out_dict["Phi_wind"][label] = np.zeros((Nt, qs))
        # delete 'Phi_wind' if empty
        if len(out_dict["Phi_wind"]) == 0:
            out_dict.pop("Phi_wind")

        # Solve for all time step and store all the results in out_dict
        if self.nb_worker > 1:
            # A Femm handler will be created for each worker
            femm.closefemm()
            output.mag.internal.handler_list.remove(femm)
            # With parallelization
            (
                B_elem,
                H_elem,
                mu_elem,
                A_node,
                meshFEMM,
                groups,
                A_elem,
            ) = self.solve_FEMM_parallel(
                femm,
                output,
                out_dict,
                FEMM_dict=FEMM_dict,
                sym=sym,
                Nt=Nt,
                angle=angle,
                Is=Is_val,
                Ir=Ir_val,
                angle_rotor=angle_rotor,
                filename=self.import_file,
            )
        else:
            # Without parallelization
            B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem = self.solve_FEMM(
                femm,
                output,
                out_dict,
                FEMM_dict=FEMM_dict,
                sym=sym,
                Nt=Nt,
                angle=angle,
                Is=Is_val,
                Ir=Ir_val,
                angle_rotor=angle_rotor,
                is_close_femm=self.is_close_femm,
                filename=self.import_file,
            )

        # Store FEMM_dict in to avoid drawing the machine several times
        output.mag.internal.FEMM_dict = FEMM_dict

        # Store stator winding flux
        if STATOR_LAB + "-0" in out_dict["Phi_wind"].keys():
            out_dict["Phi_wind_stator"] = out_dict["Phi_wind"][STATOR_LAB + "-0"]

        # Store mesh data & solution
        if self.is_get_meshsolution and B_elem is not None:
            # Define axis
            Time = Time.copy()
            meshFEMM.sym = sym
            meshFEMM.is_antiper_a = is_antiper_a
            indices_element = meshFEMM.element_dict["triangle"].indice
            Indices_Element = Data1D(
                name="indice",
                values=indices_element,
                is_components=True,
                is_overlay=False,
            )
            # Slice = axes_dict["z"]
            axis_list = [Time, Indices_Element]

            B_sol = build_solution_vector(
                field=B_elem[:, :, None, :],  # quick fix for slice issue
                axis_list=axis_list,
                name="Magnetic Flux Density",
                symbol="B",
                unit="T",
            )
            H_sol = build_solution_vector(
                field=H_elem[:, :, None, :],
                axis_list=axis_list,
                name="Magnetic Field",
                symbol="H",
                unit="A/m",
            )
            mu_sol = build_solution_data(
                field=mu_elem[:, :, None],
                axis_list=axis_list,
                name="Magnetic Permeability",
                symbol=r"\mu",
                unit="H/m",
            )
            Ae_sol = build_solution_data(
                field=A_elem[:, :, None],
                axis_list=axis_list,
                name="Magnetic Potential Vector (per element)",
                symbol="A_z^{element}",
                unit="Wb/m",
            )

            indices_nodes = meshFEMM.node.indice
            Indices_Nodes = Data1D(
                name="indice", values=indices_nodes, is_components=True
            )
            axis_list_node = [Time, Indices_Nodes]

            An_sol = build_solution_data(
                field=A_node,
                axis_list=axis_list_node,
                name="Magnetic Potential Vector (nodal)",
                symbol="A_z",
                unit="Wb/m",
            )
            An_sol.type_element = "node"

            solution_dict = {
                solution.label: solution
                for solution in [B_sol, H_sol, mu_sol, An_sol, Ae_sol]
            }

            out_dict["meshsolution"] = build_meshsolution(
                solution_dict=solution_dict,
                label="FEMM 2D Magnetostatic",
                mesh=meshFEMM,
                group=groups,
            )

        return out_dict

    # Inlined from Methods.Simulation.MagFEMM.get_meshsolution
    def get_meshsolution(
        self, femm, FEMM_dict, save_path, j_t0, id_worker=0, is_get_mesh=False
    ):
        """Load the mesh data and solution data. FEMM must be working and a simulation must have been solved.

        Parameters
        ----------
        self : MagFEMM
            a MagFEMM object
        femm : FEMMHandler
            client to send command to a FEMM instance
        save_path: str
            Full path to folder in which to save results
        j_t0 : int
            time step index
        id_worker : int
            worker index
        is_get_mesh : bool
            True to load and create the mesh or not

        Returns
        -------
        mesh: MeshMat
            Object containing magnetic mesh
        B: ndarray
            3D Magnetic flux density for each element (Nelem, 3) [T]
        H : ndarray
            3D Magnetic field for each element (Nelem, 3) [A/m]
        mu : ndarray
            Magnetic relative permeability for each element (Nelem,1) []
        groups: dict
            Dict whose values are group label and values are array of indices of related elements

        """

        idworker = str(id_worker)  # For parallelization TODO

        path_txt = os.path.join(MAIN_DIR, "Functions", "FEMM") + "\\"
        path_lua_in = os.path.join(path_txt, "get_mesh_data_FEMM.lua")
        path_lua_out = os.path.join(save_path, "get_mesh_data_FEMM" + idworker + ".lua")
        path_txt_out = save_path + "\\"
        path_txt_out = path_txt_out.replace("\\", "/")

        # Create a new LUA script with current paths
        file_lua = open(path_lua_in, "r")
        text_lua = file_lua.read()
        file_lua.close()
        text_lua = text_lua.replace("my_path_txt", path_txt_out)
        text_lua = text_lua.replace("my_id_worker", idworker)

        file_lua_out = open(path_lua_out, "w")
        file_lua_out.write(text_lua)
        file_lua_out.close()

        # Run the LUA externally using FEMM LUA console and store the data in the
        # temporary text files
        path_lua_out2 = path_lua_out.replace("\\", "/")
        femm.callfemm('dofile("' + path_lua_out2 + '")')

        # Delete the LUA script
        os.remove(path_lua_out)

        # Save MeshMat for only 1 time step with sliding band
        path_node = os.path.join(save_path, "nodes" + idworker + ".txt")
        path_element = os.path.join(save_path, "elements" + idworker + ".txt")
        results_nodes = np.loadtxt(path_node, delimiter=" ")
        if is_get_mesh:
            # Read the nodes and elements files
            listElem0 = np.loadtxt(path_element, dtype="f", delimiter=" ").astype(
                np.float64
            )
            NbNd = len(results_nodes)
            NbElem = len(listElem0)

            # Node list
            listNd = np.zeros(shape=(NbNd, 3))
            listNd[:, 0] = results_nodes[:, 0]
            listNd[:, 1] = results_nodes[:, 1]

            # Element list
            # listElem = np.zeros(shape=(NbElem, 3))
            listElem = listElem0[:, 0:3] - 1

            mesh = MeshMat()
            mesh.element_dict["triangle"] = ElementMat(
                connectivity=listElem,
                nb_element=NbElem,
                nb_node_per_element=3,
                indice=np.linspace(0, NbElem - 1, NbElem, dtype=int),
            )
            mesh.element_dict["triangle"].ref_element = RefTriangle3(epsilon=1e-9)
            mesh.element_dict["triangle"].gauss_point = FPGNTri(nb_gauss_point=1)
            mesh.element_dict["triangle"].scalar_product = ScalarProductL2()

            mesh.node = NodeMat(
                coordinate=listNd[:, 0:2],
                nb_node=NbNd,
                indice=np.linspace(0, NbNd - 1, NbNd, dtype=int),
            )
            # get all groups that are in the FEMM model
            groups = {}
            for grp, val in FEMM_dict["groups"].items():
                if grp != "lam_group_list":
                    idx = FEMM_GROUPS[grp]["ID"]
                    name = FEMM_GROUPS[grp]["name"]
                    if isinstance(val, list):
                        # Create a sub group for each index of the list, e.g for magnets
                        ind = np.array([], dtype=int)
                        for ii, id_i in enumerate(val):
                            name_i = name + "_" + str(ii)
                            ind_i = np.where(listElem0[:, 6] == id_i)[0]
                            if ind_i.size > 0:
                                # Store the list of indices for the ith subgroup
                                groups[name_i] = (
                                    mesh.element_dict["triangle"].indice[ind_i].tolist()
                                )
                                # Concatenate all sub groups to keep the main group of rotor magnets
                                ind = np.concatenate((ind, ind_i))
                    else:
                        # Create a group with all elements og group indice idx
                        ind = np.where(listElem0[:, 6] == idx)[0]

                    if ind.size > 0:
                        groups[name] = (
                            mesh.element_dict["triangle"].indice[ind].tolist()
                        )
        else:
            mesh = None
            groups = None

        # Delete text files
        os.remove(path_node)
        os.remove(path_element)

        # Read the results file
        path_results = os.path.join(save_path, "results" + idworker + ".txt")
        results = np.loadtxt(path_results, delimiter=" ")

        # Delete text files
        os.remove(path_results)

        B = results[:, 0:2]
        H = results[:, 2:4]
        mu = results[:, 4]
        A_elem = results[:, 5]
        A = results_nodes[:, 2]

        return mesh, B, H, mu, A, groups, A_elem

    # Inlined from Methods.Simulation.MagFEMM.get_path_save
    def get_path_save(self, output):
        """Return the path to save the FEMM simulation

        Parameters
        ----------
        self : MagFEMM
            a MagFEMM object
        output : Output
            an Output object

            Returns
        -------
        save_path: str
            Path to save the FEMM simulation

        """
        path_res = output.get_path_result()

        save_dir = os.path.join(path_res, "Femm")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        return save_dir

    # Inlined from Methods.Simulation.MagFEMM.get_path_save_fem
    def get_path_save_fem(self, output):
        """Return the path to save the FEMM simulation

        Parameters
        ----------
        self : MagFEMM
            a MagFEMM object
        output : Output
            an Output object

            Returns
        -------
        save_path: str
            Path to save the .fem file

        """
        save_dir = self.get_path_save(output)

        if self.file_name not in [None, ""]:
            if self.file_name[-4:] != ".fem":
                file_name = self.file_name + ".fem"
            else:
                file_name = self.file_name
        elif output.simu.machine.name not in [None, ""]:
            file_name = output.simu.machine.name + "_model.fem"
        elif output.simu.name not in [None, ""]:
            file_name = output.simu.name + "_model.fem"
        else:  # Default name
            file_name = "FEMM_simulation.fem"

        return os.path.join(save_dir, file_name)

    # Inlined from Methods.Simulation.MagFEMM.solve_FEMM
    def solve_FEMM(
        self,
        femm,
        output,
        out_dict,
        FEMM_dict,
        sym,
        Nt,
        angle,
        Is,
        Ir,
        angle_rotor,
        is_close_femm,
        filename=None,
        start_t=0,
        end_t=None,
        Nmess=4,
    ):
        """
        Solve FEMM model to calculate airgap flux density, torque instantaneous/average/ripple values,
        flux induced in stator windings and flux density, field and permeability maps

        Parameters
        ----------
        self: MagFEMM
            A MagFEMM object
        femm: _FEMMHandler
            Object to handle FEMM
        output: Output
            An Output object
        out_dict: dict
            Dict containing the following quantities to update for each time step:
                Br : ndarray
                    Airgap radial flux density (Nt,Na) [T]
                Bt : ndarray
                    Airgap tangential flux density (Nt,Na) [T]
                Tem : ndarray
                    Electromagnetic torque over time (Nt,) [Nm]
                Phi_wind : list of ndarray # TODO should it rather be a dict with lam label?
                    List of winding flux with respect to Machine.get_lamlist (qs,Nt) [Wb]
        FEMM_dict : dict
            Dict containing FEMM model parameters
        sym: int
            Spatial symmetry factor
        Nt: int
            Number of time steps for calculation
        angle: ndarray
            Angle vector for calculation
        Is : ndarray
            Stator current matrix (qs,Nt) [A]
        Ir : ndarray
            Stator current matrix (qs,Nt) [A]
        angle_rotor: ndarray
            Rotor angular position vector (Nt,)
        is_close_femm: bool
            True to close FEMM handler in the end
        filename: str
            Path to FEMM model to open
        start_t: int
            Index of first time step (0 by default, used for parallelization)
        end_t: int
            Index of last time step (Nt by default, used for parallelization)

        Returns
        -------
        B: ndarray
            3D Magnetic flux density for all time steps and each element (Nt, Nelem, 3) [T]
        H : ndarray
            3D Magnetic field for all time steps and each element (Nt, Nelem, 3) [A/m]
        mu : ndarray
            Magnetic relative permeability for all time steps and each element (Nt, Nelem) []
        mesh: MeshMat
            Object containing magnetic mesh at first time step
        groups: dict
            Dict whose values are group label and values are array of indices of related elements

        """

        logger = self.get_logger()
        is_sliding_band = self.is_sliding_band

        if filename is not None:
            # Open FEMM instance if filename is not None (parallel case)
            try:
                # Try to open FEMM instance if handler already exists (first parallelized handler)
                femm.openfemm(1)
            except Exception:
                # Create a new FEMM handler in case of parallelization on another FEMM instance
                femm = _FEMMHandler()
                output.mag.internal.handler_list.append(femm)
                # Open a new FEMM instance associated to new handler
                femm.openfemm(1)
            # Open FEMM file
            femm.opendocument(filename)
        else:
            # FEMM instance and file is already open, get filename from output
            filename = self.get_path_save_fem(output)

        if is_sliding_band and self.is_set_previous:
            # Check result .ans file existence and delete it if it exists
            ans_file = (
                (os.path.splitext(filename)[0] + ".ans")
                .replace("\\", "/")
                .replace("//", "/")
            )
            if os.path.isfile(ans_file):
                logger.debug("Delete existing result .ans file at: " + ans_file)
                os.remove(ans_file)

        if not is_sliding_band:
            fileinit_fem = self.get_path_save_fem(output)
            fileinit_ans = fileinit_fem[:-4] + ".ans"
            filetemp_fem = fileinit_fem[:-4] + "_temp.fem"
            filetemp_ans = fileinit_fem[:-4] + "_temp.ans"

        # Take last time step at Nt by default
        if end_t is None:
            end_t = Nt

        # Number of angular steps
        Na = angle.size

        # Loading parameters for readibility
        machine = output.simu.machine

        if self.Rag_enforced is not None:
            # Take enforced value
            Rag = self.Rag_enforced
        else:
            Rag = machine.comp_Rgap_mec()

        save_path = self.get_path_save(output)
        is_internal_rotor = machine.rotor.is_internal
        if "Phi_wind" in out_dict:
            qs = {}
            Npcp = {}
            for key in out_dict["Phi_wind"].keys():
                lam = machine.get_lam_by_label(key)
                qs[key] = out_dict["Phi_wind"][key].shape[1]  # Winding phase number
                Npcp[key] = lam.winding.Npcp  # parallel paths

        # Account for initial angular shift of stator and rotor and apply it to the sliding band
        angle_shift = self.angle_rotor_shift - self.angle_stator_shift

        B_elem = None
        H_elem = None
        mu_elem = None
        meshFEMM = None
        groups = None
        A_node = None
        A_elem = None

        # Check current values
        if np.all(Is == 0):
            Is = None
        if np.all(Ir == 0):
            Ir = None

        k1 = 0
        k2 = 0
        Nloop = end_t - start_t
        # Compute the data for each time step
        for ii in range(start_t, end_t):
            if Nloop > Nmess:
                if k1 >= round(k2 * Nloop / Nmess):
                    logger.info(
                        "Solving time steps: " + str(int(k2 / Nmess * 100)) + "%"
                    )
                    k2 += 1

            elif ii == 0:
                logger.info("Computing Airgap Flux in FEMM")
            k1 += 1

            if not is_sliding_band:
                # Reload model for each time step if no sliding band
                if ii > start_t:
                    femm.opendocument(fileinit_fem)
                femm.mi_saveas(filetemp_fem)

            # Update rotor position and currents
            update_FEMM_simulation(
                femm=femm,
                FEMM_dict=FEMM_dict,
                is_sliding_band=is_sliding_band,
                is_internal_rotor=is_internal_rotor,
                angle_rotor=angle_rotor + angle_shift,
                Is=Is,
                Ir=Ir,
                ii=ii,
            )

            # Check if there is a previous solution file to speed up non-linear iterations
            if is_sliding_band and self.is_set_previous and ii > start_t:
                if os.path.isfile(ans_file):
                    # Setup .ans file path in FEMM model
                    femm.mi_setprevious(ans_file, 0)
                else:
                    logger.warning("Cannot reuse result .ans file: " + ans_file)
            else:
                # Make sure that no file path is filled in FEMM model
                femm.mi_setprevious("", 0)

            # Run the computation
            femm.mi_analyze()

            # Load results
            femm.mi_loadsolution()

            # Get the flux result
            if is_sliding_band:
                for jj in range(Na):
                    (
                        out_dict["B_{rad}"][ii, jj],
                        out_dict["B_{circ}"][ii, jj],
                    ) = femm.mo_getgapb("bc_ag2", angle[jj] * 180 / np.pi)
            else:
                for jj in range(Na):
                    B = femm.mo_getb(Rag * np.cos(angle[jj]), Rag * np.sin(angle[jj]))
                    out_dict["B_{rad}"][ii, jj] = B[0] * np.cos(angle[jj]) + B[
                        1
                    ] * np.sin(angle[jj])
                    out_dict["B_{circ}"][ii, jj] = -B[0] * np.sin(angle[jj]) + B[
                        1
                    ] * np.cos(angle[jj])

            # Compute the torque
            if self.is_calc_torque_energy:
                label_rot = machine.rotor.get_label()
                rotor_groups = FEMM_dict["groups"]["lam_group_list"][label_rot]
                out_dict["Tem"][ii] = comp_FEMM_torque(
                    femm, rotor_groups=rotor_groups, sym=sym
                )

            if "Phi_wind" in out_dict:
                # Phi_wind computation
                # TODO fix inconsistency for multi lam machines here
                for key in out_dict["Phi_wind"].keys():
                    out_dict["Phi_wind"][key][ii, :] = comp_FEMM_Phi_wind(
                        femm,
                        qs[key],
                        Npcp[key],
                        is_stator=machine.get_lam_by_label(key).is_stator,
                        L1=machine.stator.L1,
                        L2=machine.rotor.L1,
                        sym=sym,
                    )

            # Load mesh data & solution
            if self.is_get_meshsolution:
                # Get mesh data and magnetic quantities from .ans file
                meshFEMMi, Bi, Hi, mui, Ani, groupsi, Aei = self.get_meshsolution(
                    femm,
                    FEMM_dict,
                    save_path,
                    j_t0=ii,
                    id_worker=start_t,
                    is_get_mesh=ii == start_t,
                )

                # Store magnetic flux density, field and relative permeability for the current time step

                # Initialize mesh and magnetic quantities for first time step
                if ii == start_t:
                    meshFEMM = meshFEMMi
                    groups = groupsi
                    Nelem = meshFEMM.element_dict["triangle"].nb_element
                    Nnode = meshFEMM.node.nb_node
                    Nt0 = end_t - start_t
                    B_elem = np.zeros([Nt0, Nelem, 3])
                    H_elem = np.zeros([Nt0, Nelem, 3])
                    mu_elem = np.zeros([Nt0, Nelem])
                    A_node = np.zeros([Nt0, Nnode])
                    A_elem = np.zeros([Nt0, Nelem])

                # Shift time index ii in case start_t is not 0 (parallelization)
                ii0 = ii - start_t

                B_elem[ii0, :, 0:2] = Bi
                H_elem[ii0, :, 0:2] = Hi
                mu_elem[ii0, :] = mui
                A_node[ii0, :] = Ani
                A_elem[ii0, :] = Aei

            if not is_sliding_band:
                femm.mi_close()
                femm.mo_close

        if Nloop > Nmess and Nt > 1 and k2 <= Nmess:
            logger.info("Solving time step: 100%")

        # Shift to take into account stator position
        if self.angle_stator_shift != 0:
            roll_id = int(self.angle_stator_shift * Na / (2 * np.pi))
            out_dict["B_{rad}"] = np.roll(out_dict["B_{rad}"], roll_id, axis=1)
            out_dict["B_{circ}"] = np.roll(out_dict["B_{circ}"], roll_id, axis=1)

        if not is_sliding_band:
            # Remove initial .fem
            if os.path.isfile(fileinit_fem):
                os.remove(fileinit_fem)
            # Remove initial .fem
            if os.path.isfile(fileinit_ans):
                os.remove(fileinit_ans)
            # Rename .fem and .ans files to initial names
            os.rename(filetemp_fem, fileinit_fem)
            os.rename(filetemp_ans, fileinit_ans)

        # Close FEMM handler
        if is_close_femm:
            femm.closefemm()
            output.mag.internal.handler_list.remove(femm)

        out_dict["Rag"] = Rag

        return B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem

    # Inlined from Methods.Simulation.MagFEMM.solve_FEMM_parallel
    def solve_FEMM_parallel(
        self,
        femm,
        output,
        out_dict,
        FEMM_dict,
        sym,
        Nt,
        angle,
        Is,
        Ir,
        angle_rotor,
        filename,
    ):
        """
        Same as solve_FEMM including parallelization on several workers

        Parameters
        ----------
        self: MagFEMM
            A MagFEMM object
        femm: FEMMHandler
            Object to handle FEMM
        output: Output
            An Output object
        out_dict: dict
            Dict containing the following quantities to update for each time step:
                Br : ndarray
                    Airgap radial flux density (Nt,Na) [T]
                Bt : ndarray
                    Airgap tangential flux density (Nt,Na) [T]
                Tem : ndarray
                    Electromagnetic torque over time (Nt,) [Nm]
                Phi_wind_stator : ndarray
                    Stator winding flux (qs,Nt) [Wb]
        FEMM_dict : dict
            Dict containing FEMM model parameters
        sym: int
            Spatial symmetry factor
        Nt: int
            Number of time steps for calculation
        angle: ndarray
            Angle vector for calculation
        Is : ndarray
            Stator current matrix (qs,Nt) [A]
        Ir : ndarray
            Stator current matrix (qs,Nt) [A]
        angle_rotor: ndarray
            Rotor angular position vector (Nt,)
        filename: str
            Path to FEMM model to open

        Returns
        -------
        B: ndarray
            3D Magnetic flux density for all time steps and each element (Nt, Nelem, 3) [T]
        H : ndarray
            3D Magnetic field for all time steps and each element (Nt, Nelem, 3) [A/m]
        mu : ndarray
            Magnetic relative permeability for all time steps and each element (Nt, Nelem) []
        mesh: MeshMat
            Object containing magnetic mesh at first time step
        groups: dict
            Dict whose values are group label and values are array of indices of related elements
        """

        # The following function must be in solve_FEMM_parallel to access
        # to its variable without passing them in arguments
        def solve_FEMM_single(femm_handler, filename, start_t, end_t):
            """
            Call FEMM to compute airgap flux density from start_t to end_t timesteps

            This function is called in threads, the shared memory enable to modify global variable
            defined in solve_FEMM_parallel such as Br and Bt

            Parameters
            ----------

            femm_handler : _FEMMHandler
                FEMM handler
            filename : str
                .fem file path
            start_t : int
                first timestep to compute
            end_t: int
                last timestep to compute

            Returns
            -------
            B: ndarray
                3D Magnetic flux density for time steps of the current FEMM instance and each element (Nt0, Nelem, 3) [T]
            H : ndarray
                3D Magnetic field for time steps of the current FEMM instance and each element (Nt0, Nelem, 3) [A/m]
            mu : ndarray
                Magnetic relative permeability for time steps of the current FEMM instance and each element (Nt0, Nelem) []
            mesh: MeshMat
                Object containing magnetic mesh at first time step of the current FEMM instance
            groups: dict
                Dict whose values are group label and values are array of indices of related elements

            """

            B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem = self.solve_FEMM(
                femm_handler,
                output,
                out_dict,
                FEMM_dict,
                sym=sym,
                Nt=Nt,
                angle=angle,
                Is=Is,
                Ir=Ir,
                angle_rotor=angle_rotor,
                is_close_femm=True,
                filename=filename,
                start_t=start_t,
                end_t=end_t,
            )

            return B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem

        # Init mesh solution as None since array allocation can only be done once
        # number of elements is known, i.e. after first time step resolution
        B_elem, H_elem, mu_elem, meshFEMM, groups, A_node, A_elem = (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

        # Loading parameters for readibility
        if filename is not None:
            fem_file = filename
        else:
            fem_file = self.get_path_save_fem(output)
        nb_worker = self.nb_worker
        logger = self.get_logger()

        # Check method parameters
        if nb_worker > cpu_count():
            logger.warning(
                f"Parallelization is set on {nb_worker} threads while "
                + f"your computer only has {cpu_count()}."
            )
        if nb_worker > Nt:
            logger.debug(
                f"{nb_worker} workers requested for {Nt} time steps. "
                + f"Using {Nt} workers instead"
            )
            nb_worker = Nt

        # Copy femm file and create lists to split the tasks
        nb_task_worker = []  # nb of task for each worker
        nb_task_to_split = Nt  # number of task remaining to split
        for w in range(nb_worker, 0, -1):
            # Copy the file
            copyfile(fem_file, fem_file[:-4] + "_" + str(w) + ".fem")
            # Compute the number of task for this worker
            nb_task_worker.append(nb_task_to_split // w + ((nb_task_to_split % w) > 0))
            # Remove the number of task of this worker from the number of remaining tasks
            nb_task_to_split -= nb_task_worker[-1]

        # Define the argument lists:
        #   - femm_handler
        #   - femm_file
        #   - start_time : index of the first time step to compute
        #   - end_time : index of the last time step to compute
        femm_handler = [_FEMMHandler() for i in range(nb_worker)]
        femm_files = [
            fem_file[:-4] + "_" + str(i) + ".fem" for i in range(1, nb_worker + 1)
        ]
        start_time_list = [sum(nb_task_worker[:i]) for i in range(nb_worker)]
        end_time_list = [sum(nb_task_worker[: i + 1]) for i in range(nb_worker)]

        # Gathering the different arguments for each instance
        args = [
            [i, j, k, l]
            for i, j, k, l in zip(
                femm_handler, femm_files, start_time_list, end_time_list
            )
        ]

        # append femm_handler to handler_list
        output.mag.internal.handler_list.extend(femm_handler)
        # Creating threads pool
        with Pool(nb_worker) as p:
            results = p.starmap(solve_FEMM_single, args)

        # Building mesh solution
        if self.is_get_meshsolution:
            B_elem = np.concatenate([res[0] for res in results], axis=0)
            H_elem = np.concatenate([res[1] for res in results], axis=0)
            mu_elem = np.concatenate([res[2] for res in results], axis=0)
            A_node = np.concatenate([res[3] for res in results], axis=0)
            meshFEMM = results[0][4]
            groups = results[0][5]
            A_elem = np.concatenate([res[6] for res in results], axis=0)

        # Remove temporary .fem and .ans files
        for w in range(nb_worker, 0, -1):
            try:
                os.remove(fem_file[:-4] + "_" + str(w) + ".fem")
            except Exception:
                filename = fem_file[:-4] + "_" + str(w) + ".fem"
                self.get_logger().warning("Could not remove file: " + filename)

            try:
                os.remove(fem_file[:-4] + "_" + str(w) + ".ans")
            except Exception:
                filename = fem_file[:-4] + "_" + str(w) + ".ans"
                self.get_logger().warning("Could not remove file: " + filename)

        return B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem
