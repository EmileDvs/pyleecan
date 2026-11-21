from ....classes_common.logger_context import get_logger
import os


import numpy as np

from ....classes_common.femm_handler import _FEMMHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.mesh.mesh_mat import MeshMat
    from ....Classes_new.output.output import Output


def solve_FEMM(
    self,
    femm,
    output: Output,
    out_dict: dict,
    FEMM_dict: dict,
    sym: int,
    Nt: int,
    angle: np.ndarray,
    Is: np.ndarray,
    Ir: np.ndarray,
    angle_rotor: np.ndarray,
    is_close_femm: bool,
    filename: str | None = None,
    start_t: int = 0,
    end_t: int | None = None,
    Nmess=4,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, MeshMat, dict, np.ndarray]:
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
    B_elem: ndarray
        3D Magnetic flux density for each element (Nelem, 3) [T]
    H_elem : ndarray
        3D Magnetic field for each element (Nelem, 3) [A/m]
    mu_elem : ndarray
        Magnetic relative permeability for each element (Nelem,1) []
    A_node : ndarray
        Magnetic Vector Potential for each node (Nnode,1) []
    meshFEMM: MeshMat
        Object containing magnetic mesh
    groups: dict
        Dict whose values are group label and values are array of indices of related elements
    A_elem : ndarray
        Magnetic Vector Potential for each elem (Nelem,1) []

    """

    # Local import: circular import with the class module
    from ....Functions_new.FEMM.femm_pyleecan import femm_pyleecan

    logger = get_logger(self)
    is_sliding_band = self.is_sliding_band

    if filename is not None:
        # Open FEMM instance if filename is not None (parallel case)
        try:
            # Try to open FEMM instance if handler already exists (first parallelized handler)
            femm.handler.openfemm(1)
        except Exception:
            # Create a new FEMM handler in case of parallelization on another FEMM instance
            femm = femm_pyleecan()
            output.mag.internal.handler_list.append(femm)
            # Open a new FEMM instance associated to new handler
            femm.handler.openfemm(1)
        # Open FEMM file
        femm.handler.opendocument(filename)
    else:
        # FEMM instance and file is already open, get filename from output
        filename = self.get_path_save_fem(output)

    if is_sliding_band and self.is_set_previous:
        # Check result .ans file existence and delete it if it exists
        ans_file = (
            (os.path.splitext(filename)[0] + ".ans").replace("\\", "/").replace("//", "/")
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
                logger.info("Solving time steps: " + str(int(k2 / Nmess * 100)) + "%")
                k2 += 1

        elif ii == 0:
            logger.info("Computing Airgap Flux in FEMM")
        k1 += 1

        if not is_sliding_band:
            # Reload model for each time step if no sliding band
            if ii > start_t:
                femm.handler.opendocument(fileinit_fem)
            femm.handler.mi_saveas(filetemp_fem)

        # Update rotor position and currents
        femm.update_FEMM_simulation(
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
                femm.handler.mi_setprevious(ans_file, 0)
            else:
                logger.warning("Cannot reuse result .ans file: " + ans_file)
        else:
            # Make sure that no file path is filled in FEMM model
            femm.handler.mi_setprevious("", 0)

        # Run the computation
        femm.handler.mi_analyze()

        # Load results
        femm.handler.mi_loadsolution()

        # Get the flux result
        if is_sliding_band:
            for jj in range(Na):
                (
                    out_dict["B_{rad}"][ii, jj],
                    out_dict["B_{circ}"][ii, jj],
                ) = femm.handler.mo_getgapb("bc_ag2", angle[jj] * 180 / np.pi)
        else:
            for jj in range(Na):
                B = femm.handler.mo_getb(Rag * np.cos(angle[jj]), Rag * np.sin(angle[jj]))
                out_dict["B_{rad}"][ii, jj] = B[0] * np.cos(angle[jj]) + B[1] * np.sin(
                    angle[jj]
                )
                out_dict["B_{circ}"][ii, jj] = -B[0] * np.sin(angle[jj]) + B[1] * np.cos(
                    angle[jj]
                )

        # Compute the torque
        if self.is_calc_torque_energy:
            label_rot = machine.rotor.get_label()
            rotor_groups = FEMM_dict["groups"]["lam_group_list"][label_rot]
            out_dict["Tem"][ii] = femm.comp_FEMM_torque(
                rotor_groups=rotor_groups, sym=sym
            )

        if "Phi_wind" in out_dict:
            # Phi_wind computation
            # TODO fix inconsistency for multi lam machines here
            for key in out_dict["Phi_wind"].keys():
                out_dict["Phi_wind"][key][ii, :] = femm.comp_FEMM_Phi_wind(
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
            meshFEMMi, Bi, Hi, mui, Ani, groupsi, Aei = self.get_FEMM_mesh_results(
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
            femm.handler.mi_close()
            femm.handler.mo_close

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
        femm.handler.closefemm()
        output.mag.internal.handler_list.remove(femm)

    out_dict["Rag"] = Rag

    return B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem
