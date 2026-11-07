# Experimental dataclass generated from Generator/ClassesRef/Simulation/MagElmer.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
import subprocess
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from meshio import read

from .. import __version__
from ..Functions.get_path_binary import get_path_binary
from ..Functions.GMSH.draw_GMSH import draw_GMSH
from ..Functions.labels import (
    AIRBOX_R_LAB,
    AIRBOX_SL_LAB,
    AIRBOX_SR_LAB,
    AIRGAP_LAB,
    AR_T_LAB,
    AS_BL_LAB,
    AS_BR_LAB,
    AS_TL_LAB,
    AS_TR_LAB,
    BOT_LAB,
    HOLEM_LAB_S,
    HOLEV_LAB_S,
    LAM_LAB_S,
    MAG_LAB,
    NO_LAM_LAB,
    ROTOR_LAB,
    ROTOR_LAB_S,
    SBR_B_LAB,
    SBR_T_LAB,
    SBS_BL_LAB,
    SBS_BR_LAB,
    SBS_TL_LAB,
    SBS_TR_LAB,
    SHAFT_LAB,
    SHAFTSL_LAB,
    SHAFTSR_LAB,
    SLID_LAB,
    STATOR_LAB,
    STATOR_LAB_S,
    WIND_LAB_S,
    YSL_LAB,
    YSR_LAB,
    decode_label,
    get_obj_from_label,
    short_label,
)
from ..Functions.Winding.find_wind_phase_color import get_phase_id
from . import NotImplementedYetError
from .data_1d import Data1D
from .data_time import DataTime
from .dxf_import import DXFImport
from .machine_ipmsm import MachineIPMSM
from .machine_sipmsm import MachineSIPMSM
from .magnetics import Magnetics
from .mesh_solution import MeshSolution
from .mesh_vtk import MeshVTK
from .norm_ref import NormRef
from .out_mag_elmer import OutMagElmer
from .solution_data import SolutionData
from .solution_vector import SolutionVector
from .vector_field import VectorField


@dataclass(eq=False)
class MagElmer(Magnetics):
    """Magnetic module: Finite Element model with Elmer

    Attributes
    ----------
    Kmesh_fineness : float
        global coefficient to adjust mesh fineness (1 : default , > 1 : finner , < 1 : less fine)
        Default: 1
    Kgeo_fineness : float
        global coefficient to adjust geometry fineness (1 : default , > 1 : finner , < 1 : less fine)
        Default: 1
    file_name : str or None
        Name of the file to save the Elmer model
        Default: None
    FEA_dict : dict or None
        To enforce user-defined values for Elmer main parameters
        Default: {}
    is_get_mesh : bool
        To save FEA mesh for latter post-procesing
        Default: False
    is_save_FEA : bool
        To save FEA mesh and solution in a file
        Default: False
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
        To import an existing simulation file
        Default: None
    nb_worker : int
        To run Elmer in parallel (the parallelization is on the time loop)
        Default: 1
    """

    Kmesh_fineness: float = 1
    """global coefficient to adjust mesh fineness (1 : default , > 1 : finner , < 1 : less fine)"""
    Kgeo_fineness: float = 1
    """global coefficient to adjust geometry fineness (1 : default , > 1 : finner , < 1 : less fine)"""
    file_name: str | None = None
    """Name of the file to save the Elmer model"""
    FEA_dict: dict[str, Any] | None = field(default_factory=dict)
    """To enforce user-defined values for Elmer main parameters """
    is_get_mesh: bool = False
    """To save FEA mesh for latter post-procesing """
    is_save_FEA: bool = False
    """To save FEA mesh and solution in a file"""
    transform_list: list[Any] = field(default_factory=list)
    """List of dictionary to apply transformation on the machine surfaces. Key: label (to select the surface), type (rotate or translate), value (alpha or delta)"""
    rotor_dxf: DXFImport | None = None
    """To use a dxf version of the rotor instead of build_geometry"""
    stator_dxf: DXFImport | None = None
    """To use a dxf version of the rotor instead of build_geometry"""
    import_file: str | None = None
    """To import an existing simulation file"""
    nb_worker: int = 1
    """To run Elmer in parallel (the parallelization is on the time loop)"""

    # Inlined from Methods.Simulation.MagElmer.comp_flux_airgap
    def comp_flux_airgap(self, output, axes_dict, Is_val=None, Ir_val=None):
        """Build and solve Elmer model to calculate and store magnetic quantities

        Parameters
        ----------
        self : MagElmer
            a MagElmer object
        output : Output
            an Output object
        axes_dict: {Data}
            Dict of axes used for magnetic calculation
        """

        # Init output dict
        out_dict = {}
        if output.mag.internal is None:
            output.mag.internal = OutMagElmer()

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
        # Na = angle.size

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

        # Setup the Elmer simulation
        # Geometry building
        gmsh_filename = self.get_path_save_fea(output) + ".msh"
        if not self.import_file:  # True if None or len == 0
            self.get_logger().debug("Drawing machine in GMSH...")
            output.mag.internal.FEA_dict = draw_GMSH(
                output=output,
                sym=sym,
                boundary_prop=self._get_BP_dict(),
                is_lam_only_S=False,
                is_lam_only_R=False,
                user_mesh_dict=self.FEA_dict,
                is_sliding_band=True,
                is_airbox=True,
                path_save=gmsh_filename,
            )

        else:
            self.get_logger().debug("Reusing the FEA file: " + self.import_file)
            # output.mag.internal.FEA_dict = self.FEA_dict
            pass

        # post process GMSH mesh with ElmerGrid
        if not self.gen_elmer_mesh(output):
            print("Something went wrong!")

        # elmermesh_folder = self.get_path_save_fea(output)
        # cmd_elmergrid = [
        #     "ElmerGrid",
        #     "14",
        #     "2",
        #     gmsh_filename,
        #     "-2d",
        #     "-autoclean",
        #     "-names",
        #     "-out",
        #     elmermesh_folder,
        # ]
        # process_elmergrid = subprocess.Popen(
        #     cmd_elmergrid, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        # )
        # (stdout, stderr) = process_elmergrid.communicate()
        #
        # process_elmergrid.wait()
        # if process_elmergrid.returncode != 0:
        #     print(stdout)
        #     print(stderr)
        #     # pass

        # setup Elmer solver
        # TODO add respective functions or methods

        # Solve for all time step and store all the results in output
        Br, Bt, Bz, Tem, Phi_wind_stator = self.solve_FEA(
            output, sym, angle, time, angle_rotor, Is_val, Ir_val
        )

        # Store standards Magnetics outputs in out_dict
        out_dict["B_{rad}"] = Br
        out_dict["B_{circ}"] = Bt
        out_dict["B_{ax}"] = Bz
        out_dict["Tem"] = Tem
        out_dict["Phi_wind_stator"] = Phi_wind_stator

        # TODO store other Elmer outputs in out_dict

        return out_dict

    @staticmethod
    def _get_BP_dict():
        """Build the mapping of Pyleecan labels to magnetic Elmer boundaries."""
        rotor_label = ROTOR_LAB + "-0_"
        stator_label = STATOR_LAB + "-0_"
        return {
            AS_BR_LAB: "MASTER_ROTOR_BOUNDARY",
            AS_BL_LAB: "SLAVE_ROTOR_BOUNDARY",
            SBS_BR_LAB: "MASTER_ROTOR_BOUNDARY",
            SBS_BL_LAB: "SLAVE_ROTOR_BOUNDARY",
            SBR_B_LAB: "SB_ROTOR_BOUNDARY",
            rotor_label + YSR_LAB: "MASTER_ROTOR_BOUNDARY",
            rotor_label + YSL_LAB: "SLAVE_ROTOR_BOUNDARY",
            stator_label + YSR_LAB: "MASTER_STATOR_BOUNDARY",
            stator_label + YSL_LAB: "SLAVE_STATOR_BOUNDARY",
            SHAFTSR_LAB: "MASTER_ROTOR_BOUNDARY",
            SHAFTSL_LAB: "SLAVE_ROTOR_BOUNDARY",
            AS_TR_LAB: "MASTER_STATOR_BOUNDARY",
            AS_TL_LAB: "SLAVE_STATOR_BOUNDARY",
            AR_T_LAB: "AIRGAP_ARC_BOUNDARY",
            SBS_TR_LAB: "MASTER_STATOR_BOUNDARY",
            SBS_TL_LAB: "SLAVE_STATOR_BOUNDARY",
            SBR_T_LAB: "SB_STATOR_BOUNDARY",
            AIRBOX_SR_LAB: "MASTER_STATOR_BOUNDARY",
            AIRBOX_SL_LAB: "SLAVE_STATOR_BOUNDARY",
            AIRBOX_R_LAB: "VP0_BOUNDARY",
        }

    # Inlined from Methods.Simulation.MagElmer.gen_elmer_mesh
    def gen_elmer_mesh(self, output):
        """Call ElmerGrid process to convert mesh from Gmsh format to Elmer's compatible

        Parameters
        ----------
        self : Magnetic
            a Magnetic object
        output : Output
            an Output object (to update)

        Returns
        -------
        success: {Boolean}
            Status flag
        """
        # ElmerGrid v8.4 must be installed and in the PATH
        project_name = self.get_path_save_fea(output)
        gmsh_filename = project_name + ".msh"
        elmermesh_folder = project_name
        ElmerGrid_binary = get_path_binary("ElmerGrid")
        cmd_elmergrid = [
            ElmerGrid_binary,
            "14",
            "2",
            gmsh_filename,
            "-2d",
            "-autoclean",
            "-names",
            "-out",
            elmermesh_folder,
        ]
        self.get_logger().info(
            "Calling ElmerGrid: " + " ".join(map(str, cmd_elmergrid))
        )
        elmergrid = subprocess.Popen(
            cmd_elmergrid, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        (stdout, stderr) = elmergrid.communicate()
        elmergrid.wait()
        self.get_logger().info(stdout.decode("UTF-8"))
        if elmergrid.returncode != 0:
            self.get_logger().info("ElmerGrid [Error]: " + stderr.decode("UTF-8"))
            return False
        elmergrid.terminate()
        self.get_logger().info("ElmerGrid call complete!")

        return True

    # Inlined from Methods.Simulation.MagElmer.get_meshsolution
    def get_meshsolution(self, output):
        """Build the MeshSolution objects from the FEA outputs.

        Parameters
        ----------
        self : MagElmer
            a MagElmer object
        output: Output
            An Output object

        Returns
        -------
        meshsol: MeshSolution
            a MeshSolution object with Elmer outputs at every time step
        """
        project_name = self.get_path_save_fea(output)
        elmermesh_folder = project_name
        meshsol = MeshSolution(label="Elmer MagnetoDynamics")
        if not self.is_get_mesh or not self.is_save_FEA:
            self.get_logger().info("MagElmer: MeshSolution is not stored by request.")
            return False

        meshvtk = MeshVTK(path=elmermesh_folder, name="step_t0002", format="vtu")
        meshsol.mesh = meshvtk

        result_filename = os.path.join(elmermesh_folder, "step_t0002.vtu")
        meshsolvtu = read(result_filename)
        # pt_data = meshsolvtu.point_data
        cell_data = meshsolvtu.cell_data

        # indices = arange(meshsolvtu.points.shape[0])
        indices = np.arange(
            meshsolvtu.cells[0].data.shape[0] + meshsolvtu.cells[1].data.shape[0]
        )

        Indices = Data1D(name="indice", values=indices, is_components=True)
        # store_dict = {
        #     "magnetic vector potential": {
        #         "name": "Magnetic Vector Potential A",
        #         "unit": "Wb",
        #         "symbol": "A",
        #         "norm": 1,
        #     },
        #     "magnetic flux density": {
        #         "name": "Magnetic Flux Density B",
        #         "unit": "T",
        #         "symbol": "B",
        #         "norm": 1,
        #     },
        #     "magnetic field strength": {
        #         "name": "Magnetic Field H",
        #         "unit": "A/m",
        #         "symbol": "H",
        #         "norm": 1,
        #     },
        #     "current density": {
        #         "name": "Current Density J",
        #         "unit": "A/mm2",
        #         "symbol": "J",
        #         "norm": 1,
        #     }
        # }
        store_dict = {
            "magnetic flux density e": {
                "name": "Magnetic Flux Density B",
                "unit": "T",
                "symbol": "B",
                "norm": 1,
            },
            "magnetic vector potential e": {
                "name": "Magnetic Vector Potential A",
                "unit": "Wb",
                "symbol": "A",
                "norm": 1,
            },
            "magnetic field strength e": {
                "name": "Magnetic Field H",
                "unit": "A/m",
                "symbol": "H",
                "norm": 1,
            },
            "current density e": {
                "name": "Current Density J",
                "unit": "A/mm2",
                "symbol": "J",
                "norm": 1,
            },
        }
        comp_ext = ["x", "y", "z"]
        sol_dict = {}
        # for key, value in pt_data.items():
        for key, value in cell_data.items():
            if key in store_dict:
                # siz = value.shape[1]
                siz = value[0].shape[1]
                if siz > 3:
                    print("Some Message")
                    siz = 3
                components = []
                comp_name = []
                values = np.append(value[0], value[1], axis=0)
                for i in range(siz):
                    if siz == 1:
                        ext = ""
                    else:
                        ext = comp_ext[i]

                    data = DataTime(
                        name=store_dict[key]["name"] + ext,
                        unit=store_dict[key]["unit"],
                        symbol=store_dict[key]["symbol"] + ext,
                        axes=[Indices],
                        # values=value[:, i],
                        values=values[:, i],
                        normalizations={"ref": NormRef(ref=store_dict[key]["norm"])},
                    )

                    components.append(data)
                    comp_name.append("comp_" + ext)

                if siz == 1:
                    field = components[0]
                    sol_dict[store_dict[key]["symbol"]] = SolutionData(
                        field=field,
                        # type_element="point",
                        type_element="triangle",
                        label=store_dict[key]["symbol"],
                    )
                else:
                    comps = {}
                    for i in range(siz):
                        comps[comp_name[i]] = components[i]
                    field = VectorField(
                        name=store_dict[key]["name"],
                        symbol=store_dict[key]["symbol"],
                        components=comps,
                    )
                    sol_dict[store_dict[key]["symbol"]] = SolutionVector(
                        field=field,
                        # type_element="point",
                        type_element="triangle",
                        label=store_dict[key]["symbol"],
                    )

        meshsol.solution_dict = sol_dict
        output.mag.meshsolution = meshsol

        return True

    # Inlined from Methods.Simulation.MagElmer.get_path_save
    def get_path_save(self, output):
        """Return the path to save the Elmer simulation

        Parameters
        ----------
        self : MagElmer
            a MagElmer object
        output : Output
            an Output object

            Returns
        -------
        save_path: str
            Path to save the Elmer simulation

        """
        path_res = output.get_path_result()

        save_dir = os.path.join(path_res, "Elmer")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        return save_dir

    # Inlined from Methods.Simulation.MagElmer.get_path_save_fea
    def get_path_save_fea(self, output):
        """Return the path to save the Elmer simulation

        Parameters
        ----------
        self : MagElmer
            a MagElmer object
        output : Output
            an Output object

            Returns
        -------
        save_path: str
            Path to save the .fem file

        """
        save_dir = self.get_path_save(output)

        # if self.file_name not in [None, ""]:
        #     if self.file_name[-4:] != ".fem":
        #         file_name = self.file_name + ".fem"
        #     else:
        #         file_name = self.file_name
        # elif output.simu.machine.name not in [None, ""]:
        #     file_name = output.simu.machine.name + "_model.fem"
        # elif output.simu.name not in [None, ""]:
        #     file_name = output.simu.name + "_model.fem"
        # else:  # Default name
        #     file_name = "FEMM_simulation.fem"
        file_name = "ELMER_simulation"

        return os.path.join(save_dir, file_name)

    # Inlined from Methods.Simulation.MagElmer.solve_FEA
    def solve_FEA(self, output, sym, angle, time, angle_rotor, Is, Ir):
        """
        Solve Elmer model to calculate airgap flux density, torque instantaneous/average/ripple values,
        flux induced in stator windings and flux density, field and permeability maps

        Parameters
        ----------
        self: MagElmer
            A MagElmer object
        output: Output
            An Output object
        sym: int
            Spatial symmetry factor
        time: ndarray
            Time vector for calculation
        angle: ndarray
            Angle vector for calculation
        Is : ndarray
            Stator current matrix (qs,Nt) [A]
        Ir : ndarray
            Stator current matrix (qs,Nt) [A]
        angle_rotor: ndarray
            Rotor angular position vector (Nt,)
        """

        project_name = self.get_path_save_fea(output)
        elmermesh_folder = project_name
        mesh_names_file = os.path.join(project_name, "mesh.names")
        boundaries = {}
        bodies = {}
        machine = output.simu.machine
        BHs = output.geo.stator.BH_curve  # Stator B(H) curve
        BHr = output.geo.rotor.BH_curve  # Rotor B(H) curve
        # Is = output.elec.Is  # Stator currents waveforms
        # Ir = output.elec.Ir  # Rotor currents waveforms
        Speed = output.elec.OP.get_N0()
        rotor_mat_file = os.path.join(project_name, "rotor_material.pmf")
        stator_mat_file = os.path.join(project_name, "stator_material.pmf")

        # TO-DO: Time vector must be greater than one
        timesize_str = np.array2string(
            np.diff(time), separator=" ", formatter={"float_kind": lambda x: "%.2e" % x}
        )
        time = np.append(time, time[1] + time[-1])
        timesize_str = np.array2string(
            np.diff(time), separator=" ", formatter={"float_kind": lambda x: "%.2e" % x}
        )
        timelen = len(time) - 1
        ones_str = np.array2string(
            np.ones(timelen), separator=" ", formatter={"int": lambda x: "%d" % x}
        )
        timeinterval_str = ones_str.replace(".", "")

        with open(mesh_names_file, "rt") as f:
            for line in f:
                fields = line.strip().split()
                if fields[0] == "$":
                    field_name = fields[1]
                    field_value = fields[3]
                    # update dictionary
                    # _settings['Geometry'][field_name] = field_value
                    if field_name.count("BOUNDARY"):
                        boundaries[field_name] = field_value
                    else:
                        bodies[field_name] = {
                            "id": field_value,
                            "mat": 1,  # Air by Default
                            "eq": 1,  # RigidMeshMapper by Default
                            "bf": None,
                            "tg": None,
                        }

        with open(rotor_mat_file, "wt") as ro:
            ro.write(f"! File Generated by pyleecan v{__version__}\n")
            ro.write(
                f"! Material Name: {machine.rotor.mat_type.name}\n"
                "! B-H Curve Rotor Material\n"
                "Electric Conductivity = 0\n"
                "H-B Curve = Variable coupled iter\n"
                " Real\t\tCubic Monotone\n"
            )
            ro.writelines(
                f"   {BHr[ii][1]}\t\t{BHr[ii][0]}\n" for ii in range(BHr.shape[0])
            )
            ro.write("End\n")

        with open(stator_mat_file, "wt") as ro:
            ro.write(f"! File Generated by pyleecan v{__version__}\n")
            ro.write(
                f"! Material Name: {machine.stator.mat_type.name}\n"
                "! B-H Curve Stator Material\n"
                "Electric Conductivity = 0\n"
                "H-B Curve = Variable coupled iter\n"
                " Real\t\tCubic Monotone\n"
            )
            ro.writelines(
                f"   {BHs[ii][1]}\t\t{BHs[ii][0]}\n" for ii in range(BHs.shape[0])
            )
            ro.write("End\n")

        elmer_sim_file = os.path.join(project_name, "pyleecan_elmer.sif")
        pp = machine.stator.winding.p
        wind_mat = machine.stator.winding.get_connection_mat(machine.stator.slot.Zs)
        surf_wind = machine.stator.slot.comp_surface_active()
        ror = machine.rotor.comp_radius_mec()
        sir = machine.stator.comp_radius_mec()
        with open(elmer_sim_file, "wt") as fo:
            fo.write(f"! File Generated by pyleecan v{__version__}\n")
            fo.write(f"$ WM = 2*pi*{Speed}/60        ! Mechanical Frequency [rad/s]\n")
            fo.write(f"$ PP = {pp}                ! Pole pairs\n")
            fo.write("$ WE = PP*WM              ! Electrical Frequency [Hz]\n")

            if isinstance(machine, MachineSIPMSM):
                # magnet_0 = machine.rotor.slot.magnet[0]
                magnet_0 = machine.rotor.magnet
            elif isinstance(machine, MachineIPMSM):
                magnet_dict = machine.rotor.hole[0].get_magnet_dict()
                magnet_0 = magnet_dict["magnet_0"]
            else:
                self.get_logger().info(
                    "ElmerSolver [Error]: Unsupported Machine Geometry"
                )
                return False

            surf_list = machine.build_geometry(sym=sym)
            pm_index = 6
            Mangle = []
            Ncond_Aplus = 1
            Ncond_Aminus = 1
            Ncond_Bplus = 1
            Ncond_Bminus = 1
            Ncond_Cplus = 1
            Ncond_Cminus = 1
            Ncond_Dplus = 1
            Ncond_Dminus = 1
            Ncond_Eplus = 1
            Ncond_Eminus = 1
            Ncond_Fplus = 1
            Ncond_Fminus = 1
            Npcp = machine.stator.winding.Npcp
            for surf in surf_list:
                label = short_label(surf.label)
                label_dict = decode_label(label)
                point_ref = surf.point_ref
                if HOLEM_LAB_S in label_dict["surf_type"]:  # LamHole
                    mag_obj = get_obj_from_label(machine, label_dict=label_dict)
                    if mag_obj.type_magnetization == 1:  # Parallel
                        magnetization_type = "parallel"
                        # calculate pole angle and angle of pole middle
                        T_id = label_dict["T_id"]
                        hole = mag_obj.parent
                        Zh = hole.Zh
                        alpha_p = 360 / Zh
                        mag_0 = (
                            np.floor_divide(np.angle(point_ref, deg=True), alpha_p)
                            + 0.5
                        ) * alpha_p

                        mag_dict = hole.comp_magnetization_dict()
                        mag = mag_0 + mag_dict["magnet_" + str(T_id)] * 180 / np.pi
                        # modifiy magnetisation of south poles
                        if (label_dict["S_id"] % 2) == 1:
                            mag = mag + 180
                    else:
                        raise NotImplementedYetError(
                            "Only parallele magnetization are available for HoleMagnet"
                        )
                    if bodies.get(label, None) is not None:
                        Mangle.append(mag)
                        bodies[label]["mat"] = pm_index
                        bodies[label]["eq"] = 1
                        bodies[label]["bf"] = 1
                        bodies[label]["tg"] = 1
                        pm_index = pm_index + 1
                elif MAG_LAB in label_dict["surf_type"]:
                    mag_obj = get_obj_from_label(machine, label_dict=label_dict)
                    if (
                        mag_obj.type_magnetization == 0
                        and (label_dict["S_id"] % 2) == 0
                    ):
                        mag = 0  # North pole magnet
                        magnetization_type = "radial"
                    elif mag_obj.type_magnetization == 0:
                        mag = 180  # South pole magnet
                        magnetization_type = "radial"
                    elif (
                        mag_obj.type_magnetization == 1
                        and (label_dict["S_id"] % 2) == 0
                    ):
                        mag = np.angle(point_ref) * 180 / np.pi  # North pole magnet
                        magnetization_type = "parallel"
                    elif mag_obj.type_magnetization == 1:
                        mag = (
                            np.angle(point_ref) * 180 / np.pi + 180
                        )  # South pole magnet
                        magnetization_type = "parallel"
                    elif mag_obj.type_magnetization == 2:
                        Zs = mag_obj.parent.slot.Zs
                        mag = str(-(Zs / 2 - 1)) + " * theta + 90 "
                        magnetization_type = "hallback"
                    else:
                        continue
                    if bodies.get(label, None) is not None:
                        Mangle.append(mag)
                        bodies[label]["mat"] = pm_index
                        bodies[label]["eq"] = 1
                        bodies[label]["bf"] = 1
                        bodies[label]["tg"] = 1
                        pm_index = pm_index + 1
                elif WIND_LAB_S in label_dict["surf_type"]:
                    lam_obj = get_obj_from_label(machine, label_dict=label_dict)
                    wind_mat = lam_obj.winding.get_connection_mat(lam_obj.get_Zs())
                    Nrad_id = label_dict["R_id"]  # zone radial coordinate
                    Ntan_id = label_dict["T_id"]  # zone tangential coordinate
                    Zs_id = label_dict["S_id"]  # Zone slot number coordinate
                    # Get the phase value in the correct slot zone
                    q_id = get_phase_id(wind_mat, Nrad_id, Ntan_id, Zs_id)
                    Ncond = wind_mat[Nrad_id, Ntan_id, Zs_id, q_id]
                    s = np.sign(Ncond)
                    if bodies.get(label, None) is not None:
                        bodies[label]["mat"] = 5
                        bodies[label]["eq"] = 1
                        if q_id == 0 and s == 1:
                            bodies[label]["bf"] = 2
                            Ncond_Aplus = abs(Ncond)
                        elif q_id == 0 and s == -1:
                            bodies[label]["bf"] = 3
                            Ncond_Aminus = abs(Ncond)
                        elif q_id == 1 and s == 1:
                            bodies[label]["bf"] = 4
                            Ncond_Bplus = abs(Ncond)
                        elif q_id == 1 and s == -1:
                            bodies[label]["bf"] = 5
                            Ncond_Bminus = abs(Ncond)
                        elif q_id == 2 and s == 1:
                            bodies[label]["bf"] = 6
                            Ncond_Cplus = abs(Ncond)
                        elif q_id == 2 and s == -1:
                            bodies[label]["bf"] = 7
                            Ncond_Cminus = abs(Ncond)
                        elif q_id == 3 and s == 1:
                            bodies[label]["bf"] = 8
                            Ncond_Dplus = abs(Ncond)
                        elif q_id == 3 and s == -1:
                            bodies[label]["bf"] = 9
                            Ncond_Dminus = abs(Ncond)
                        elif q_id == 4 and s == 1:
                            bodies[label]["bf"] = 10
                            Ncond_Eplus = abs(Ncond)
                        elif q_id == 4 and s == -1:
                            bodies[label]["bf"] = 11
                            Ncond_Eminus = abs(Ncond)
                        elif q_id == 5 and s == 1:
                            bodies[label]["bf"] = 12
                            Ncond_Fplus = abs(Ncond)
                        elif q_id == 5 and s == -1:
                            bodies[label]["bf"] = 13
                            Ncond_Fminus = abs(Ncond)
                        else:
                            pass
                elif (
                    LAM_LAB_S in label_dict["surf_type"]
                    and ROTOR_LAB_S in label_dict["lam_label"]
                    and bodies.get(label, None) is not None
                ):
                    bodies[label]["mat"] = 4
                    bodies[label]["eq"] = 1
                    bodies[label]["bf"] = 1
                    bodies[label]["tg"] = 1
                elif (
                    LAM_LAB_S in label_dict["surf_type"]
                    and STATOR_LAB_S in label_dict["lam_label"]
                    and bodies.get(label, None) is not None
                ):
                    bodies[label]["mat"] = 3
                    bodies[label]["eq"] = 1
                elif (
                    SHAFT_LAB in label_dict["surf_type"]
                    and bodies.get(label, None) is not None
                ) or (
                    HOLEV_LAB_S in label_dict["surf_type"]
                    and bodies.get(label, None) is not None
                ):
                    bodies[label]["mat"] = 1
                    bodies[label]["eq"] = 1
                    bodies[label]["bf"] = 1
                    bodies[label]["tg"] = 1
                else:
                    pass

            # The following bodies are not in the dictionary
            bodies[ROTOR_LAB + "-0_" + AIRGAP_LAB + BOT_LAB]["bf"] = 1
            bodies[NO_LAM_LAB + "_" + SLID_LAB + BOT_LAB]["bf"] = (
                1  # Sliding band bottom
            )

            No_Magnets = pm_index - 6
            magnet_temp = self.T_mag
            Hcm20 = magnet_0.mat_type.mag.get_Hc()
            Br = magnet_0.mat_type.mag.get_Brm(T_op=self.T_mag)
            magnet_permeability = magnet_0.mat_type.mag.mur_lin
            conductivity_m = magnet_0.mat_type.elec.get_conductivity(
                T_op=magnet_temp, T_ref=20.0
            )

            skip_steps = 1  # Fixed for now
            degrees_step = 1  # Fixed for now
            current_angle = 0 - pp * degrees_step * skip_steps
            angle_shift = self.angle_rotor_shift - self.angle_stator_shift
            rotor_init_pos = machine.comp_angle_rotor_initial() + angle_shift
            rotor_d_axis = machine.rotor.comp_angle_d_axis() * 180.0 / np.pi
            Ncond = 1  # Fixed for Now
            Cp = 1  # Fixed for Now
            qs = len(machine.stator.get_name_phase())

            fo.write(
                f"$ H_PM = {round(Hcm20, 2)}              ! Magnetization at 20 deg C [A/m]\n"
            )
            fo.write(f"$ Shift = 2*pi/{qs}        ! N-phase machine [rad]\n")
            fo.write(
                f"$ Gamma = {round(current_angle, 2)}*pi/180      ! Current Angle [rad]\n"
            )
            fo.write(f"$ Ncond = {Ncond}             ! Conductors per coil\n")
            fo.write(f"$ Cp = {Cp}                ! Parallel paths\n")
            fo.write(f"$ Is = {0.0}                ! Stator current [A]\n")
            fo.write(f"$ Aaxis = {0.0}             ! Axis Coil A [deg]\n")
            fo.write(
                f"$ Carea = {surf_wind}             ! Coil Side Conductor Area [m2]\n"
            )

            fo.writelines(
                f"$ Mangle{mm} = {round(Mangle[mm - 1], 2)}     ! Magnetization Angle [deg]\n"
                for mm in range(1, No_Magnets + 1)
            )

            fo.write(f"$ Nsteps = {2}            !\n")
            fo.write(f"$ StepDegrees = {degrees_step}       !\n")
            fo.write("$ DegreesPerSec = WM*180.0/pi  !\n")
            fo.write(f"$ RotorInitPos = {round(rotor_init_pos * 180.0 / np.pi, 2)}!\n")

            fo.write(
                "\nHeader\n"
                "\tCHECK KEYWORDS Warn\n"
                f'\tMesh DB "{elmermesh_folder}"\n'
                '\tInclude Path "."\n'
                f'\tResults Directory "{elmermesh_folder}"\n'
                "End\n"
            )

            fo.write("\nConstants\n\tPermittivity of Vacuum = 8.8542e-12\nEnd\n")

            fo.write(
                "\nSimulation\n"
                "\tMax Output Level = 4\n"
                "\tCoordinate System = Cartesian 2D\n"
                f"\tCoordinate Scaling = {1.0}\n"
                "\tSimulation Type = Transient\n"
                "\tTimestepping Method = BDF\n"
                "\tBDF Order = 2\n"
                #                 "\tTimestep Sizes = $ (StepDegrees / DegreesPerSec)  ! sampling time\n"
                #                 "\tTimestep Intervals = $ Nsteps              ! steps\n"
                #                 "\tOutput Intervals = 1\n"
                f"\tTimestep Sizes({timelen}) = {timesize_str[1:-1]}\n"
                f"\tTimestep Intervals({timelen}) = {timeinterval_str[1:-1]}\n"
                "\tUse Mesh Names = Logical True\n"
                "End\n"
            )

            fo.write("\n!--- MATERIALS ---\n")
            fo.write(
                "Material 1\n"
                '\tName = "Air"\n'
                "\tRelative Permeability = 1\n"
                "\tElectric Conductivity = 0\n"
                "End\n"
            )

            fo.write(
                "\nMaterial 2\n"
                '\tName = "Insulation"\n'
                "\tRelative Permeability = 1\n"
                "\tElectric Conductivity = 0\n"
                "End\n"
            )

            fo.write(
                "\nMaterial 3\n"
                '\tName = "StatorMaterial"\n'
                f'\tInclude "{stator_mat_file}"\n'
                "End\n"
            )

            fo.write(
                "\nMaterial 4\n"
                '\tName = "RotorMaterial"\n'
                f'\tInclude "{rotor_mat_file}"\n'
                "End\n"
            )

            winding_temp = 20.0  # Fixed for Now
            conductivity = (
                machine.stator.winding.conductor.cond_mat.elec.get_conductivity(
                    T_op=winding_temp, T_ref=20
                )
            )

            fo.write(
                "\nMaterial 5\n"
                '\tName = "Copper"\n'
                "\tRelative Permeability = 1\n"
                f"\tElectric Conductivity = {round(conductivity, 2)}\n"
                "End\n"
            )

            magnets_per_pole = No_Magnets  # TO-DO: Assumes only one pole drawn
            for m in range(1, magnets_per_pole + 1):
                mat_number = 5 + m
                if magnetization_type == "parallel":
                    fo.write(
                        "\nMaterial {0}\n"
                        '\tName = "PM_{1}"\n'
                        "\tRelative Permeability = {2}\n"
                        "\tMagnetization 1 = Variable time, timestep size\n"
                        '\t\tReal MATC  "H_PM*cos(WM*(tx(0)-tx(1)) + {3}*pi/PP + {3}*pi + (RotorInitPos + Mangle{1})*pi/180)"\n'
                        "\tMagnetization 2 = Variable time, timestep size\n"
                        '\t\tReal MATC "H_PM*sin(WM*(tx(0)-tx(1)) + {3}*pi/PP + {3}*pi + (RotorInitPos + Mangle{1})*pi/180)"\n'
                        "\tElectric Conductivity = {4}\n"
                        "End\n".format(
                            mat_number,
                            m,
                            magnet_permeability,
                            int((m - 1) / magnets_per_pole),
                            round(conductivity_m, 2),
                        )
                    )
                elif magnetization_type == "radial":
                    fo.write(
                        f"\nMaterial {mat_number}\n"
                        f'\tName = "PM_{m}"\n'
                        f"\tRelative Permeability = {magnet_permeability}\n"
                        "\tMagnetization 1 = Variable Coordinate\n"
                        f'\t\tReal MATC  "H_PM*cos(atan2(tx(1),tx(0)) + {m - 1}*pi + Mangle{m}*pi/180)"\n'
                        "\tMagnetization 2 = Variable Coordinate\n"
                        f'\t\tReal MATC "H_PM*sin(atan2(tx(1),tx(0)) + {m - 1}*pi + Mangle{m}*pi/180)"\n'
                        f"\tElectric Conductivity = {round(conductivity_m, 2)}\n"
                        "End\n"
                    )
                elif magnetization_type == "perpendicular":
                    fo.write(
                        "\nMaterial {0}\n"
                        '\tName = "PM_{1}"\n'
                        "\tRelative Permeability = {2}\n"
                        "\tMagnetization 1 = Variable time, timestep size\n"
                        '\t\tReal MATC  "H_PM*cos(WM*(tx(0)-tx(1)) + {3}*pi/PP + {3}*pi + Aaxis*pi/180 + (Mangle{1}*pi/180))"\n'
                        "\tMagnetization 2 = Variable time, timestep size\n"
                        '\t\tReal MATC "H_PM*sin(WM*(tx(0)-tx(1)) + {3}*pi/PP + {3}*pi + Aaxis*pi/180 + (Mangle{1}*pi/180))"\n'
                        "\tElectric Conductivity = {4}\n"
                        "End\n".format(
                            mat_number,
                            m,
                            magnet_permeability,
                            int((m - 1) / magnets_per_pole),
                            round(conductivity_m, 2),
                        )
                    )
                else:
                    fo.write(
                        "\nMaterial {0}\n"
                        '\tName = "PM_{1}"\n'
                        "\tRelative Permeability = {2}\n"
                        "\tElectric Conductivity = {4}\n"
                        "End\n".format(
                            mat_number, m, magnet_permeability, round(conductivity_m, 2)
                        )
                    )

            fo.write("\n!--- BODY FORCES ---\n")

            # fo.write("Body Force 1\n"
            #          "\tName = \"BodyForce_Rotation\"\n"
            #          "\t$omega = (180/pi)*WM\n"
            #          "\tMesh Rotate 3 = Variable time, timestep size\n"
            #          "\t\tReal MATC \"omega*(tx(0)-tx(1)) + RotorInitPos\"\n"
            #          "End\n")
            fo.write(
                "Body Force 1\n"
                '\tName = "BodyForce_Rotation"\n'
                "\tMesh Rotate 3 = Variable time\n"
                "\t\tReal\n"
                "\t\t0.0\t\t0.0\n"
            )
            fo.writelines(
                f"\t\t{time[tt]:.2e}\t\t{angle_rotor[tt - 1] * 180.0 / np.pi:.3f}\n"
                for tt in range(1, timelen + 1)
            )
            fo.write("\tEnd\nEnd\n")

            # fo.write("Body Force 2\n"
            #          "\tName = \"J_A_PLUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) + Gamma)\"\n"
            #          "End\n".format(Ncond_Aplus))

            # fo.write("Body Force 3\n"
            #          "\tName = \"J_A_MINUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"-(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) + Gamma)\"\n"
            #          "End\n".format(Ncond_Aminus))

            # fo.write("Body Force 4\n"
            #          "\tName = \"J_B_PLUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Bplus))
            #
            # fo.write("Body Force 5\n"
            #          "\tName = \"J_B_MINUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"-(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Bminus))
            #
            # fo.write("Body Force 6\n"
            #          "\tName = \"J_C_PLUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - 2*Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Cplus))
            #
            # fo.write("Body Force 7\n"
            #          "\tName = \"J_C_MINUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"-(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - 2*Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Cminus))
            #
            # fo.write("Body Force 8\n"
            #          "\tName = \"J_D_PLUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - 3*Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Dplus))
            #
            # fo.write("Body Force 9\n"
            #          "\tName = \"J_D_MINUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"-(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - 3*Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Dminus))
            #
            # fo.write("Body Force 10\n"
            #          "\tName = \"J_E_PLUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - 4*Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Eplus))
            #
            # fo.write("Body Force 11\n"
            #          "\tName = \"J_E_MINUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"-(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - 4*Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Eminus))
            #
            # fo.write("Body Force 12\n"
            #          "\tName = \"J_F_PLUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - 5*Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Fplus))
            #
            # fo.write("Body Force 13\n"
            #          "\tName = \"J_F_MINUS\"\n"
            #          "\tCurrent Density = Variable time, timestep size\n"
            #          "\t\tReal MATC \"-(Is/Carea) * ({0}/Cp) * sin(WE * (tx(0)-tx(1)) - 5*Shift + Gamma)\"\n"
            #          "End\n".format(Ncond_Fminus))

            fo.write(
                "Body Force 2\n"
                '\tName = "J_A_PLUS"\n'
                "\tCurrent Density = Variable time\n"
                "\t\tReal\n"
                "\t\t0.0\t\t0.0\n"
            )
            fo.writelines(
                f"\t\t{time[tt]:.2e}\t\t{Ncond_Aplus * Is[0, tt - 1] / surf_wind:.3f}\n"
                for tt in range(1, timelen + 1)
            )
            fo.write("\tEnd\nEnd\n")

            fo.write(
                "Body Force 3\n"
                '\tName = "J_A_MINUS"\n'
                "\tCurrent Density = Variable time\n"
                "\t\tReal\n"
                "\t\t0.0\t\t0.0\n"
            )
            fo.writelines(
                f"\t\t{time[tt]:.2e}\t\t{-Ncond_Aminus * Is[0, tt - 1] / surf_wind:.3f}\n"
                for tt in range(1, timelen + 1)
            )
            fo.write("\tEnd\nEnd\n")

            fo.write(
                "Body Force 4\n"
                '\tName = "J_B_PLUS"\n'
                "\tCurrent Density = Variable time\n"
                "\t\tReal\n"
                "\t\t0.0\t\t0.0\n"
            )
            fo.writelines(
                f"\t\t{time[tt]:.2e}\t\t{Ncond_Bplus * Is[1, tt - 1] / surf_wind:.3f}\n"
                for tt in range(1, timelen + 1)
            )
            fo.write("\tEnd\nEnd\n")

            fo.write(
                "Body Force 5\n"
                '\tName = "J_B_MINUS"\n'
                "\tCurrent Density = Variable time\n"
                "\t\tReal\n"
                "\t\t0.0\t\t0.0\n"
            )
            fo.writelines(
                f"\t\t{time[tt]:.2e}\t\t{-Ncond_Bminus * Is[1, tt - 1] / surf_wind:.3f}\n"
                for tt in range(1, timelen + 1)
            )
            fo.write("\tEnd\nEnd\n")

            fo.write(
                "Body Force 6\n"
                '\tName = "J_C_PLUS"\n'
                "\tCurrent Density = Variable time\n"
                "\t\tReal\n"
                "\t\t0.0\t\t0.0\n"
            )
            fo.writelines(
                f"\t\t{time[tt]:.2e}\t\t{Ncond_Cplus * Is[2, tt - 1] / surf_wind:.3f}\n"
                for tt in range(1, timelen + 1)
            )
            fo.write("\tEnd\nEnd\n")

            fo.write(
                "Body Force 7\n"
                '\tName = "J_C_MINUS"\n'
                "\tCurrent Density = Variable time\n"
                "\t\tReal\n"
                "\t\t0.0\t\t0.0\n"
            )
            fo.writelines(
                f"\t\t{time[tt]:.2e}\t\t{-Ncond_Cminus * Is[2, tt - 1] / surf_wind:.3f}\n"
                for tt in range(1, timelen + 1)
            )
            fo.write("\tEnd\nEnd\n")

            fo.write("\n!--- BODIES ---\n")
            for k, v in bodies.items():
                bid = v["id"]
                beq = v["eq"]
                bmat = v["mat"]
                bf = v["bf"]
                btg = v["tg"]
                fo.write(
                    f"Body {bid}\n\tName = {k}\n\tEquation = {beq}\n\tMaterial = {bmat}\n"
                )
                if bf is not None:
                    fo.write(f"\tBody Force = {bf}\n")
                if btg is not None:
                    fo.write(f"\tTorque Groups = Integer {btg}\n")
                if k == "SB_INT":
                    fo.write(f"\tR Inner = Real {ror}\n\tR Outer = Real {sir}\n")
                fo.write("End\n\n")

            fo.write(
                "Equation 1\n"
                '\tName = "Model_Domain"\n'
                "\tActive Solvers(6) = 1 2 3 4 5 6\n"
                "End\n"
            )

            fo.write("\n!--- SOLVERS ---\n")
            fo.write(
                "Solver 1\n"
                "\tExec Solver = Before Timestep\n"
                "\tEquation = MeshDeform\n"
                '\tProcedure = "RigidMeshMapper" "RigidMeshMapper"\n'
                "End\n"
            )

            fo.write(
                "\nSolver 2\n"
                "\tEquation = MgDyn2D\n"
                '\tProcedure = "MagnetoDynamics2D" "MagnetoDynamics2D"\n'
                "\tExec Solver = Always\n"
                "\tVariable = A\n"
            )
            fo.write(f"\tNonlinear System Convergence Tolerance = {1e-6}\n")
            fo.write(f"\tNonlinear System Max Iterations = {100}\n")
            fo.write(f"\tNonlinear System Min Iterations = {1}\n")
            fo.write(f"\tNonlinear System Newton After Iterations = {5}\n")
            fo.write(f"\tNonlinear System Relaxation Factor = {0.9}\n")
            fo.write(
                "\tNonlinear System Convergence Without Constraints = {0}\n".format(
                    "Logical True"
                )
            )
            fo.write("\tExport Lagrange Multiplier = {0}\n".format("Logical True"))
            fo.write(
                "\tLinear System Abort Not Converged = {0}\n".format("Logical False")
            )
            fo.write("\tLinear System Solver = {0}\n".format("Direct"))
            fo.write("\tLinear System Direct Method = {0}\n".format("umfpack"))
            fo.write("\tOptimize Bandwidth = {0}\n".format("Logical True"))
            fo.write("\tLinear System Preconditioning =  {0}\n".format("ILU2"))
            fo.write(f"\tLinear System Max Iterations =  {5000}\n")
            fo.write(f"\tLinear System Residual Output =  {20}\n")
            fo.write(f"\tLinear System Convergence Tolerance =  {1e-7}\n")
            fo.write("\tMortar BCs Additive =  {0}\n".format("Logical True"))
            fo.write("End\n")

            fo.write(
                "\nSolver 3\n"
                "\tExec Solver = Always\n"
                "\tEquation = CalcFields\n"
                '\tPotential Variable = "A"\n'
                '\tProcedure = "MagnetoDynamics" "MagnetoDynamicsCalcFields"\n'
                "\tCalculate Nodal Forces = Logical True\n"
                "\tCalculate Magnetic Vector Potential = Logical True\n"
                "\tCalculate Winding Voltage = Logical True\n"
                "\tCalculate Current Density = Logical True\n"
                "\tCalculate Maxwell Stress = Logical True\n"
                "\tCalculate JxB = Logical True\n"
                "\tCalculate Magnetic Field Strength = Logical True\n"
                "End\n"
            )

            fo.write(
                "\nSolver 4\n"
                "\tExec Solver = After Timestep\n"
                '\tProcedure = "ResultOutputSolve" "ResultOutputSolver"\n'
                '\tOutput File Name = "{0}"\n'
                "\tVtu Format = True\n"
                "\tBinary Output = True\n"
                "\tSingle Precision = True\n"
                "\tSave Geometry Ids = True\n"
                "\tShow Variables = True\n"
                "End\n".format("step")
            )

            fo.write(
                "\nSolver 5\n"
                "\tExec Solver = After Timestep\n"
                "\tEquation = SaveLine\n"
                '\tFilename = "{0}"\n'
                '\tProcedure = "SaveData" "SaveLine"\n'
                "\tVariable 1 = Magnetic Flux Density 1\n"
                "\tVariable 2 = Magnetic Flux Density 2\n"
                "\tVariable 3 = Magnetic Flux Density 3\n"
                "\tVariable 4 = Magnetic Flux Density e 1\n"
                "\tVariable 5 = Magnetic Flux Density e 2\n"
                "\tVariable 6 = Magnetic Flux Density e 3\n"
                "End\n".format("lines.dat")
            )

            fo.write(
                "\nSolver 6\n"
                "\tExec Solver = After Timestep\n"
                '\tFilename = "{0}"\n'
                '\tProcedure = "SaveData" "SaveScalars"\n'
                "\tShow Norm Index = 1\n"
                "End\n".format("scalars.dat")
            )

            fo.write("\n!--- BOUNDARIES ---\n")
            for k, v in boundaries.items():
                if k == "VP0_BOUNDARY":
                    fo.write(
                        f"Boundary Condition {v}\n\tName = {k}\n\tA = Real 0\nEnd\n\n"
                    )
                elif k == "MASTER_STATOR_BOUNDARY":
                    for k1, v1 in boundaries.items():
                        if k1 == "SLAVE_STATOR_BOUNDARY":
                            slave = v1
                            break
                    if not self.is_periodicity_a:
                        fo.write(
                            f"Boundary Condition {v}\n"
                            f"\tName = {k}\n"
                            f"\tMortar BC = Integer {slave}\n"
                            "\tMortar BC Static = Logical True\n"
                            "\tRadial Projector = Logical True\n"
                            "\tGalerkin Projector = Logical True\n"
                            "End\n\n"
                        )
                    else:
                        fo.write(
                            f"Boundary Condition {v}\n"
                            f"\tName = {k}\n"
                            f"\tMortar BC = Integer {slave}\n"
                            "\tMortar BC Static = Logical True\n"
                            "\tAnti Radial Projector = Logical True\n"
                            "\tGalerkin Projector = Logical True\n"
                            "End\n\n"
                        )
                elif k == "MASTER_ROTOR_BOUNDARY":
                    for k1, v1 in boundaries.items():
                        if k1 == "SLAVE_ROTOR_BOUNDARY":
                            slave = v1
                            break
                    if not self.is_periodicity_a:
                        fo.write(
                            f"Boundary Condition {v}\n"
                            f"\tName = {k}\n"
                            f"\tMortar BC = Integer {slave}\n"
                            "\tMortar BC Static = Logical True\n"
                            "\tRadial Projector = Logical True\n"
                            "\tGalerkin Projector = Logical True\n"
                            "End\n\n"
                        )
                    else:
                        fo.write(
                            f"Boundary Condition {v}\n"
                            f"\tName = {k}\n"
                            f"\tMortar BC = Integer {slave}\n"
                            "\tMortar BC Static = Logical True\n"
                            "\tAnti Radial Projector = Logical True\n"
                            "\tGalerkin Projector = Logical True\n"
                            "End\n\n"
                        )
                elif k == "SB_STATOR_BOUNDARY":
                    for k1, v1 in boundaries.items():
                        if k1 == "SB_ROTOR_BOUNDARY":
                            slave = v1
                            break
                    if not self.is_periodicity_a:
                        fo.write(
                            f"Boundary Condition {v}\n"
                            f"\tName = {k}\n"
                            f"\tMortar BC = Integer {slave}\n"
                            "\tRotational Projector = Logical True\n"
                            "\tGalerkin Projector = Logical True\n"
                            "End\n\n"
                        )
                    else:
                        fo.write(
                            f"Boundary Condition {v}\n"
                            f"\tName = {k}\n"
                            f"\tMortar BC = Integer {slave}\n"
                            "\tAnti Rotational Projector = Logical True\n"
                            "\tGalerkin Projector = Logical True\n"
                            "End\n\n"
                        )
                elif k == "AIRGAP_ARC_BOUNDARY":
                    fo.write(
                        f"Boundary Condition {v}\n\tName = {k}\n\tSave Line = True\nEnd\n\n"
                    )
                else:
                    fo.write(f"Boundary Condition {v}\n\tName = {k}\nEnd\n\n")

        # setup Elmer solver
        # ElmerSolver v8.4 must be installed and in the PATH

        elmer_settings = os.path.join(project_name, "pyleecan_elmer.sif")
        ElmerSolver_binary = get_path_binary("ElmerSolver")
        cmd_elmersolver = [
            ElmerSolver_binary,
            elmer_settings,
        ]
        self.get_logger().info(
            "Calling ElmerSolver: " + " ".join(map(str, cmd_elmersolver))
        )
        elmersolver = subprocess.Popen(
            cmd_elmersolver, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        (stdout, stderr) = elmersolver.communicate()
        elmersolver.wait()
        self.get_logger().info(stdout.decode("UTF-8"))
        if elmersolver.returncode != 0:
            self.get_logger().info("ElmerSolver [Error]: " + stderr.decode("UTF-8"))
            return False
        elmersolver.terminate()
        self.get_logger().info("ElmerSolver call complete!")

        self.get_meshsolution(output)

        Na = angle.size
        Nt = time.size - 1

        # Loading parameters for readibility
        L1 = output.simu.machine.stator.comp_length()
        save_path = self.get_path_save(output)

        scalars_file = os.path.join(elmermesh_folder, "scalars.dat")
        ecp, mfe, agt, iv, im, tq = np.loadtxt(
            scalars_file, unpack=True, usecols=(0, 1, 2, 3, 4, 5)
        )
        # ecp: eddy current power
        # mfe: magnetic field energy
        # agt: air gap torque
        # iv: inertial volume
        # im: inertial moment
        # tq: group 1 torque

        # TODO Load Air gap flux density

        # FEM_dict = output.mag.FEM_dict
        #
        if (
            hasattr(output.simu.machine.stator, "winding")
            and output.simu.machine.stator.winding is not None
        ):
            qs = output.simu.machine.stator.winding.qs  # Winding phase number
            Phi_wind_stator = np.zeros((Nt, qs))
        else:
            Phi_wind_stator = None

        # Initialize results matrix
        Br = np.zeros((Nt, Na))
        Bt = np.zeros((Nt, Na))
        Bz = np.zeros((Nt, Na))
        Tem = tq * sym * L1

        # Phi_wind_stator = zeros((Nt, qs))

        # compute the data for each time step
        # TODO Other than FEMM, in Elmer I think it's possible to compute
        #      all time steps at once
        self.get_logger().debug("Solving Simulation")

        # run the computation
        if self.nb_worker > 1:
            # TODO run solver in parallel
            pass
        else:
            # TODO run solver 'normal'
            pass

        # get the air gap flux result
        # TODO add function (or method)
        # ii -> Time, jj -> Angle
        # Br[ii, jj], Bt[ii, jj] = get_airgap_flux()

        # get the torque
        # TODO add function (or method)
        # Tem[ii] = comp_Elmer_torque(FEM_dict, sym=sym)

        # flux linkage computation
        # if Phi_wind_stator is not None:
        #     # TODO
        #     # Phi_wind[ii, :] = comp_Elmer_Phi_wind()
        #     pass

        return Br, Bt, Bz, Tem, Phi_wind_stator
