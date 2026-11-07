# Experimental dataclass generated from Generator/ClassesRef/Output/LUT.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ..Functions.Load.import_class import import_class
from .xoutput import XOutput


@dataclass(eq=False)
class LUT(XOutput):
    """Abstract class for Look Up Table (LUT)

    Attributes
    ----------
    """

    # Inlined from Methods.Output.LUT.get_eec
    def get_eec(self):
        """Get the Electrical Equivalent Circuit

        Parameters
        ----------
        self : LUT
            a LUT object

        Returns
        ----------
        eec : EEC
            Electrical Equivalent Circuit
        """

        if self.simu is None:
            return None
        if self.simu.elec is None:
            return None
        return self.simu.elec.eec

    # Inlined from Methods.Output.LUT.get_OP_array
    def get_OP_array(self, *arg_list):
        """Get the Operating Point array

        Parameters
        ----------
        self : LUT
            a LUT object

        Returns
        ----------
        OP_array : ndarray
            Operating Point Matrix object
        """

        OPM = self.get_OP_matrix_obj()
        return OPM.get_OP_array(*arg_list)

    # Inlined from Methods.Output.LUT.get_OP_matrix_obj
    def get_OP_matrix_obj(self):
        """Get the Operating Point Matrix

        Parameters
        ----------
        self : LUT
            a LUT object

        Returns
        ----------
        OP_matrix : OPMatrix
            Operating Point Matrix object
        """

        if self.simu is None:
            return None
        var_load = self.simu.get_var_load()
        if var_load is None:
            return None
        return var_load.OP_matrix

    # Inlined from Methods.Output.LUT.get_phase_dir
    def get_phase_dir(self):
        """Return the Rotation direction of the stator phases

        Parameters
        ----------
        self : LUT
            A LUT object

        Returns
        -------
        phase_dir : int
            Rotation direction of the stator phase
        """

        return self.output_list[0].elec.phase_dir

    # Inlined from Methods.Output.LUT.set_default_simulation
    def set_default_simulation(self, machine, OP_matrix=None, name=None):
        """Set the default simulation to compute the LUT

        Parameters
        ----------
        self : LUT
            A LUT object
        machine : Machine
            The machine to use in the simulation
        OP_matrix : OP_matrix/ndarray
            OP_matrix to use for VarLoadCurrent
        name : str
            Name of the simulation
        """

        # Dynamic import to avoid loop
        Simu1 = import_class("pyleecan.Classes", "Simu1")
        InputCurrent = import_class("pyleecan.Classes", "InputCurrent")
        VarLoadCurrent = import_class("pyleecan.Classes", "VarLoadCurrent")
        OPdq = import_class("pyleecan.Classes", "OPdq")
        MagFEMM = import_class("pyleecan.Classes", "MagFEMM")
        PostLUT = import_class("pyleecan.Classes", "PostLUT")

        if name is None:
            name = "comp_LUT_" + machine.name
        simu = Simu1(name=name, machine=machine)

        # Definition of the input
        simu.input = InputCurrent(
            Nt_tot=8 * 12,
            Na_tot=8 * 200,
            OP=OPdq(N0=1000, Id_ref=0, Iq_ref=0),  # Will be overwritten
        )

        # Set varspeed simulation
        simu.var_simu = VarLoadCurrent(
            is_keep_all_output=True,
            stop_if_error=True,
        )
        if OP_matrix is not None:
            simu.var_simu.set_OP_matrix_obj(OP_matrix)

        # Define second simu for FEMM comparison
        simu.mag = MagFEMM(is_periodicity_a=True, is_periodicity_t=True, nb_worker=4)

        # Postprocessing
        simu.var_simu.postproc_list = [PostLUT(is_save_LUT=True)]

        # Set simu in LUT
        self.simu = simu
