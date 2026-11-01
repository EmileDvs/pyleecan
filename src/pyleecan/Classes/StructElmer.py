# File generated according to Generator/ClassesRef/Simulation/StructElmer.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/StructElmer"""

import subprocess
from os import linesep, makedirs, replace
from os.path import exists, join, split, splitext
from sys import getsizeof

import gmsh
import numpy as np
from pyleecan.Classes.ElmerResultsVTU import ElmerResultsVTU
from pyleecan.Classes.Section import File, MATC, Section, Variable
from pyleecan.Classes.SolverInputFile import SolverInputFile
from pyleecan.Classes.Structural import Structural
from pyleecan.Classes._check import check_var

from pyleecan.Functions.GMSH.draw_GMSH import draw_GMSH
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.get_path_binary import get_path_binary
from pyleecan.Functions.labels import (
    AIRBOX_R_LAB,
    AIRBOX_SL_LAB,
    AIRBOX_SR_LAB,
    AR_T_LAB,
    AS_BL_LAB,
    AS_BR_LAB,
    AS_TL_LAB,
    AS_TR_LAB,
    BORE_LAB,
    HOLEM_LAB_S,
    HOLEV_LAB_S,
    LAM_LAB,
    LAM_LAB_S,
    ROTOR_LAB,
    ROTOR_LAB_S,
    SBR_B_LAB,
    SBR_T_LAB,
    SBS_BL_LAB,
    SBS_BR_LAB,
    SBS_TL_LAB,
    SBS_TR_LAB,
    SHAFTSL_LAB,
    SHAFTSR_LAB,
    SHAFT_LAB,
    STATOR_LAB,
    STATOR_LAB_S,
    WIND_LAB_S,
    YSL_LAB,
    YSR_LAB,
    decode_label,
)
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class StructElmer(Structural):
    """Structural module: FEA model with Elmer"""

    VERSION = 1

    # cf Methods.Simulation.StructElmer.gen_case
    def gen_case(self, output, mesh_names, *, ID_LAM=1, ID_MAG=2):
        """Setup the Elmer Case file (.sif file)"""

        # get the save path
        save_dir = self.get_path_save_fea(output)

        sif_file = join(save_dir, "case.sif")

        # save solver start info
        start_file = join(save_dir, "ELMERSOLVER_STARTINFO")

        with open(start_file, "wt") as fout:
            fout.write(split(sif_file)[1])

        # generate list of mesh names
        names = []
        for value in mesh_names.values():
            names.extend(value)

        # --- prepare sections ----------------------------------------------------------- #
        # --- bodies --------------------------------------------------------------------- #
        bodies = []
        for name in names:
            if "Body" in name:
                body = Section(section="Body", id=len(bodies) + 1)
                body["name"] = name
                body["Equation"] = 1
                if "Magnet" in name:
                    body["Material"] = ID_MAG
                elif "Lamination" in name:
                    body["Material"] = ID_LAM
                body["Body Force"] = 1

                bodies.append(body)

        # --- simulation ----------------------------------------------------------------- #
        sim = Section(section="Simulation")
        sim["Max Output Level"] = 5
        sim["Coordinate System"] = "Cartesian 2D"
        sim["Coordinate Mapping"] = [1, 2, 3]
        sim["Simulation Type"] = "Steady State"
        sim["Steady State Max Iterations"] = 1
        sim["Initialize Dirichlet Conditions"] = False
        # sim["Output File"] = File("simulation.result")
        sim["Use Mesh Names"] = True

        # --- constants ------------------------------------------------------------------ #
        const = Section(section="Constants")
        const["Gravity"] = [0.0, -1.0, 0.0, 9.82]

        # --- solvers -------------------------------------------------------------------- #
        solver_list = []

        # solver - move mesh before simulation
        i = 1
        solver = Section(section="Solver", id=i)
        solver.comment = "Moves the magnets as defined in the body force section"
        solver["Exec Solver"] = "Before all"
        solver["Equation"] = "MeshDeform"
        solver["Procedure"] = [File("RigidMeshMapper"), File("RigidMeshMapper")]
        solver_list.append(solver)

        # solver - elasticity simulation
        i += 1
        solver = Section(section="Solver", id=i)
        solver["Equation"] = "Linear Elasticity"
        solver["Procedure"] = [File("ElasticSolve"), File("ElasticSolver")]
        solver["Variable"] = "-dofs 2 Displacement"
        solver["Linear System Solver"] = "Iterative"
        solver["Linear System Preconditioning"] = "ILU3"
        solver["Linear System Residual Output"] = 10
        solver["Linear System Max Iterations"] = 400
        solver["Linear System Iterative Method"] = "GCR"
        solver["Linear System Convergence Tolerance"] = 1.0e-9
        solver["Linear System Abort Not Converged"] = False
        solver["Linear System Residual Mode"] = True
        solver["Nonlinear System Convergence Tolerance"] = 1.0e-7
        solver["Nonlinear System Max Iterations"] = 20
        solver["Nonlinear System Relaxation Factor"] = 1.0
        # solver['Displace Mesh'] = True
        solver["Calculate Principal"] = True
        solver["Calculate Loads"] = True
        solver["Calculate Stresses"] = True
        solver["Calculate Strains"] = True
        solver["Apply Contact BCs"] = True
        solver["Stabilize"] = True
        solver["Elasticity Solver Linear"] = True
        solver["Optimize Bandwidth"] = True
        solver_list.append(solver)

        # solver - save results as vtu if requested
        i += 1
        solver = Section(section="Solver", id=i)
        solver["Exec Solver"] = "After Simulation" if self.is_save_FEA else "Never"
        solver["Equation"] = "result output"
        solver["Procedure"] = [File("ResultOutputSolve"), File("ResultOutputSolver")]
        solver["Output Directory"] = File("Results")
        solver["Output File Name"] = File("case")
        solver["Vtu Format"] = True
        # solver["Ascii Output"] = True  # to save vtu as ascii
        solver["Save Geometry Ids"] = True
        solver["Displace Mesh"] = True
        solver["Single Precision"] = (
            True  # default: False, False == 32 bit, True == 64 bit
        )
        solver_list.append(solver)

        # solver - save statistical, integral, min, max, mean, ... values
        i += 1
        solver = Section(section="Solver", id=i)
        solver["Exec Solver"] = "After Simulation"
        solver["Equation"] = "SaveScalars"
        solver["Procedure"] = [File("SaveData"), File("SaveScalars")]
        solver["Output Directory"] = File("Results")
        solver["Filename"] = File("Scalars.dat")
        solver["Operator 1"] = "boundary int"
        solver["Variable 1"] = "Principal Stress 1"
        solver["Mask Name 1"] = "MASTER_ROTOR_BOUNDARY"
        solver["Operator 2"] = "boundary int"
        solver["Variable 2"] = "Principal Stress 2"
        solver["Mask Name 2"] = "MASTER_ROTOR_BOUNDARY"
        solver["Operator 3"] = "boundary int"
        solver["Variable 3"] = "Principal Stress 1"
        solver["Mask Name 3"] = "SLAVE_ROTOR_BOUNDARY"
        solver["Operator 4"] = "boundary int"
        solver["Variable 4"] = "Principal Stress 2"
        solver["Mask Name 4"] = "SLAVE_ROTOR_BOUNDARY"
        solver_list.append(solver)

        # solver - save line values
        # if no variable given, all variables are saved
        i += 1
        solver = Section(section="Solver", id=i)
        solver["Exec Solver"] = "After Simulation"
        solver["Equation"] = "SaveLineValues"
        solver["Procedure"] = [File("SaveData"), File("SaveLine")]
        solver["Output Directory"] = File("Results")
        solver["Filename"] = File("LineValues.dat")
        solver["Variable 1"] = "Displacement 1"
        solver["Variable 2"] = "Displacement 2"
        solver["Variable 3"] = "Principal Stress 1"
        solver["Variable 4"] = "Principal Stress 2"
        solver["Variable 5"] = "VonMises"
        # solver["Save Mask 1"] = "MASTER_ROTOR_BOUNDARY"
        # solver["Skip Boundary Info"] = Logical True
        solver_list.append(solver)

        # Variable 1 = Stress Bodyforce 1
        # Mask Name 1 = BodyForce
        # Operator 2 = boundary int
        # Variable 2 = Displacement Loads 1
        # Mask Name 2 = Top_0
        # Operator 3 = boundary int
        # Variable 3 = Displacement Loads 2
        # Mask Name 3 = Top_0
        # Operator 4 = boundary int
        # Variable 4 = Displacement Contact Load 1
        # Mask Name 4 = Top_0

        # Solver 5
        # Equation = "SaveMaterial"
        # Procedure = File "SaveData" "SaveMaterials"
        # !Parameter 1 = String "Stress Bodyforce 1"
        # !Parameter 2 = String "Stress Bodyforce 2"
        # !Body Force Parameters = 1

        # --- equations ------------------------------------------------------------------ #
        eqs = Section(section="Equation", id=1)
        eqs["Name"] = "Equation"
        eqs["Active Solvers"] = [i + 1 for i in range(len(solver_list))]

        # --- materials ------------------------------------------------------------------ #
        # TODO get magnets materials is inconvienent
        materials = [None, None, None]  # one extra element since ID_xx starts with 1

        mat_section = [Section(section="Material", id=ID_LAM)]
        materials[ID_LAM] = output.simu.machine.rotor.mat_type

        if self.include_magnets:
            mat_section.append(Section(section="Material", id=ID_MAG))
            materials[ID_MAG] = output.simu.machine.rotor.hole[0].magnet_0.mat_type

        # add materials to material sections
        for idx in range(len(mat_section)):
            ID = mat_section[idx].id
            mat_section[idx]["Name"] = materials[ID].name
            mat_section[idx]["Density"] = float(materials[ID].struct.rho)
            mat_section[idx]["Youngs modulus"] = float(materials[ID].struct.Ex)
            mat_section[idx]["Poisson ratio"] = float(materials[ID].struct.nu_xy)
            # TODO check anisotropy

        # --- boundary conditions -------------------------------------------------------- #

        boundaries = []
        i = 0

        # pair master and slave of Magnet_x_Top, Magnet_0_Right and Magnet_1_Left
        paired_bnds = [
            "Rotor_Magnet_0_Top",
            "Rotor_Magnet_1_Top",
            "Rotor_Magnet_0_Right",
            "Rotor_Magnet_1_Left",
        ]

        for name in paired_bnds:
            master = name + "_Master"
            slave = name + "_Slave"
            if master in names and slave in names:
                # "slave"
                i += 1
                bnd = Section(section="Boundary Condition", id=i)
                bnd["Name"] = slave
                bnd["Normal-Tangential Displacement"] = True
                bnd["Periodic BC"] = i + 1  # next bnd will be the corresponding master
                bnd["Periodic BC Displacement 1"] = (
                    True  # normal disp is fixed between M&S
                )
                bnd["Periodic BC Displacement 2"] = (
                    False  # tangential disp is independent
                )
                bnd["Periodic BC Pressure"] = False  # pressure can be independent
                bnd["Top_0"] = True  # for save values
                boundaries.append(bnd)

                # "master"
                i += 1
                bnd = Section(section="Boundary Condition", id=i)
                bnd["Name"] = master
                bnd["Normal-Tangential Displacement"] = True
                boundaries.append(bnd)

        # no normal displacement on lamination sides
        i += 1
        bnd = Section(section="Boundary Condition", id=i)
        bnd["Name"] = "MASTER_ROTOR_BOUNDARY"
        bnd["Displacement 1"] = 0.0
        bnd["Normal-Tangential Displacement"] = True
        bnd["Save Line"] = True
        bnd["Save Scalars"] = True
        bnd["MASTER_ROTOR_BOUNDARY"] = True  # mask name for SaveLine and SaveScalar
        boundaries.append(bnd)

        i += 1
        bnd = Section(section="Boundary Condition", id=i)
        bnd["Name"] = "SLAVE_ROTOR_BOUNDARY"
        bnd["Displacement 1"] = 0.0
        bnd["Normal-Tangential Displacement"] = True
        bnd["Save Line"] = True
        bnd["Save Scalars"] = True
        bnd["SLAVE_ROTOR_BOUNDARY"] = True  # mask name for SaveLine and SaveScalar
        boundaries.append(bnd)

        i += 1  # Boundary to save line values
        bnd = Section(section="Boundary Condition", id=i)
        bnd["Name"] = "ROTOR_BORE_CURVE"
        # bnd["Normal-Tangential Displacement"] = True
        bnd["Save Line"] = True
        bnd["Save Scalars"] = True
        boundaries.append(bnd)

        # --- body force ----------------------------------------------------------------- #
        omega = 2 * np.pi * self.parent.input.OP.N0 / 60
        bfs = []

        ID_list = [
            ID_LAM,
        ]
        if self.include_magnets:
            ID_list.append(ID_MAG)

        for ID in ID_list:
            matc = MATC(expr=f"{materials[ID].struct.rho}*{omega}^2*tx(0)")
            bf = Section(section="Body Force", id=ID)
            bf["Name"] = "Stress"
            bf["Mesh Rotate 3"] = 0.0
            bf["Stress Bodyforce 1"] = Variable(name="Coordinate 1", value=matc)
            bf["Stress Bodyforce 2"] = Variable(name="Coordinate 2", value=matc)
            bfs.append(bf)

        # -------------------------------------------------------------------------------- #
        # list of section - list need to be extended, single obj. can be appended
        sect_list = []
        sect_list.extend(bodies)
        sect_list.append(sim)
        sect_list.append(const)
        sect_list.extend(mat_section)
        sect_list.extend(solver_list)
        sect_list.append(eqs)
        sect_list.extend(boundaries)
        sect_list.extend(bfs)

        # create SolverInputFile obj.
        sif = SolverInputFile(sections=sect_list)

        # save the sif file
        with open(sif_file, "wt") as f:
            sif.write(f)

    @staticmethod
    def _execute(binary_name, cwd, logger, parameter=None):
        """Function to execute Elmer Binaries in the current working directory 'cwd'"""
        binary = get_path_binary(binary_name)
        cmd = ['"' + binary + '"']
        logger.info(f"Calling {binary_name}: " + " ".join(map(str, cmd)))
        if parameter:
            cmd.extend(parameter)
        popen = subprocess.Popen(
            " ".join(cmd),
            stdout=subprocess.PIPE,
            universal_newlines=True,
            shell=True,
            cwd=cwd,
        )
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise ElmerProcessError(
                f"Elmer Process Error while executing {' '.join(cmd)}: Return Code [{return_code}]"
            )

    @staticmethod
    def _get_BP_dict():
        """Build the mapping of Pyleecan labels to structural Elmer boundaries."""
        rotor_label = ROTOR_LAB + "-0_"
        stator_label = STATOR_LAB + "-0_"
        return {
            AS_BR_LAB: "MASTER_ROTOR_BOUNDARY",
            AS_BL_LAB: "SLAVE_ROTOR_BOUNDARY",
            SBS_BR_LAB: "MASTER_ROTOR_BOUNDARY",
            SBS_BL_LAB: "SLAVE_ROTOR_BOUNDARY",
            SBR_B_LAB: "SB_ROTOR_BOUNDARY",
            rotor_label + LAM_LAB + BORE_LAB: "ROTOR_BORE_CURVE",
            rotor_label + YSR_LAB: "MASTER_ROTOR_BOUNDARY",
            rotor_label + YSL_LAB: "SLAVE_ROTOR_BOUNDARY",
            stator_label + YSR_LAB: "MASTER_STATOR_BOUNDARY",
            stator_label + YSL_LAB: "SLAVE_STATOR_BOUNDARY",
            SHAFTSR_LAB: "MASTER_ROTOR_BOUNDARY",
            SHAFTSL_LAB: "SLAVE_ROTOR_BOUNDARY",
            AIRBOX_R_LAB: "VP0_BOUNDARY",
            AIRBOX_SR_LAB: "MASTER_STATOR_BOUNDARY",
            AIRBOX_SL_LAB: "SLAVE_STATOR_BOUNDARY",
            AS_TR_LAB: "MASTER_STATOR_BOUNDARY",
            AS_TL_LAB: "SLAVE_STATOR_BOUNDARY",
            AR_T_LAB: "AIRGAP_ARC_BOUNDARY",
            SBS_TR_LAB: "MASTER_STATOR_BOUNDARY",
            SBS_TL_LAB: "SLAVE_STATOR_BOUNDARY",
            SBR_T_LAB: "SB_STATOR_BOUNDARY",
        }

    # cf Methods.Simulation.StructElmer.gen_mesh
    def gen_mesh(self, output):
        """Initialize the FEA simulation model

        Parameters
        ----------
        self : StructElmer object

        output : Output
            Output object that contains the StructElmer simulation

        Return
        ------


        """
        # readability
        machine = output.simu.machine
        sym_r, is_antipert_r = machine.comp_periodicity_spatial()

        sym_r = sym_r * (1 + is_antipert_r)

        # get the save path and file names
        save_dir = self.get_path_save_fea(output)

        # draw initial gmsh model
        file_gmsh_geo = join(save_dir, "GMSH_Machine_Model.geo")

        draw_GMSH(
            output=output,
            sym=sym_r,  # TODO is it possible to have to use draw_GMSH with sym_r > sym ?
            boundary_prop=self._get_BP_dict(),
            is_lam_only_S=False,
            is_lam_only_R=False,
            is_sliding_band=False,
            user_mesh_dict=self.FEA_dict_enforced,
            path_save=file_gmsh_geo,
            is_set_labels=True,
        )

        # preprocess GMSH model to get rotor lamination and magnet and set boundary names
        lam_name = "lamination.msh"
        mag_name = "magnets.msh" if self.include_magnets else None

        names = {}
        _, _, names["Lamination"] = self.process_mesh(
            file_gmsh_geo,
            join(save_dir, lam_name),
            is_get_lam=True,
            is_get_magnet=False,
        )

        if self.include_magnets:
            _, _, names["Magnets"] = self.process_mesh(
                file_gmsh_geo,
                join(save_dir, mag_name),
                is_get_lam=False,
                is_get_magnet=True,
            )

        # convert to ElmerGrid mesh
        self._gen_mesh(save_dir, "Mesh", lam_name, mag_name, self.get_logger())

        return names

    @staticmethod
    def _gen_mesh(cwd, out_name, lam_name, mag_name=None, logger=None):
        """Convert the mesh from GMSH format to ElmerGrid format

        Parameters
        ----------

        Returns
        -------

        """
        # command line parameter to ElmerGrid
        parameter = []
        parameter.append("14 2")
        parameter.append(lam_name)
        if mag_name is not None:
            parameter.append("-in")
            parameter.append(mag_name)
            parameter.append("-unite")

        parameter.append("-out")
        parameter.append(out_name)
        parameter.append("-2d")
        parameter.append("-autoclean")
        parameter.append("-names")

        # execute ElmerGrid
        for info in self._execute("ElmerGrid", cwd, logger, parameter=parameter):
            print(info, end="")

        return True

    # cf Methods.Simulation.StructElmer.get_meshsolution
    def get_meshsolution(self, output):
        """Get and set the mesh data and solution data.

        Parameters
        ----------
        self : StructElmer
            a StructElmer object
        save_path: str
            Full path to folder in which the results are saved

        Returns
        -------
        success: bool
            Information if meshsolution could be created

        """
        # logger
        logger = self.get_logger()

        fea_path = self.get_path_save_fea(output)

        # if meshsoltion is not requested set meshsolution to None
        if not self.is_get_mesh or not self.is_save_FEA:
            logger.info("StructElmer: MeshSolution is not stored by request.")
            output.struct.meshsolution = None
            return False

        # setup Elmer result helper class
        ElmerVtu = ElmerResultsVTU()

        ElmerVtu.store_dict = {
            "displacement": {
                "name": "Displacement",
                "unit": "mm",
                "symbol": "disp",
                "norm": 1e-3,
            },
            "vonmises": {
                "name": "Von Mises Stress",
                "unit": "MPa",
                "symbol": "vonmises",
                "norm": 1e6,
            },
        }

        ElmerVtu.label = "Elmer Structural"
        ElmerVtu.file_path = join(fea_path, "Results", "case_t0001.vtu")

        output.struct.meshsolution = ElmerVtu.build_meshsolution()

        return True

    # cf Methods.Simulation.StructElmer.get_path_save_fea
    def get_path_save_fea(self, output):
        """Return the path to save the FEA simulation

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
        path_res = output.get_path_result()

        save_dir = join(path_res, "Elmer_Elasticity")
        if not exists(save_dir):
            makedirs(save_dir)

        return save_dir

    # cf Methods.Simulation.StructElmer.process_mesh
    def process_mesh(
        self, file_in, file_out, is_get_lam=True, is_get_magnet=False, is_hole_air=True
    ):
        """Preprocess the GMSH model, i.e. remove unused parts, rename boundaries, ..."""
        # TODO utilize 'translation' dict

        gmsh.initialize()
        gmsh.open(file_in)
        gmsh.model.geo.removeAllDuplicates()

        # remove unused model parts
        sta_lam = (STATOR_LAB_S + "-0_" + LAM_LAB_S).lower()  # Stator Lamination
        sta_wind = (STATOR_LAB_S + "-0_" + WIND_LAB_S).lower()  # Stator Winding
        self._remove_entities(gmsh, labels=[sta_lam, sta_wind])

        # get group names
        grps = gmsh.model.getPhysicalGroups(-1)
        grp_names = [gmsh.model.getPhysicalName(*grp) for grp in grps]

        # get lists of some surfaces by name
        magnet_list = []
        for grp, name in zip(grps, grp_names):
            label_dict = decode_label(name)
            if HOLEM_LAB_S in label_dict["surf_type"]:
                entities = gmsh.model.getEntitiesForPhysicalGroup(*grp)
                if grp[0] == 2:
                    magnet_list.extend(entities.tolist())

        if True:  # is_get_lam:
            lam_list = []
            for grp, name in zip(grps, grp_names):
                label_dict = decode_label(name)
                if (
                    ROTOR_LAB_S in label_dict["lam_type"]
                    and LAM_LAB_S in label_dict["surf_type"]
                ):
                    entities = gmsh.model.getEntitiesForPhysicalGroup(*grp)
                    if grp[0] == 2:
                        lam_list.extend(entities.tolist())

            lam_lines = []
            for lam in lam_list:
                lam_lines.extend(gmsh.model.getBoundary([(2, lam)], oriented=False))
            lam_lines = list(set([lam[1] for lam in lam_lines]))  # unique

            hole_lines = []
            for line in lam_lines:
                names = self._get_names_physical(
                    gmsh,
                    dimtag=[
                        1,
                        line,
                    ],
                )
                if any(
                    [HOLEV_LAB_S in decode_label(name)["surf_type"] for name in names]
                ):
                    hole_lines.append(line)

        if is_get_lam and not is_get_magnet:
            ext = "Master"
        else:
            ext = "Slave"

        # setup dict to store physical groups, key: group name, value: list of tags
        groups_dict = {}

        # get lines of magnets for processing their physical groups
        for id, magnet in enumerate(magnet_list):
            lines = gmsh.model.getBoundary([(2, magnet)])
            # store new group names in 'groups_dict' to set it later
            for line in lines:
                names = self._get_names_physical(
                    gmsh,
                    dimtag=[
                        1,
                        abs(line[1]),
                    ],
                )
                if not names:
                    print(f"Warning: Found magnet line without label - line {line[1]}")

                if is_get_magnet or (is_get_lam and line[1] in lam_lines):
                    for name in names:
                        label_dict = decode_label(name)
                        if HOLEM_LAB_S in label_dict["surf_type"]:
                            if (
                                line[1] in lam_lines
                            ):  # only lines with direct contact for now
                                # replace number and add 'Slave'
                                s = name.split("_")
                                s.append(ext)  # add extension
                                s[2] = str(id)  # renumber
                                key = "_".join(s)  # new name
                                if key not in groups_dict.keys():
                                    groups_dict[key] = []
                                groups_dict[key].append(line)

                # Test if other lines (with 'Hole' phy. group) and same phy. group ext.
                # ('Left', ...) share the same points to add them as well
                # TODO if not used with direct contact (see above),
                #      but I will keep it for Contact Simulation
                # if is_get_lam:
                #     # get the name of the magnets line
                #     s = None
                #     for name in names:
                #         if "Magnet" in name:
                #             s = name.split('_')
                #     # basic check of magnet line name
                #     if s is not None and len(s) >= 3:
                #         for hline in hole_lines:
                #             if hline != abs(line[1]): # skip if hole line == magnet line
                #                 # test for same extension ('Left', 'Right', ...)
                #                 names = _get_names_physical(gmsh, dimtag=[1, hline])
                #                 if any([s[2] in name for name in names]):
                #                     p1 = [x[1] for x in gmsh.model.getBoundary([line])]
                #                     p2 = [x[1] for x in gmsh.model.getBoundary([(1, hline)])]
                #                     pt = [p for p in p1 if p in p2]
                #                     if pt:
                #                         if len(s) == 3:
                #                             s.append('Master') # add extension
                #                         s[1] = str(id) # renumber
                #                         key = "_".join(s) # new name
                #                         if key not in groups_dict.keys():
                #                             groups_dict[key] = []
                #                         groups_dict[key].append((1, hline))
                #         if not is_hole_air:
                #             pass # TODO implement

            if is_get_magnet:
                # store new magnet body name
                s = "Magnet_" + str(id) + "_Body"
                groups_dict[s] = [
                    (2, magnet),
                ]

        if is_get_lam:
            # store new lamination body name
            for id, lam in enumerate(lam_list):
                s = "Lamination_" + str(id) + "_Body"
                if s not in groups_dict:
                    groups_dict[s] = []
                groups_dict[s].append((2, lam))

            # store hole if not air
            if not is_hole_air:
                pass  # TODO

        # add symmetry boundaries to keeper dict 'groups_dict'
        if is_get_lam:
            keeper_list = [
                "MASTER_ROTOR_BOUNDARY",
                "SLAVE_ROTOR_BOUNDARY",
                "Rotor_Tangential_Bridge",
                "Rotor_Radial_Bridge",
                "ROTOR_BORE_CURVE",
            ]

            for line in lam_lines:
                names = self._get_names_physical(gmsh, dimtag=[1, line])
                for key in keeper_list:
                    if any([key in name for name in names]):
                        if key not in groups_dict:
                            groups_dict[key] = []
                        groups_dict[key].append((1, line))

        # update group names
        grps = gmsh.model.getPhysicalGroups(-1)
        grp_names = [gmsh.model.getPhysicalName(*grp) for grp in grps]

        # delete unused surfaces
        RL = ROTOR_LAB_S + "-0_"
        del_list = [SHAFT_LAB, RL + HOLEV_LAB_S]
        if not is_get_magnet:
            del_list.append(RL + HOLEM_LAB_S)

        if not is_get_lam:
            rot_lam = (RL + LAM_LAB_S).lower()  # Rotor Lamination
            del_list.append(rot_lam)

        for grp, name in zip(grps, grp_names):
            if any([n in name.lower() for n in del_list]):
                entities = gmsh.model.getEntitiesForPhysicalGroup(*grp).tolist()
                for entity in entities:
                    if grp[0] == 2:
                        gmsh.model.geo.remove([(2, entity)], recursive=False)

        # set new physical group names after removing all 'old' physical groups
        gmsh.model.removePhysicalGroups(dimTags=[])
        for name in grp_names:
            gmsh.model.removePhysicalName(name)

        for key, values in groups_dict.items():
            # lines
            tags = [abs(dimtag[1]) for dimtag in values if dimtag[0] == 1]
            tags = list(set(tags))
            if tags:
                print(f"Add physical group {key} with lines {tags}")
                pg = gmsh.model.addPhysicalGroup(1, tags, tag=-1)
                gmsh.model.setPhysicalName(1, pg, key)
            # surfaces
            tags = [abs(dimtag[1]) for dimtag in values if dimtag[0] == 2]
            tags = list(set(tags))
            if tags:
                print(f"Add physical group {key} with surface {tags}")
                pg = gmsh.model.addPhysicalGroup(2, tags, tag=-1)
                gmsh.model.setPhysicalName(2, pg, key)

        # cleanup
        # get all entities
        gmsh.model.geo.synchronize()
        entities_all = gmsh.model.getEntities(dim=-1)
        surf_list = gmsh.model.getEntities(dim=2)
        print(surf_list)

        # get lines of surfaces
        line_list = []
        for surf in surf_list:
            line_list.extend(gmsh.model.getBoundary([surf]))
        line_list = [(line[0], abs(line[1])) for line in line_list]

        # remove all lines that are not part of the surfaces
        for entity in entities_all:
            if (entity[0], abs(entity[1])) not in line_list and entity[0] == 1:
                gmsh.model.geo.remove([entity], recursive=False)

        # entities_all = gmsh.model.getEntities(dim=-1)

        # remove unknown/unused physical groups
        # TODO

        # save
        gmsh.model.geo.synchronize()

        # gmsh.model.geo.mesh.setTransfiniteSurface(tag)
        for surf in surf_list:
            gmsh.model.mesh.setRecombine(2, surf[1])

        # gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 1)

        gmsh.model.mesh.generate(2)
        # gmsh.model.mesh.recombine()
        gmsh.model.mesh.refine()
        # gmsh.model.mesh.refine()
        # gmsh.model.mesh.recombine()
        # gmsh.model.mesh.refine()

        # save mesh or geo file depending on file extension
        filename, file_extension = splitext(file_out)

        if file_extension == ".geo":
            gmsh.write(filename + ".geo_unrolled")
            replace(filename + ".geo_unrolled", filename + file_extension)
        else:
            gmsh.model.mesh.generate(2)
            gmsh.write(file_out)

        # gmsh.fltk.run()      # Uncomment to launch Gmsh GUI

        # update group names once again
        grps = gmsh.model.getPhysicalGroups(-1)
        grp_names = [gmsh.model.getPhysicalName(*grp) for grp in grps]

        gmsh.finalize()

        return gmsh, grps, grp_names

    @staticmethod
    def _get_names_physical(gmsh, dimtag):
        grp_tags = gmsh.model.getPhysicalGroupsForEntity(*dimtag)
        names = [gmsh.model.getPhysicalName(1, tag) for tag in grp_tags]

        return names

    @staticmethod
    def _remove_entities(gmsh, labels):
        """
        Remove model entities that have one of the given labels in their physical
        groups names.

        Parameters
        ----------

        gmsh :
            gmsh object

        labels : list
            list of labels

        """
        # TODO add test that entities are not in surf or part of other 'keeper'entities
        # get all group names
        grps = gmsh.model.getPhysicalGroups(-1)
        grp_names = [gmsh.model.getPhysicalName(*grp) for grp in grps]

        # get entities that will be removed
        pt_list = []
        line_list = []
        surf_list = []
        for grp, name in zip(grps, grp_names):
            if any([label in name.lower() for label in labels]):
                dim = grp[0]
                entities = gmsh.model.getEntitiesForPhysicalGroup(dim, grp[1])
                if dim == 0:
                    pt_list.extend(entities.tolist())
                elif dim == 1:
                    line_list.extend(entities.tolist())
                elif dim == 2:
                    surf_list.extend(entities.tolist())

        # get lines of surfaces
        for surf in surf_list:
            lines = gmsh.model.getBoundary(
                [(2, surf)]
            )  # TODO check if holes are included
            for line in lines:
                line_list.append(line[1])

        # get points of lines
        for line in line_list:
            pts = gmsh.model.getBoundary([(1, line)])
            for pt in pts:
                pt_list.append(pt[1])

        # get unique list of entities to remove
        line_list = list(set(line_list))
        pt_list = list(set(pt_list))

        # delete unused entities
        for surf in surf_list:
            # gmsh.model.removeEntities((2, surf), recursive=False)
            gmsh.model.geo.remove([(2, surf)], recursive=False)

        for line in line_list:
            # gmsh.model.removeEntities((1, line), recursive=False)
            gmsh.model.geo.remove([(1, line)], recursive=False)

        for pt in pt_list:
            # gmsh.model.removeEntities((0, pt), recursive=False)
            gmsh.model.geo.remove([(0, pt)], recursive=False)

        # synchronize to apply changes to model
        gmsh.model.geo.synchronize()

    # cf Methods.Simulation.StructElmer.run
    def run(self):
        """Run the Structural module"""
        if self.parent is None:
            raise InputError(
                "ERROR: The Structural object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError(
                "ERROR: The Simulation object must be in an Output object to run"
            )

        output = self.parent.parent

        self.comp_axes(output)

        # setup the mesh
        mesh_names = self.gen_mesh(output)

        # setup the Elmer case file
        self.gen_case(output, mesh_names)

        # Compute the magnetic force according to the Force model
        self.solve_FEA(output)

        # Post processing
        self.get_meshsolution(output)

    # cf Methods.Simulation.StructElmer.solve_FEA
    def solve_FEA(self, output):
        """Solve the FEA simulation

        Parameters
        ----------


        Return
        ------


        """
        cwd = self.get_path_save_fea(output)  # current working dir

        logger = self.get_logger()

        for info in self._execute("ElmerSolver", cwd, logger):
            print(info, end="")

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Kmesh_fineness=1,
        path_name="",
        FEA_dict_enforced=-1,
        is_get_mesh=False,
        is_save_FEA=True,
        transform_list=-1,
        include_magnets=True,
        logger_name="Pyleecan.Structural",
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
            if "path_name" in list(init_dict.keys()):
                path_name = init_dict["path_name"]
            if "FEA_dict_enforced" in list(init_dict.keys()):
                FEA_dict_enforced = init_dict["FEA_dict_enforced"]
            if "is_get_mesh" in list(init_dict.keys()):
                is_get_mesh = init_dict["is_get_mesh"]
            if "is_save_FEA" in list(init_dict.keys()):
                is_save_FEA = init_dict["is_save_FEA"]
            if "transform_list" in list(init_dict.keys()):
                transform_list = init_dict["transform_list"]
            if "include_magnets" in list(init_dict.keys()):
                include_magnets = init_dict["include_magnets"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
        # Set the properties (value check and convertion are done in setter)
        self.Kmesh_fineness = Kmesh_fineness
        self.path_name = path_name
        self.FEA_dict_enforced = FEA_dict_enforced
        self.is_get_mesh = is_get_mesh
        self.is_save_FEA = is_save_FEA
        self.transform_list = transform_list
        self.include_magnets = include_magnets
        # Call Structural init
        super(StructElmer, self).__init__(logger_name=logger_name)
        # The class is frozen (in Structural init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        StructElmer_str = ""
        # Get the properties inherited from Structural
        StructElmer_str += super(StructElmer, self).__str__()
        StructElmer_str += "Kmesh_fineness = " + str(self.Kmesh_fineness) + linesep
        StructElmer_str += 'path_name = "' + str(self.path_name) + '"' + linesep
        StructElmer_str += (
            "FEA_dict_enforced = " + str(self.FEA_dict_enforced) + linesep
        )
        StructElmer_str += "is_get_mesh = " + str(self.is_get_mesh) + linesep
        StructElmer_str += "is_save_FEA = " + str(self.is_save_FEA) + linesep
        StructElmer_str += (
            "transform_list = "
            + linesep
            + str(self.transform_list).replace(linesep, linesep + "\t")
            + linesep
        )
        StructElmer_str += "include_magnets = " + str(self.include_magnets) + linesep
        return StructElmer_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Structural
        if not super(StructElmer, self).__eq__(other):
            return False
        if other.Kmesh_fineness != self.Kmesh_fineness:
            return False
        if other.path_name != self.path_name:
            return False
        if other.FEA_dict_enforced != self.FEA_dict_enforced:
            return False
        if other.is_get_mesh != self.is_get_mesh:
            return False
        if other.is_save_FEA != self.is_save_FEA:
            return False
        if other.transform_list != self.transform_list:
            return False
        if other.include_magnets != self.include_magnets:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Structural
        diff_list.extend(
            super(StructElmer, self).compare(
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
        if other._path_name != self._path_name:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._path_name)
                    + ", other="
                    + str(other._path_name)
                    + ")"
                )
                diff_list.append(name + ".path_name" + val_str)
            else:
                diff_list.append(name + ".path_name")
        if other._FEA_dict_enforced != self._FEA_dict_enforced:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._FEA_dict_enforced)
                    + ", other="
                    + str(other._FEA_dict_enforced)
                    + ")"
                )
                diff_list.append(name + ".FEA_dict_enforced" + val_str)
            else:
                diff_list.append(name + ".FEA_dict_enforced")
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
        if other._include_magnets != self._include_magnets:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._include_magnets)
                    + ", other="
                    + str(other._include_magnets)
                    + ")"
                )
                diff_list.append(name + ".include_magnets" + val_str)
            else:
                diff_list.append(name + ".include_magnets")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Structural
        S += super(StructElmer, self).__sizeof__()
        S += getsizeof(self.Kmesh_fineness)
        S += getsizeof(self.path_name)
        if self.FEA_dict_enforced is not None:
            for key, value in self.FEA_dict_enforced.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.is_get_mesh)
        S += getsizeof(self.is_save_FEA)
        if self.transform_list is not None:
            for value in self.transform_list:
                S += getsizeof(value)
        S += getsizeof(self.include_magnets)
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

        # Get the properties inherited from Structural
        StructElmer_dict = super(StructElmer, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        StructElmer_dict["Kmesh_fineness"] = self.Kmesh_fineness
        StructElmer_dict["path_name"] = self.path_name
        StructElmer_dict["FEA_dict_enforced"] = (
            self.FEA_dict_enforced.copy()
            if self.FEA_dict_enforced is not None
            else None
        )
        StructElmer_dict["is_get_mesh"] = self.is_get_mesh
        StructElmer_dict["is_save_FEA"] = self.is_save_FEA
        StructElmer_dict["transform_list"] = (
            self.transform_list.copy() if self.transform_list is not None else None
        )
        StructElmer_dict["include_magnets"] = self.include_magnets
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        StructElmer_dict["__class__"] = "StructElmer"
        return StructElmer_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Kmesh_fineness_val = self.Kmesh_fineness
        path_name_val = self.path_name
        if self.FEA_dict_enforced is None:
            FEA_dict_enforced_val = None
        else:
            FEA_dict_enforced_val = self.FEA_dict_enforced.copy()
        is_get_mesh_val = self.is_get_mesh
        is_save_FEA_val = self.is_save_FEA
        if self.transform_list is None:
            transform_list_val = None
        else:
            transform_list_val = self.transform_list.copy()
        include_magnets_val = self.include_magnets
        logger_name_val = self.logger_name
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Kmesh_fineness=Kmesh_fineness_val,
            path_name=path_name_val,
            FEA_dict_enforced=FEA_dict_enforced_val,
            is_get_mesh=is_get_mesh_val,
            is_save_FEA=is_save_FEA_val,
            transform_list=transform_list_val,
            include_magnets=include_magnets_val,
            logger_name=logger_name_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Kmesh_fineness = None
        self.path_name = None
        self.FEA_dict_enforced = None
        self.is_get_mesh = None
        self.is_save_FEA = None
        self.transform_list = None
        self.include_magnets = None
        # Set to None the properties inherited from Structural
        super(StructElmer, self)._set_None()

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

    def _get_path_name(self):
        """getter of path_name"""
        return self._path_name

    def _set_path_name(self, value):
        """setter of path_name"""
        check_var("path_name", value, "str")
        self._path_name = value

    path_name = property(
        fget=_get_path_name,
        fset=_set_path_name,
        doc="""Name of the path to save the FEA model

        :Type: str
        """,
    )

    def _get_FEA_dict_enforced(self):
        """getter of FEA_dict_enforced"""
        return self._FEA_dict_enforced

    def _set_FEA_dict_enforced(self, value):
        """setter of FEA_dict_enforced"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("FEA_dict_enforced", value, "dict")
        self._FEA_dict_enforced = value

    FEA_dict_enforced = property(
        fget=_get_FEA_dict_enforced,
        fset=_set_FEA_dict_enforced,
        doc="""To enforce user-defined values for FEA main parameters 

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
        doc="""To save FEA mesh for latter post-procesing (only possible with is_save_FEA set to True)

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
        doc="""To save FEA mesh and solution in .vtu file

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

    def _get_include_magnets(self):
        """getter of include_magnets"""
        return self._include_magnets

    def _set_include_magnets(self, value):
        """setter of include_magnets"""
        check_var("include_magnets", value, "bool")
        self._include_magnets = value

    include_magnets = property(
        fget=_get_include_magnets,
        fset=_set_include_magnets,
        doc="""Switch to include magents in the structural simulation

        :Type: bool
        """,
    )

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""

        pass


InputError = StructElmer.InputError


class ElmerProcessError(Exception):
    """Raised when there is an Elmer Binary process error"""

    pass
