from ....classes_common.logger_context import get_logger
import os
import subprocess

from ....Classes_new.output.out_mag_elmer import OutMagElmer
from . import _get_BP_dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data import Data
    from ....Classes_new.output.output import Output


def comp_flux_airgap(self, output: Output, axes_dict: dict[str, Data], Is_val=None, Ir_val=None):
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
    # Local import: circular import with the class module
    from ....Functions_new.GMSH.gmsh_pyleecan import gmsh_pyleecan

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
        get_logger(self).debug("Drawing machine in GMSH...")
        output.mag.internal.FEA_dict = gmsh_pyleecan.draw_GMSH(
            output=output,
            sym=sym,
            boundary_prop=_get_BP_dict(),
            is_lam_only_S=False,
            is_lam_only_R=False,
            user_mesh_dict=self.FEA_dict,
            is_sliding_band=True,
            is_airbox=True,
            path_save=gmsh_filename,
        )

    else:
        get_logger(self).debug("Reusing the FEA file: " + self.import_file)
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
