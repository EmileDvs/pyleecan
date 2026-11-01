# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/MagElmer.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/MagElmer
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
from .Magnetics import Magnetics

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Functions.GMSH.draw_GMSH import draw_GMSH
from .OutMagElmer import OutMagElmer
from ..Methods.Simulation.MagElmer import MagElmer_BP_dict
import subprocess, os, numpy as np
from ..Functions.get_path_binary import get_path_binary
from os.path import join
from meshio import read
from numpy import (
    append as np_append,
    arange,
    angle as np_angle,
    floor_divide,
    loadtxt,
    pi,
    sign,
    zeros,
)
from .Data1D import Data1D
from .DataTime import DataTime
from .MeshSolution import MeshSolution
from .MeshVTK import MeshVTK
from .Norm_ref import Norm_ref
from .SolutionData import SolutionData
from .SolutionVector import SolutionVector
from .VectorField import VectorField
from .. import __version__
from .MachineIPMSM import MachineIPMSM
from .MachineSIPMSM import MachineSIPMSM
from ..Functions.labels import (
    AIRGAP_LAB,
    BOT_LAB,
    HOLEM_LAB_S,
    HOLEV_LAB_S,
    LAM_LAB_S,
    MAG_LAB,
    NO_LAM_LAB,
    ROTOR_LAB,
    ROTOR_LAB_S,
    SHAFT_LAB,
    SLID_LAB,
    STATOR_LAB_S,
    WIND_LAB_S,
    decode_label,
    get_obj_from_label,
    short_label,
)
from ..Functions.Winding.find_wind_phase_color import get_phase_id
from ..Methods import NotImplementedYetError

from numpy import isnan
from ._check import InitUnKnowClassError


class MagElmer(Magnetics):
    """Magnetic module: Finite Element model with Elmer"""

    VERSION = 1

    # cf Methods.Simulation.MagElmer.comp_flux_airgap
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
        out_dict = dict()
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
                boundary_prop=MagElmer_BP_dict,
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

    # cf Methods.Simulation.MagElmer.gen_elmer_mesh
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

    # cf Methods.Simulation.MagElmer.get_meshsolution
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

        result_filename = join(elmermesh_folder, "step_t0002.vtu")
        meshsolvtu = read(result_filename)
        # pt_data = meshsolvtu.point_data
        cell_data = meshsolvtu.cell_data

        # indices = arange(meshsolvtu.points.shape[0])
        indices = arange(
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
        sol_dict = dict()
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
                values = np_append(value[0], value[1], axis=0)
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
                        normalizations={"ref": Norm_ref(ref=store_dict[key]["norm"])},
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

    # cf Methods.Simulation.MagElmer.get_path_save
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

        save_dir = join(path_res, "Elmer")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        return save_dir

    # cf Methods.Simulation.MagElmer.get_path_save_fea
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

        return join(save_dir, file_name)

    # cf Methods.Simulation.MagElmer.solve_FEA
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
        mesh_names_file = join(project_name, "mesh.names")
        boundaries = {}
        bodies = {}
        machine = output.simu.machine
        BHs = output.geo.stator.BH_curve  # Stator B(H) curve
        BHr = output.geo.rotor.BH_curve  # Rotor B(H) curve
        # Is = output.elec.Is  # Stator currents waveforms
        # Ir = output.elec.Ir  # Rotor currents waveforms
        Speed = output.elec.OP.get_N0()
        rotor_mat_file = join(project_name, "rotor_material.pmf")
        stator_mat_file = join(project_name, "stator_material.pmf")

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

        elmer_sim_file = join(project_name, "pyleecan_elmer.sif")
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
            Mangle = list()
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
                            floor_divide(np_angle(point_ref, deg=True), alpha_p) + 0.5
                        ) * alpha_p

                        mag_dict = hole.comp_magnetization_dict()
                        mag = mag_0 + mag_dict["magnet_" + str(T_id)] * 180 / pi
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
                        mag = np_angle(point_ref) * 180 / pi  # North pole magnet
                        magnetization_type = "parallel"
                    elif mag_obj.type_magnetization == 1:
                        mag = np_angle(point_ref) * 180 / pi + 180  # South pole magnet
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
                    s = sign(Ncond)
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
            bodies[NO_LAM_LAB + "_" + SLID_LAB + BOT_LAB][
                "bf"
            ] = 1  # Sliding band bottom

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
            rotor_d_axis = machine.rotor.comp_angle_d_axis() * 180.0 / pi
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
            fo.write(f"$ RotorInitPos = {round(rotor_init_pos * 180.0 / pi, 2)}!\n")

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
                f"\t\t{time[tt]:.2e}\t\t{angle_rotor[tt - 1] * 180.0 / pi:.3f}\n"
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

        elmer_settings = join(project_name, "pyleecan_elmer.sif")
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

        scalars_file = join(elmermesh_folder, "scalars.dat")
        ecp, mfe, agt, iv, im, tq = loadtxt(
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
            Phi_wind_stator = zeros((Nt, qs))
        else:
            Phi_wind_stator = None

        # Initialize results matrix
        Br = zeros((Nt, Na))
        Bt = zeros((Nt, Na))
        Bz = zeros((Nt, Na))
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Kmesh_fineness=1,
        Kgeo_fineness=1,
        file_name="",
        FEA_dict=-1,
        is_get_mesh=False,
        is_save_FEA=False,
        transform_list=-1,
        rotor_dxf=None,
        stator_dxf=None,
        import_file="",
        nb_worker=1,
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
            if "file_name" in list(init_dict.keys()):
                file_name = init_dict["file_name"]
            if "FEA_dict" in list(init_dict.keys()):
                FEA_dict = init_dict["FEA_dict"]
            if "is_get_mesh" in list(init_dict.keys()):
                is_get_mesh = init_dict["is_get_mesh"]
            if "is_save_FEA" in list(init_dict.keys()):
                is_save_FEA = init_dict["is_save_FEA"]
            if "transform_list" in list(init_dict.keys()):
                transform_list = init_dict["transform_list"]
            if "rotor_dxf" in list(init_dict.keys()):
                rotor_dxf = init_dict["rotor_dxf"]
            if "stator_dxf" in list(init_dict.keys()):
                stator_dxf = init_dict["stator_dxf"]
            if "import_file" in list(init_dict.keys()):
                import_file = init_dict["import_file"]
            if "nb_worker" in list(init_dict.keys()):
                nb_worker = init_dict["nb_worker"]
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
        self.file_name = file_name
        self.FEA_dict = FEA_dict
        self.is_get_mesh = is_get_mesh
        self.is_save_FEA = is_save_FEA
        self.transform_list = transform_list
        self.rotor_dxf = rotor_dxf
        self.stator_dxf = stator_dxf
        self.import_file = import_file
        self.nb_worker = nb_worker
        # Call Magnetics init
        super(MagElmer, self).__init__(
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

        MagElmer_str = ""
        # Get the properties inherited from Magnetics
        MagElmer_str += super(MagElmer, self).__str__()
        MagElmer_str += "Kmesh_fineness = " + str(self.Kmesh_fineness) + linesep
        MagElmer_str += "Kgeo_fineness = " + str(self.Kgeo_fineness) + linesep
        MagElmer_str += 'file_name = "' + str(self.file_name) + '"' + linesep
        MagElmer_str += "FEA_dict = " + str(self.FEA_dict) + linesep
        MagElmer_str += "is_get_mesh = " + str(self.is_get_mesh) + linesep
        MagElmer_str += "is_save_FEA = " + str(self.is_save_FEA) + linesep
        MagElmer_str += (
            "transform_list = "
            + linesep
            + str(self.transform_list).replace(linesep, linesep + "\t")
            + linesep
        )
        if self.rotor_dxf is not None:
            tmp = self.rotor_dxf.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            MagElmer_str += "rotor_dxf = " + tmp
        else:
            MagElmer_str += "rotor_dxf = None" + linesep + linesep
        if self.stator_dxf is not None:
            tmp = (
                self.stator_dxf.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            )
            MagElmer_str += "stator_dxf = " + tmp
        else:
            MagElmer_str += "stator_dxf = None" + linesep + linesep
        MagElmer_str += 'import_file = "' + str(self.import_file) + '"' + linesep
        MagElmer_str += "nb_worker = " + str(self.nb_worker) + linesep
        return MagElmer_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Magnetics
        if not super(MagElmer, self).__eq__(other):
            return False
        if other.Kmesh_fineness != self.Kmesh_fineness:
            return False
        if other.Kgeo_fineness != self.Kgeo_fineness:
            return False
        if other.file_name != self.file_name:
            return False
        if other.FEA_dict != self.FEA_dict:
            return False
        if other.is_get_mesh != self.is_get_mesh:
            return False
        if other.is_save_FEA != self.is_save_FEA:
            return False
        if other.transform_list != self.transform_list:
            return False
        if other.rotor_dxf != self.rotor_dxf:
            return False
        if other.stator_dxf != self.stator_dxf:
            return False
        if other.import_file != self.import_file:
            return False
        if other.nb_worker != self.nb_worker:
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
            super(MagElmer, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Kmesh_fineness is not None
            and self._Kmesh_fineness is not None
            and isnan(other._Kmesh_fineness)
            and isnan(self._Kmesh_fineness)
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
            and isnan(other._Kgeo_fineness)
            and isnan(self._Kgeo_fineness)
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
        if other._FEA_dict != self._FEA_dict:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._FEA_dict)
                    + ", other="
                    + str(other._FEA_dict)
                    + ")"
                )
                diff_list.append(name + ".FEA_dict" + val_str)
            else:
                diff_list.append(name + ".FEA_dict")
        if other._is_get_mesh != self._is_get_mesh:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_get_mesh)
                    + ", other="
                    + str(other._is_get_mesh)
                    + ")"
                )
                diff_list.append(name + ".is_get_mesh" + val_str)
            else:
                diff_list.append(name + ".is_get_mesh")
        if other._is_save_FEA != self._is_save_FEA:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_save_FEA)
                    + ", other="
                    + str(other._is_save_FEA)
                    + ")"
                )
                diff_list.append(name + ".is_save_FEA" + val_str)
            else:
                diff_list.append(name + ".is_save_FEA")
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Magnetics
        S += super(MagElmer, self).__sizeof__()
        S += getsizeof(self.Kmesh_fineness)
        S += getsizeof(self.Kgeo_fineness)
        S += getsizeof(self.file_name)
        if self.FEA_dict is not None:
            for key, value in self.FEA_dict.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.is_get_mesh)
        S += getsizeof(self.is_save_FEA)
        if self.transform_list is not None:
            for value in self.transform_list:
                S += getsizeof(value)
        S += getsizeof(self.rotor_dxf)
        S += getsizeof(self.stator_dxf)
        S += getsizeof(self.import_file)
        S += getsizeof(self.nb_worker)
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
        MagElmer_dict = super(MagElmer, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        MagElmer_dict["Kmesh_fineness"] = self.Kmesh_fineness
        MagElmer_dict["Kgeo_fineness"] = self.Kgeo_fineness
        MagElmer_dict["file_name"] = self.file_name
        MagElmer_dict["FEA_dict"] = (
            self.FEA_dict.copy() if self.FEA_dict is not None else None
        )
        MagElmer_dict["is_get_mesh"] = self.is_get_mesh
        MagElmer_dict["is_save_FEA"] = self.is_save_FEA
        MagElmer_dict["transform_list"] = (
            self.transform_list.copy() if self.transform_list is not None else None
        )
        if self.rotor_dxf is None:
            MagElmer_dict["rotor_dxf"] = None
        else:
            MagElmer_dict["rotor_dxf"] = self.rotor_dxf.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        if self.stator_dxf is None:
            MagElmer_dict["stator_dxf"] = None
        else:
            MagElmer_dict["stator_dxf"] = self.stator_dxf.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        MagElmer_dict["import_file"] = self.import_file
        MagElmer_dict["nb_worker"] = self.nb_worker
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        MagElmer_dict["__class__"] = "MagElmer"
        return MagElmer_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Kmesh_fineness_val = self.Kmesh_fineness
        Kgeo_fineness_val = self.Kgeo_fineness
        file_name_val = self.file_name
        if self.FEA_dict is None:
            FEA_dict_val = None
        else:
            FEA_dict_val = self.FEA_dict.copy()
        is_get_mesh_val = self.is_get_mesh
        is_save_FEA_val = self.is_save_FEA
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
        nb_worker_val = self.nb_worker
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
            file_name=file_name_val,
            FEA_dict=FEA_dict_val,
            is_get_mesh=is_get_mesh_val,
            is_save_FEA=is_save_FEA_val,
            transform_list=transform_list_val,
            rotor_dxf=rotor_dxf_val,
            stator_dxf=stator_dxf_val,
            import_file=import_file_val,
            nb_worker=nb_worker_val,
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
        self.file_name = None
        self.FEA_dict = None
        self.is_get_mesh = None
        self.is_save_FEA = None
        self.transform_list = None
        if self.rotor_dxf is not None:
            self.rotor_dxf._set_None()
        if self.stator_dxf is not None:
            self.stator_dxf._set_None()
        self.import_file = None
        self.nb_worker = None
        # Set to None the properties inherited from Magnetics
        super(MagElmer, self)._set_None()

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
        doc="""global coefficient to adjust mesh fineness (1 : default , > 1 : finner , < 1 : less fine)

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
        doc="""global coefficient to adjust geometry fineness (1 : default , > 1 : finner , < 1 : less fine)

        :Type: float
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
        doc="""Name of the file to save the Elmer model

        :Type: str
        """,
    )

    def _get_FEA_dict(self):
        """getter of FEA_dict"""
        return self._FEA_dict

    def _set_FEA_dict(self, value):
        """setter of FEA_dict"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("FEA_dict", value, "dict")
        self._FEA_dict = value

    FEA_dict = property(
        fget=_get_FEA_dict,
        fset=_set_FEA_dict,
        doc="""To enforce user-defined values for Elmer main parameters 

        :Type: dict
        """,
    )

    def _get_is_get_mesh(self):
        """getter of is_get_mesh"""
        return self._is_get_mesh

    def _set_is_get_mesh(self, value):
        """setter of is_get_mesh"""
        check_var("is_get_mesh", value, "bool")
        self._is_get_mesh = value

    is_get_mesh = property(
        fget=_get_is_get_mesh,
        fset=_set_is_get_mesh,
        doc="""To save FEA mesh for latter post-procesing 

        :Type: bool
        """,
    )

    def _get_is_save_FEA(self):
        """getter of is_save_FEA"""
        return self._is_save_FEA

    def _set_is_save_FEA(self, value):
        """setter of is_save_FEA"""
        check_var("is_save_FEA", value, "bool")
        self._is_save_FEA = value

    is_save_FEA = property(
        fget=_get_is_save_FEA,
        fset=_set_is_save_FEA,
        doc="""To save FEA mesh and solution in a file

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
        doc="""To import an existing simulation file

        :Type: str
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
        doc="""To run Elmer in parallel (the parallelization is on the time loop)

        :Type: int
        """,
    )
