# Experimental dataclass generated from Generator/ClassesRef/Simulation/StructElmer.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
import subprocess
from dataclasses import dataclass, field
from typing import Any

import gmsh
import numpy as np

from ..Functions_new.get_path_binary import get_path_binary
from ..Functions_new.GMSH.draw_GMSH import draw_GMSH
from ..Functions_new.labels import (
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
    SHAFT_LAB,
    SHAFTSL_LAB,
    SHAFTSR_LAB,
    STATOR_LAB,
    STATOR_LAB_S,
    WIND_LAB_S,
    YSL_LAB,
    YSR_LAB,
    decode_label,
)
from ._error import InputError
from .elmer_results_vtu import ElmerResultsVTU
from .section import MATC, File, Section, Variable
from .solver_input_file import SolverInputFile
from .structural import Structural


@dataclass(eq=False)
class StructElmer(Structural):
    """Structural module: FEA model with Elmer

    Attributes
    ----------
    Kmesh_fineness : float
        global coefficient to adjust mesh fineness in FEMM (1 : default , > 1 : finner , < 1 : less fine)
        Default: 1
    path_name : str or None
        Name of the path to save the FEA model
        Default: None
    FEA_dict_enforced : dict or None
        To enforce user-defined values for FEA main parameters
        Default: {}
    is_get_mesh : bool
        To save FEA mesh for latter post-procesing (only possible with is_save_FEA set to True)
        Default: False
    is_save_FEA : bool
        To save FEA mesh and solution in .vtu file
        Default: True
    transform_list : list
        List of dictionary to apply transformation on the machine surfaces. Key: label (to select the surface), type (rotate or translate), value (alpha or delta)
        Default: []
    include_magnets : bool
        Switch to include magents in the structural simulation
        Default: True
    """

    Kmesh_fineness: float = 1
    """global coefficient to adjust mesh fineness in FEMM (1 : default , > 1 : finner , < 1 : less fine)"""
    path_name: str | None = None
    """Name of the path to save the FEA model"""
    FEA_dict_enforced: dict[str, Any] | None = field(default_factory=dict)
    """To enforce user-defined values for FEA main parameters """
    is_get_mesh: bool = False
    """To save FEA mesh for latter post-procesing (only possible with is_save_FEA set to True)"""
    is_save_FEA: bool = True
    """To save FEA mesh and solution in .vtu file"""
    transform_list: list[Any] = field(default_factory=list)
    """List of dictionary to apply transformation on the machine surfaces. Key: label (to select the surface), type (rotate or translate), value (alpha or delta)"""
    include_magnets: bool = True
    """Switch to include magents in the structural simulation"""

    # Inlined from Methods.Simulation.StructElmer.gen_case
    def gen_case(self, output, mesh_names, *, ID_LAM=1, ID_MAG=2):
        """Setup the Elmer Case file (.sif file)"""

        # get the save path
        save_dir = self.get_path_save_fea(output)

        sif_file = os.path.join(save_dir, "case.sif")

        # save solver start info
        start_file = os.path.join(save_dir, "ELMERSOLVER_STARTINFO")

        with open(start_file, "wt") as fout:
            fout.write(os.path.split(sif_file)[1])

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

    # Inlined from Methods.Simulation.StructElmer.gen_mesh
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
        file_gmsh_geo = os.path.join(save_dir, "GMSH_Machine_Model.geo")

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
            os.path.join(save_dir, lam_name),
            is_get_lam=True,
            is_get_magnet=False,
        )

        if self.include_magnets:
            _, _, names["Magnets"] = self.process_mesh(
                file_gmsh_geo,
                os.path.join(save_dir, mag_name),
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

    # Inlined from Methods.Simulation.StructElmer.get_meshsolution
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
        ElmerVtu.file_path = os.path.join(fea_path, "Results", "case_t0001.vtu")

        output.struct.meshsolution = ElmerVtu.build_meshsolution()

        return True

    # Inlined from Methods.Simulation.StructElmer.get_path_save_fea
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

        save_dir = os.path.join(path_res, "Elmer_Elasticity")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        return save_dir

    # Inlined from Methods.Simulation.StructElmer.process_mesh
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
        filename, file_extension = os.path.splitext(file_out)

        if file_extension == ".geo":
            gmsh.write(filename + ".geo_unrolled")
            os.replace(filename + ".geo_unrolled", filename + file_extension)
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

    # Inlined from Methods.Simulation.StructElmer.run
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

    # Inlined from Methods.Simulation.StructElmer.solve_FEA
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
