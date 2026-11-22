from ....classes_common.errors import FieldMissingError
from ....classes_common.logger_context import get_logger
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
import os
from shutil import copyfile

import numpy as np

from ....classes_common.femm_handler import _FEMMHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.mesh.mesh_mat import MeshMat
    from ....Classes_new.output.output import Output
    from ....Functions_new.FEMM.femm_pyleecan import femm_pyleecan


def solve_FEMM_parallel(
    self,
    femm: femm_pyleecan,
    output: Output,
    out_dict: dict,
    FEMM_dict: dict,
    sym: int,
    Nt: int,
    angle: np.ndarray,
    Is: np.ndarray,
    Ir: np.ndarray,
    angle_rotor: np.ndarray,
    filename: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, MeshMat, dict]:
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
    # Local import: circular import with the class module
    from ....Functions_new.FEMM.femm_pyleecan import femm_pyleecan

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
    logger = get_logger(self)

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
    femm_handler = [femm_pyleecan() for i in range(nb_worker)]
    femm_files = [
        fem_file[:-4] + "_" + str(i) + ".fem" for i in range(1, nb_worker + 1)
    ]
    start_time_list = [sum(nb_task_worker[:i]) for i in range(nb_worker)]
    end_time_list = [sum(nb_task_worker[: i + 1]) for i in range(nb_worker)]

    # Gathering the different arguments for each instance
    args = [
        [i, j, k, l]
        for i, j, k, l in zip(femm_handler, femm_files, start_time_list, end_time_list)
    ]

    # append femm_handler to handler_list
    if output.mag.internal is None:
        raise FieldMissingError("OutMag.internal is None: the FEMM handlers are stored in OutMagFEMM")
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
            get_logger(self).warning("Could not remove file: " + filename)

        try:
            os.remove(fem_file[:-4] + "_" + str(w) + ".ans")
        except Exception:
            filename = fem_file[:-4] + "_" + str(w) + ".ans"
            get_logger(self).warning("Could not remove file: " + filename)

    return B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem
