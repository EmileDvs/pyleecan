# File generated according to Generator/ClassesRef/Simulation/MagFEMM.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/MagFEMM"""

import os
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from os import linesep, remove, rename
from os.path import isfile, join, splitext
from shutil import copyfile
from sys import getsizeof

import numpy as np
from pyleecan.Classes.Data1D import Data1D
from pyleecan.Classes.ElementMat import ElementMat
from pyleecan.Classes.FPGNTri import FPGNTri
from pyleecan.Classes.Magnetics import Magnetics
from pyleecan.Classes.MeshMat import MeshMat
from pyleecan.Classes.NodeMat import NodeMat
from pyleecan.Classes.OutMagFEMM import OutMagFEMM
from pyleecan.Classes.RefTriangle3 import RefTriangle3
from pyleecan.Classes.ScalarProductL2 import ScalarProductL2
from pyleecan.Classes._FEMMHandler import _FEMMHandler
from pyleecan.Classes._check import check_var

from pyleecan.definitions import MAIN_DIR

from pyleecan.Functions.FEMM import FEMM_GROUPS
from pyleecan.Functions.FEMM.comp_FEMM_Phi_wind import comp_FEMM_Phi_wind
from pyleecan.Functions.FEMM.comp_FEMM_torque import comp_FEMM_torque
from pyleecan.Functions.FEMM.draw_FEMM import draw_FEMM
from pyleecan.Functions.FEMM.update_FEMM_simulation import update_FEMM_simulation
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.MeshSolution.build_meshsolution import build_meshsolution
from pyleecan.Functions.MeshSolution.build_solution_data import build_solution_data
from pyleecan.Functions.MeshSolution.build_solution_vector import build_solution_vector
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import STATOR_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class MagFEMM(Magnetics):
    """Magnetic module: Finite Element model with FEMM"""

    VERSION = 1

    # cf Methods.Simulation.MagFEMM.build_MS_sliced
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

    # cf Methods.Simulation.MagFEMM.comp_flux_airgap
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
        out_dict = dict()
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

    # cf Methods.Simulation.MagFEMM.get_meshsolution
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

        path_txt = join(MAIN_DIR, "Functions", "FEMM") + "\\"
        path_lua_in = join(path_txt, "get_mesh_data_FEMM.lua")
        path_lua_out = join(save_path, "get_mesh_data_FEMM" + idworker + ".lua")
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
        path_node = join(save_path, "nodes" + idworker + ".txt")
        path_element = join(save_path, "elements" + idworker + ".txt")
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
            groups = dict()
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
        path_results = join(save_path, "results" + idworker + ".txt")
        results = np.loadtxt(path_results, delimiter=" ")

        # Delete text files
        os.remove(path_results)

        B = results[:, 0:2]
        H = results[:, 2:4]
        mu = results[:, 4]
        A_elem = results[:, 5]
        A = results_nodes[:, 2]

        return mesh, B, H, mu, A, groups, A_elem

    # cf Methods.Simulation.MagFEMM.get_path_save
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

        save_dir = join(path_res, "Femm")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        return save_dir

    # cf Methods.Simulation.MagFEMM.get_path_save_fem
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

        return join(save_dir, file_name)

    # cf Methods.Simulation.MagFEMM.solve_FEMM
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
                (splitext(filename)[0] + ".ans").replace("\\", "/").replace("//", "/")
            )
            if isfile(ans_file):
                logger.debug("Delete existing result .ans file at: " + ans_file)
                remove(ans_file)

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
                if isfile(ans_file):
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
            if isfile(fileinit_fem):
                remove(fileinit_fem)
            # Remove initial .fem
            if isfile(fileinit_ans):
                remove(fileinit_ans)
            # Rename .fem and .ans files to initial names
            rename(filetemp_fem, fileinit_fem)
            rename(filetemp_ans, fileinit_ans)

        # Close FEMM handler
        if is_close_femm:
            femm.closefemm()
            output.mag.internal.handler_list.remove(femm)

        out_dict["Rag"] = Rag

        return B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem

    # cf Methods.Simulation.MagFEMM.solve_FEMM_parallel
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
                remove(fem_file[:-4] + "_" + str(w) + ".fem")
            except Exception:
                filename = fem_file[:-4] + "_" + str(w) + ".fem"
                self.get_logger().warning("Could not remove file: " + filename)

            try:
                remove(fem_file[:-4] + "_" + str(w) + ".ans")
            except Exception:
                filename = fem_file[:-4] + "_" + str(w) + ".ans"
                self.get_logger().warning("Could not remove file: " + filename)

        return B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Kmesh_fineness=1,
        Kgeo_fineness=1,
        type_calc_leakage=0,
        file_name="",
        FEMM_dict_enforced=-1,
        is_get_meshsolution=False,
        is_save_meshsolution_as_file=False,
        is_sliding_band=True,
        transform_list=-1,
        rotor_dxf=None,
        stator_dxf=None,
        import_file=None,
        is_close_femm=True,
        nb_worker=1,
        Rag_enforced=None,
        is_set_previous=True,
        is_fast_draw=True,
        is_calc_torque_energy=True,
        is_remove_slotS=False,
        is_remove_slotR=False,
        is_remove_ventS=False,
        is_remove_ventR=False,
        is_mmfs=True,
        is_mmfr=True,
        type_BH_stator=0,
        type_BH_rotor=0,
        is_periodicity_t=False,
        is_periodicity_a=False,
        angle_stator_shift=0,
        angle_rotor_shift=0,
        logger_name="Pyleecan.Magnetics",
        Slice_enforced=None,
        Nslices_enforced=None,
        type_distribution_enforced=None,
        is_current_harm=True,
        T_mag=20,
        is_periodicity_rotor=False,
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
            if "Kmesh_fineness" in list(init_dict.keys()):
                Kmesh_fineness = init_dict["Kmesh_fineness"]
            if "Kgeo_fineness" in list(init_dict.keys()):
                Kgeo_fineness = init_dict["Kgeo_fineness"]
            if "type_calc_leakage" in list(init_dict.keys()):
                type_calc_leakage = init_dict["type_calc_leakage"]
            if "file_name" in list(init_dict.keys()):
                file_name = init_dict["file_name"]
            if "FEMM_dict_enforced" in list(init_dict.keys()):
                FEMM_dict_enforced = init_dict["FEMM_dict_enforced"]
            if "is_get_meshsolution" in list(init_dict.keys()):
                is_get_meshsolution = init_dict["is_get_meshsolution"]
            if "is_save_meshsolution_as_file" in list(init_dict.keys()):
                is_save_meshsolution_as_file = init_dict["is_save_meshsolution_as_file"]
            if "is_sliding_band" in list(init_dict.keys()):
                is_sliding_band = init_dict["is_sliding_band"]
            if "transform_list" in list(init_dict.keys()):
                transform_list = init_dict["transform_list"]
            if "rotor_dxf" in list(init_dict.keys()):
                rotor_dxf = init_dict["rotor_dxf"]
            if "stator_dxf" in list(init_dict.keys()):
                stator_dxf = init_dict["stator_dxf"]
            if "import_file" in list(init_dict.keys()):
                import_file = init_dict["import_file"]
            if "is_close_femm" in list(init_dict.keys()):
                is_close_femm = init_dict["is_close_femm"]
            if "nb_worker" in list(init_dict.keys()):
                nb_worker = init_dict["nb_worker"]
            if "Rag_enforced" in list(init_dict.keys()):
                Rag_enforced = init_dict["Rag_enforced"]
            if "is_set_previous" in list(init_dict.keys()):
                is_set_previous = init_dict["is_set_previous"]
            if "is_fast_draw" in list(init_dict.keys()):
                is_fast_draw = init_dict["is_fast_draw"]
            if "is_calc_torque_energy" in list(init_dict.keys()):
                is_calc_torque_energy = init_dict["is_calc_torque_energy"]
            if "is_remove_slotS" in list(init_dict.keys()):
                is_remove_slotS = init_dict["is_remove_slotS"]
            if "is_remove_slotR" in list(init_dict.keys()):
                is_remove_slotR = init_dict["is_remove_slotR"]
            if "is_remove_ventS" in list(init_dict.keys()):
                is_remove_ventS = init_dict["is_remove_ventS"]
            if "is_remove_ventR" in list(init_dict.keys()):
                is_remove_ventR = init_dict["is_remove_ventR"]
            if "is_mmfs" in list(init_dict.keys()):
                is_mmfs = init_dict["is_mmfs"]
            if "is_mmfr" in list(init_dict.keys()):
                is_mmfr = init_dict["is_mmfr"]
            if "type_BH_stator" in list(init_dict.keys()):
                type_BH_stator = init_dict["type_BH_stator"]
            if "type_BH_rotor" in list(init_dict.keys()):
                type_BH_rotor = init_dict["type_BH_rotor"]
            if "is_periodicity_t" in list(init_dict.keys()):
                is_periodicity_t = init_dict["is_periodicity_t"]
            if "is_periodicity_a" in list(init_dict.keys()):
                is_periodicity_a = init_dict["is_periodicity_a"]
            if "angle_stator_shift" in list(init_dict.keys()):
                angle_stator_shift = init_dict["angle_stator_shift"]
            if "angle_rotor_shift" in list(init_dict.keys()):
                angle_rotor_shift = init_dict["angle_rotor_shift"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
            if "Slice_enforced" in list(init_dict.keys()):
                Slice_enforced = init_dict["Slice_enforced"]
            if "Nslices_enforced" in list(init_dict.keys()):
                Nslices_enforced = init_dict["Nslices_enforced"]
            if "type_distribution_enforced" in list(init_dict.keys()):
                type_distribution_enforced = init_dict["type_distribution_enforced"]
            if "is_current_harm" in list(init_dict.keys()):
                is_current_harm = init_dict["is_current_harm"]
            if "T_mag" in list(init_dict.keys()):
                T_mag = init_dict["T_mag"]
            if "is_periodicity_rotor" in list(init_dict.keys()):
                is_periodicity_rotor = init_dict["is_periodicity_rotor"]
        # Set the properties (value check and convertion are done in setter)
        self.Kmesh_fineness = Kmesh_fineness
        self.Kgeo_fineness = Kgeo_fineness
        self.type_calc_leakage = type_calc_leakage
        self.file_name = file_name
        self.FEMM_dict_enforced = FEMM_dict_enforced
        self.is_get_meshsolution = is_get_meshsolution
        self.is_save_meshsolution_as_file = is_save_meshsolution_as_file
        self.is_sliding_band = is_sliding_band
        self.transform_list = transform_list
        self.rotor_dxf = rotor_dxf
        self.stator_dxf = stator_dxf
        self.import_file = import_file
        self.is_close_femm = is_close_femm
        self.nb_worker = nb_worker
        self.Rag_enforced = Rag_enforced
        self.is_set_previous = is_set_previous
        self.is_fast_draw = is_fast_draw
        self.is_calc_torque_energy = is_calc_torque_energy
        # Call Magnetics init
        super(MagFEMM, self).__init__(
            is_remove_slotS=is_remove_slotS,
            is_remove_slotR=is_remove_slotR,
            is_remove_ventS=is_remove_ventS,
            is_remove_ventR=is_remove_ventR,
            is_mmfs=is_mmfs,
            is_mmfr=is_mmfr,
            type_BH_stator=type_BH_stator,
            type_BH_rotor=type_BH_rotor,
            is_periodicity_t=is_periodicity_t,
            is_periodicity_a=is_periodicity_a,
            angle_stator_shift=angle_stator_shift,
            angle_rotor_shift=angle_rotor_shift,
            logger_name=logger_name,
            Slice_enforced=Slice_enforced,
            Nslices_enforced=Nslices_enforced,
            type_distribution_enforced=type_distribution_enforced,
            is_current_harm=is_current_harm,
            T_mag=T_mag,
            is_periodicity_rotor=is_periodicity_rotor,
        )
        # The class is frozen (in Magnetics init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        MagFEMM_str = ""
        # Get the properties inherited from Magnetics
        MagFEMM_str += super(MagFEMM, self).__str__()
        MagFEMM_str += "Kmesh_fineness = " + str(self.Kmesh_fineness) + linesep
        MagFEMM_str += "Kgeo_fineness = " + str(self.Kgeo_fineness) + linesep
        MagFEMM_str += "type_calc_leakage = " + str(self.type_calc_leakage) + linesep
        MagFEMM_str += 'file_name = "' + str(self.file_name) + '"' + linesep
        MagFEMM_str += "FEMM_dict_enforced = " + str(self.FEMM_dict_enforced) + linesep
        MagFEMM_str += (
            "is_get_meshsolution = " + str(self.is_get_meshsolution) + linesep
        )
        MagFEMM_str += (
            "is_save_meshsolution_as_file = "
            + str(self.is_save_meshsolution_as_file)
            + linesep
        )
        MagFEMM_str += "is_sliding_band = " + str(self.is_sliding_band) + linesep
        MagFEMM_str += (
            "transform_list = "
            + linesep
            + str(self.transform_list).replace(linesep, linesep + "\t")
            + linesep
        )
        if self.rotor_dxf is not None:
            tmp = self.rotor_dxf.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            MagFEMM_str += "rotor_dxf = " + tmp
        else:
            MagFEMM_str += "rotor_dxf = None" + linesep + linesep
        if self.stator_dxf is not None:
            tmp = (
                self.stator_dxf.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            )
            MagFEMM_str += "stator_dxf = " + tmp
        else:
            MagFEMM_str += "stator_dxf = None" + linesep + linesep
        MagFEMM_str += 'import_file = "' + str(self.import_file) + '"' + linesep
        MagFEMM_str += "is_close_femm = " + str(self.is_close_femm) + linesep
        MagFEMM_str += "nb_worker = " + str(self.nb_worker) + linesep
        MagFEMM_str += "Rag_enforced = " + str(self.Rag_enforced) + linesep
        MagFEMM_str += "is_set_previous = " + str(self.is_set_previous) + linesep
        MagFEMM_str += "is_fast_draw = " + str(self.is_fast_draw) + linesep
        MagFEMM_str += (
            "is_calc_torque_energy = " + str(self.is_calc_torque_energy) + linesep
        )
        return MagFEMM_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Magnetics
        if not super(MagFEMM, self).__eq__(other):
            return False
        if other.Kmesh_fineness != self.Kmesh_fineness:
            return False
        if other.Kgeo_fineness != self.Kgeo_fineness:
            return False
        if other.type_calc_leakage != self.type_calc_leakage:
            return False
        if other.file_name != self.file_name:
            return False
        if other.FEMM_dict_enforced != self.FEMM_dict_enforced:
            return False
        if other.is_get_meshsolution != self.is_get_meshsolution:
            return False
        if other.is_save_meshsolution_as_file != self.is_save_meshsolution_as_file:
            return False
        if other.is_sliding_band != self.is_sliding_band:
            return False
        if other.transform_list != self.transform_list:
            return False
        if other.rotor_dxf != self.rotor_dxf:
            return False
        if other.stator_dxf != self.stator_dxf:
            return False
        if other.import_file != self.import_file:
            return False
        if other.is_close_femm != self.is_close_femm:
            return False
        if other.nb_worker != self.nb_worker:
            return False
        if other.Rag_enforced != self.Rag_enforced:
            return False
        if other.is_set_previous != self.is_set_previous:
            return False
        if other.is_fast_draw != self.is_fast_draw:
            return False
        if other.is_calc_torque_energy != self.is_calc_torque_energy:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Magnetics
        diff_list.extend(
            super(MagFEMM, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Kmesh_fineness is not None
            and self._Kmesh_fineness is not None
            and np.isnan(other._Kmesh_fineness)
            and np.isnan(self._Kmesh_fineness)
        ):
            pass
        elif other._Kmesh_fineness != self._Kmesh_fineness:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Kmesh_fineness)
                    + ", other="
                    + str(other._Kmesh_fineness)
                    + ")"
                )
                diff_list.append(name + ".Kmesh_fineness" + val_str)
            else:
                diff_list.append(name + ".Kmesh_fineness")
        if (
            other._Kgeo_fineness is not None
            and self._Kgeo_fineness is not None
            and np.isnan(other._Kgeo_fineness)
            and np.isnan(self._Kgeo_fineness)
        ):
            pass
        elif other._Kgeo_fineness != self._Kgeo_fineness:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Kgeo_fineness)
                    + ", other="
                    + str(other._Kgeo_fineness)
                    + ")"
                )
                diff_list.append(name + ".Kgeo_fineness" + val_str)
            else:
                diff_list.append(name + ".Kgeo_fineness")
        if other._type_calc_leakage != self._type_calc_leakage:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_calc_leakage)
                    + ", other="
                    + str(other._type_calc_leakage)
                    + ")"
                )
                diff_list.append(name + ".type_calc_leakage" + val_str)
            else:
                diff_list.append(name + ".type_calc_leakage")
        if other._file_name != self._file_name:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._file_name)
                    + ", other="
                    + str(other._file_name)
                    + ")"
                )
                diff_list.append(name + ".file_name" + val_str)
            else:
                diff_list.append(name + ".file_name")
        if other._FEMM_dict_enforced != self._FEMM_dict_enforced:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._FEMM_dict_enforced)
                    + ", other="
                    + str(other._FEMM_dict_enforced)
                    + ")"
                )
                diff_list.append(name + ".FEMM_dict_enforced" + val_str)
            else:
                diff_list.append(name + ".FEMM_dict_enforced")
        if other._is_get_meshsolution != self._is_get_meshsolution:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_get_meshsolution)
                    + ", other="
                    + str(other._is_get_meshsolution)
                    + ")"
                )
                diff_list.append(name + ".is_get_meshsolution" + val_str)
            else:
                diff_list.append(name + ".is_get_meshsolution")
        if other._is_save_meshsolution_as_file != self._is_save_meshsolution_as_file:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_save_meshsolution_as_file)
                    + ", other="
                    + str(other._is_save_meshsolution_as_file)
                    + ")"
                )
                diff_list.append(name + ".is_save_meshsolution_as_file" + val_str)
            else:
                diff_list.append(name + ".is_save_meshsolution_as_file")
        if other._is_sliding_band != self._is_sliding_band:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_sliding_band)
                    + ", other="
                    + str(other._is_sliding_band)
                    + ")"
                )
                diff_list.append(name + ".is_sliding_band" + val_str)
            else:
                diff_list.append(name + ".is_sliding_band")
        if other._transform_list != self._transform_list:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._transform_list)
                    + ", other="
                    + str(other._transform_list)
                    + ")"
                )
                diff_list.append(name + ".transform_list" + val_str)
            else:
                diff_list.append(name + ".transform_list")
        if (other.rotor_dxf is None and self.rotor_dxf is not None) or (
            other.rotor_dxf is not None and self.rotor_dxf is None
        ):
            diff_list.append(name + ".rotor_dxf None mismatch")
        elif self.rotor_dxf is not None:
            diff_list.extend(
                self.rotor_dxf.compare(
                    other.rotor_dxf,
                    name=name + ".rotor_dxf",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.stator_dxf is None and self.stator_dxf is not None) or (
            other.stator_dxf is not None and self.stator_dxf is None
        ):
            diff_list.append(name + ".stator_dxf None mismatch")
        elif self.stator_dxf is not None:
            diff_list.extend(
                self.stator_dxf.compare(
                    other.stator_dxf,
                    name=name + ".stator_dxf",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._import_file != self._import_file:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._import_file)
                    + ", other="
                    + str(other._import_file)
                    + ")"
                )
                diff_list.append(name + ".import_file" + val_str)
            else:
                diff_list.append(name + ".import_file")
        if other._is_close_femm != self._is_close_femm:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_close_femm)
                    + ", other="
                    + str(other._is_close_femm)
                    + ")"
                )
                diff_list.append(name + ".is_close_femm" + val_str)
            else:
                diff_list.append(name + ".is_close_femm")
        if other._nb_worker != self._nb_worker:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._nb_worker)
                    + ", other="
                    + str(other._nb_worker)
                    + ")"
                )
                diff_list.append(name + ".nb_worker" + val_str)
            else:
                diff_list.append(name + ".nb_worker")
        if (
            other._Rag_enforced is not None
            and self._Rag_enforced is not None
            and np.isnan(other._Rag_enforced)
            and np.isnan(self._Rag_enforced)
        ):
            pass
        elif other._Rag_enforced != self._Rag_enforced:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Rag_enforced)
                    + ", other="
                    + str(other._Rag_enforced)
                    + ")"
                )
                diff_list.append(name + ".Rag_enforced" + val_str)
            else:
                diff_list.append(name + ".Rag_enforced")
        if other._is_set_previous != self._is_set_previous:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_set_previous)
                    + ", other="
                    + str(other._is_set_previous)
                    + ")"
                )
                diff_list.append(name + ".is_set_previous" + val_str)
            else:
                diff_list.append(name + ".is_set_previous")
        if other._is_fast_draw != self._is_fast_draw:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_fast_draw)
                    + ", other="
                    + str(other._is_fast_draw)
                    + ")"
                )
                diff_list.append(name + ".is_fast_draw" + val_str)
            else:
                diff_list.append(name + ".is_fast_draw")
        if other._is_calc_torque_energy != self._is_calc_torque_energy:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_calc_torque_energy)
                    + ", other="
                    + str(other._is_calc_torque_energy)
                    + ")"
                )
                diff_list.append(name + ".is_calc_torque_energy" + val_str)
            else:
                diff_list.append(name + ".is_calc_torque_energy")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Magnetics
        S += super(MagFEMM, self).__sizeof__()
        S += getsizeof(self.Kmesh_fineness)
        S += getsizeof(self.Kgeo_fineness)
        S += getsizeof(self.type_calc_leakage)
        S += getsizeof(self.file_name)
        if self.FEMM_dict_enforced is not None:
            for key, value in self.FEMM_dict_enforced.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.is_get_meshsolution)
        S += getsizeof(self.is_save_meshsolution_as_file)
        S += getsizeof(self.is_sliding_band)
        if self.transform_list is not None:
            for value in self.transform_list:
                S += getsizeof(value)
        S += getsizeof(self.rotor_dxf)
        S += getsizeof(self.stator_dxf)
        S += getsizeof(self.import_file)
        S += getsizeof(self.is_close_femm)
        S += getsizeof(self.nb_worker)
        S += getsizeof(self.Rag_enforced)
        S += getsizeof(self.is_set_previous)
        S += getsizeof(self.is_fast_draw)
        S += getsizeof(self.is_calc_torque_energy)
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

        # Get the properties inherited from Magnetics
        MagFEMM_dict = super(MagFEMM, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        MagFEMM_dict["Kmesh_fineness"] = self.Kmesh_fineness
        MagFEMM_dict["Kgeo_fineness"] = self.Kgeo_fineness
        MagFEMM_dict["type_calc_leakage"] = self.type_calc_leakage
        MagFEMM_dict["file_name"] = self.file_name
        MagFEMM_dict["FEMM_dict_enforced"] = (
            self.FEMM_dict_enforced.copy()
            if self.FEMM_dict_enforced is not None
            else None
        )
        MagFEMM_dict["is_get_meshsolution"] = self.is_get_meshsolution
        MagFEMM_dict["is_save_meshsolution_as_file"] = self.is_save_meshsolution_as_file
        MagFEMM_dict["is_sliding_band"] = self.is_sliding_band
        MagFEMM_dict["transform_list"] = (
            self.transform_list.copy() if self.transform_list is not None else None
        )
        if self.rotor_dxf is None:
            MagFEMM_dict["rotor_dxf"] = None
        else:
            MagFEMM_dict["rotor_dxf"] = self.rotor_dxf.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        if self.stator_dxf is None:
            MagFEMM_dict["stator_dxf"] = None
        else:
            MagFEMM_dict["stator_dxf"] = self.stator_dxf.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        MagFEMM_dict["import_file"] = self.import_file
        MagFEMM_dict["is_close_femm"] = self.is_close_femm
        MagFEMM_dict["nb_worker"] = self.nb_worker
        MagFEMM_dict["Rag_enforced"] = self.Rag_enforced
        MagFEMM_dict["is_set_previous"] = self.is_set_previous
        MagFEMM_dict["is_fast_draw"] = self.is_fast_draw
        MagFEMM_dict["is_calc_torque_energy"] = self.is_calc_torque_energy
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        MagFEMM_dict["__class__"] = "MagFEMM"
        return MagFEMM_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Kmesh_fineness_val = self.Kmesh_fineness
        Kgeo_fineness_val = self.Kgeo_fineness
        type_calc_leakage_val = self.type_calc_leakage
        file_name_val = self.file_name
        if self.FEMM_dict_enforced is None:
            FEMM_dict_enforced_val = None
        else:
            FEMM_dict_enforced_val = self.FEMM_dict_enforced.copy()
        is_get_meshsolution_val = self.is_get_meshsolution
        is_save_meshsolution_as_file_val = self.is_save_meshsolution_as_file
        is_sliding_band_val = self.is_sliding_band
        if self.transform_list is None:
            transform_list_val = None
        else:
            transform_list_val = self.transform_list.copy()
        if self.rotor_dxf is None:
            rotor_dxf_val = None
        else:
            rotor_dxf_val = self.rotor_dxf.copy()
        if self.stator_dxf is None:
            stator_dxf_val = None
        else:
            stator_dxf_val = self.stator_dxf.copy()
        import_file_val = self.import_file
        is_close_femm_val = self.is_close_femm
        nb_worker_val = self.nb_worker
        Rag_enforced_val = self.Rag_enforced
        is_set_previous_val = self.is_set_previous
        is_fast_draw_val = self.is_fast_draw
        is_calc_torque_energy_val = self.is_calc_torque_energy
        is_remove_slotS_val = self.is_remove_slotS
        is_remove_slotR_val = self.is_remove_slotR
        is_remove_ventS_val = self.is_remove_ventS
        is_remove_ventR_val = self.is_remove_ventR
        is_mmfs_val = self.is_mmfs
        is_mmfr_val = self.is_mmfr
        type_BH_stator_val = self.type_BH_stator
        type_BH_rotor_val = self.type_BH_rotor
        is_periodicity_t_val = self.is_periodicity_t
        is_periodicity_a_val = self.is_periodicity_a
        angle_stator_shift_val = self.angle_stator_shift
        angle_rotor_shift_val = self.angle_rotor_shift
        logger_name_val = self.logger_name
        if self.Slice_enforced is None:
            Slice_enforced_val = None
        else:
            Slice_enforced_val = self.Slice_enforced.copy()
        Nslices_enforced_val = self.Nslices_enforced
        type_distribution_enforced_val = self.type_distribution_enforced
        is_current_harm_val = self.is_current_harm
        T_mag_val = self.T_mag
        is_periodicity_rotor_val = self.is_periodicity_rotor
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Kmesh_fineness=Kmesh_fineness_val,
            Kgeo_fineness=Kgeo_fineness_val,
            type_calc_leakage=type_calc_leakage_val,
            file_name=file_name_val,
            FEMM_dict_enforced=FEMM_dict_enforced_val,
            is_get_meshsolution=is_get_meshsolution_val,
            is_save_meshsolution_as_file=is_save_meshsolution_as_file_val,
            is_sliding_band=is_sliding_band_val,
            transform_list=transform_list_val,
            rotor_dxf=rotor_dxf_val,
            stator_dxf=stator_dxf_val,
            import_file=import_file_val,
            is_close_femm=is_close_femm_val,
            nb_worker=nb_worker_val,
            Rag_enforced=Rag_enforced_val,
            is_set_previous=is_set_previous_val,
            is_fast_draw=is_fast_draw_val,
            is_calc_torque_energy=is_calc_torque_energy_val,
            is_remove_slotS=is_remove_slotS_val,
            is_remove_slotR=is_remove_slotR_val,
            is_remove_ventS=is_remove_ventS_val,
            is_remove_ventR=is_remove_ventR_val,
            is_mmfs=is_mmfs_val,
            is_mmfr=is_mmfr_val,
            type_BH_stator=type_BH_stator_val,
            type_BH_rotor=type_BH_rotor_val,
            is_periodicity_t=is_periodicity_t_val,
            is_periodicity_a=is_periodicity_a_val,
            angle_stator_shift=angle_stator_shift_val,
            angle_rotor_shift=angle_rotor_shift_val,
            logger_name=logger_name_val,
            Slice_enforced=Slice_enforced_val,
            Nslices_enforced=Nslices_enforced_val,
            type_distribution_enforced=type_distribution_enforced_val,
            is_current_harm=is_current_harm_val,
            T_mag=T_mag_val,
            is_periodicity_rotor=is_periodicity_rotor_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Kmesh_fineness = None
        self.Kgeo_fineness = None
        self.type_calc_leakage = None
        self.file_name = None
        self.FEMM_dict_enforced = None
        self.is_get_meshsolution = None
        self.is_save_meshsolution_as_file = None
        self.is_sliding_band = None
        self.transform_list = None
        if self.rotor_dxf is not None:
            self.rotor_dxf._set_None()
        if self.stator_dxf is not None:
            self.stator_dxf._set_None()
        self.import_file = None
        self.is_close_femm = None
        self.nb_worker = None
        self.Rag_enforced = None
        self.is_set_previous = None
        self.is_fast_draw = None
        self.is_calc_torque_energy = None
        # Set to None the properties inherited from Magnetics
        super(MagFEMM, self)._set_None()

    def _get_Kmesh_fineness(self):
        """getter of Kmesh_fineness"""
        return self._Kmesh_fineness

    def _set_Kmesh_fineness(self, value):
        """setter of Kmesh_fineness"""
        check_var("Kmesh_fineness", value, "float")
        self._Kmesh_fineness = value

    Kmesh_fineness = property(
        fget=_get_Kmesh_fineness,
        fset=_set_Kmesh_fineness,
        doc="""global coefficient to adjust mesh fineness in FEMM (1 : default , > 1 : finner , < 1 : less fine)

        :Type: float
        """,
    )

    def _get_Kgeo_fineness(self):
        """getter of Kgeo_fineness"""
        return self._Kgeo_fineness

    def _set_Kgeo_fineness(self, value):
        """setter of Kgeo_fineness"""
        check_var("Kgeo_fineness", value, "float")
        self._Kgeo_fineness = value

    Kgeo_fineness = property(
        fget=_get_Kgeo_fineness,
        fset=_set_Kgeo_fineness,
        doc="""global coefficient to adjust geometry fineness in FEMM (1 : default , > 1 : finner , < 1 : less fine)

        :Type: float
        """,
    )

    def _get_type_calc_leakage(self):
        """getter of type_calc_leakage"""
        return self._type_calc_leakage

    def _set_type_calc_leakage(self, value):
        """setter of type_calc_leakage"""
        check_var("type_calc_leakage", value, "int", Vmin=0, Vmax=1)
        self._type_calc_leakage = value

    type_calc_leakage = property(
        fget=_get_type_calc_leakage,
        fset=_set_type_calc_leakage,
        doc="""0 no leakage calculation /  1 calculation using single slot 

        :Type: int
        :min: 0
        :max: 1
        """,
    )

    def _get_file_name(self):
        """getter of file_name"""
        return self._file_name

    def _set_file_name(self, value):
        """setter of file_name"""
        check_var("file_name", value, "str")
        self._file_name = value

    file_name = property(
        fget=_get_file_name,
        fset=_set_file_name,
        doc="""Name of the file to save the FEMM model

        :Type: str
        """,
    )

    def _get_FEMM_dict_enforced(self):
        """getter of FEMM_dict_enforced"""
        return self._FEMM_dict_enforced

    def _set_FEMM_dict_enforced(self, value):
        """setter of FEMM_dict_enforced"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("FEMM_dict_enforced", value, "dict")
        self._FEMM_dict_enforced = value

    FEMM_dict_enforced = property(
        fget=_get_FEMM_dict_enforced,
        fset=_set_FEMM_dict_enforced,
        doc="""To enforce user-defined values for FEMM main parameters 

        :Type: dict
        """,
    )

    def _get_is_get_meshsolution(self):
        """getter of is_get_meshsolution"""
        return self._is_get_meshsolution

    def _set_is_get_meshsolution(self, value):
        """setter of is_get_meshsolution"""
        check_var("is_get_meshsolution", value, "bool")
        self._is_get_meshsolution = value

    is_get_meshsolution = property(
        fget=_get_is_get_meshsolution,
        fset=_set_is_get_meshsolution,
        doc="""To save FEA and mesh for latter post-procesing 

        :Type: bool
        """,
    )

    def _get_is_save_meshsolution_as_file(self):
        """getter of is_save_meshsolution_as_file"""
        return self._is_save_meshsolution_as_file

    def _set_is_save_meshsolution_as_file(self, value):
        """setter of is_save_meshsolution_as_file"""
        check_var("is_save_meshsolution_as_file", value, "bool")
        self._is_save_meshsolution_as_file = value

    is_save_meshsolution_as_file = property(
        fget=_get_is_save_meshsolution_as_file,
        fset=_set_is_save_meshsolution_as_file,
        doc="""To save FEA and mesh as h5 files to save memory

        :Type: bool
        """,
    )

    def _get_is_sliding_band(self):
        """getter of is_sliding_band"""
        return self._is_sliding_band

    def _set_is_sliding_band(self, value):
        """setter of is_sliding_band"""
        check_var("is_sliding_band", value, "bool")
        self._is_sliding_band = value

    is_sliding_band = property(
        fget=_get_is_sliding_band,
        fset=_set_is_sliding_band,
        doc="""0 to desactivate the sliding band

        :Type: bool
        """,
    )

    def _get_transform_list(self):
        """getter of transform_list"""
        return self._transform_list

    def _set_transform_list(self, value):
        """setter of transform_list"""
        if type(value) is int and value == -1:
            value = list()
        check_var("transform_list", value, "list")
        self._transform_list = value

    transform_list = property(
        fget=_get_transform_list,
        fset=_set_transform_list,
        doc="""List of dictionary to apply transformation on the machine surfaces. Key: label (to select the surface), type (rotate or translate), value (alpha or delta)

        :Type: list
        """,
    )

    def _get_rotor_dxf(self):
        """getter of rotor_dxf"""
        return self._rotor_dxf

    def _set_rotor_dxf(self, value):
        """setter of rotor_dxf"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "rotor_dxf"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            DXFImport = import_class("pyleecan.Classes", "DXFImport", "rotor_dxf")
            value = DXFImport()
        check_var("rotor_dxf", value, "DXFImport")
        self._rotor_dxf = value

        if self._rotor_dxf is not None:
            self._rotor_dxf.parent = self

    rotor_dxf = property(
        fget=_get_rotor_dxf,
        fset=_set_rotor_dxf,
        doc="""To use a dxf version of the rotor instead of build_geometry

        :Type: DXFImport
        """,
    )

    def _get_stator_dxf(self):
        """getter of stator_dxf"""
        return self._stator_dxf

    def _set_stator_dxf(self, value):
        """setter of stator_dxf"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "stator_dxf"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            DXFImport = import_class("pyleecan.Classes", "DXFImport", "stator_dxf")
            value = DXFImport()
        check_var("stator_dxf", value, "DXFImport")
        self._stator_dxf = value

        if self._stator_dxf is not None:
            self._stator_dxf.parent = self

    stator_dxf = property(
        fget=_get_stator_dxf,
        fset=_set_stator_dxf,
        doc="""To use a dxf version of the rotor instead of build_geometry

        :Type: DXFImport
        """,
    )

    def _get_import_file(self):
        """getter of import_file"""
        return self._import_file

    def _set_import_file(self, value):
        """setter of import_file"""
        check_var("import_file", value, "str")
        self._import_file = value

    import_file = property(
        fget=_get_import_file,
        fset=_set_import_file,
        doc="""To import an existing femm file

        :Type: str
        """,
    )

    def _get_is_close_femm(self):
        """getter of is_close_femm"""
        return self._is_close_femm

    def _set_is_close_femm(self, value):
        """setter of is_close_femm"""
        check_var("is_close_femm", value, "bool")
        self._is_close_femm = value

    is_close_femm = property(
        fget=_get_is_close_femm,
        fset=_set_is_close_femm,
        doc="""To close femm automatically after the simulation

        :Type: bool
        """,
    )

    def _get_nb_worker(self):
        """getter of nb_worker"""
        return self._nb_worker

    def _set_nb_worker(self, value):
        """setter of nb_worker"""
        check_var("nb_worker", value, "int")
        self._nb_worker = value

    nb_worker = property(
        fget=_get_nb_worker,
        fset=_set_nb_worker,
        doc="""To run FEMM in parallel (the parallelization is on the time loop)

        :Type: int
        """,
    )

    def _get_Rag_enforced(self):
        """getter of Rag_enforced"""
        return self._Rag_enforced

    def _set_Rag_enforced(self, value):
        """setter of Rag_enforced"""
        check_var("Rag_enforced", value, "float")
        self._Rag_enforced = value

    Rag_enforced = property(
        fget=_get_Rag_enforced,
        fset=_set_Rag_enforced,
        doc="""To enforce a different radius value for air-gap outputs

        :Type: float
        """,
    )

    def _get_is_set_previous(self):
        """getter of is_set_previous"""
        return self._is_set_previous

    def _set_is_set_previous(self, value):
        """setter of is_set_previous"""
        check_var("is_set_previous", value, "bool")
        self._is_set_previous = value

    is_set_previous = property(
        fget=_get_is_set_previous,
        fset=_set_is_set_previous,
        doc="""True set previous .ans result file in current .fem to use it as initialization and speed up calculation time

        :Type: bool
        """,
    )

    def _get_is_fast_draw(self):
        """getter of is_fast_draw"""
        return self._is_fast_draw

    def _set_is_fast_draw(self, value):
        """setter of is_fast_draw"""
        check_var("is_fast_draw", value, "bool")
        self._is_fast_draw = value

    is_fast_draw = property(
        fget=_get_is_fast_draw,
        fset=_set_is_fast_draw,
        doc="""True to use the symetry of the lamination to draw the machine faster

        :Type: bool
        """,
    )

    def _get_is_calc_torque_energy(self):
        """getter of is_calc_torque_energy"""
        return self._is_calc_torque_energy

    def _set_is_calc_torque_energy(self, value):
        """setter of is_calc_torque_energy"""
        check_var("is_calc_torque_energy", value, "bool")
        self._is_calc_torque_energy = value

    is_calc_torque_energy = property(
        fget=_get_is_calc_torque_energy,
        fset=_set_is_calc_torque_energy,
        doc="""True to calculate torque from integration of energy derivate over rotor elements

        :Type: bool
        """,
    )
