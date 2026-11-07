# Experimental dataclass generated from Generator/ClassesRef/Simulation/OPMatrix.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ._pyleecan_class import PyleecanClass
from .op_dq import OPdq
from .op_dqf import OPdqf
from .op_slip import OPslip
from .var_simu import VarSimu


@dataclass(eq=False)
class OPMatrix(PyleecanClass):
    """Define the Operating Point of a variable speed simulation

    Attributes
    ----------
    N0 : ndarray or None
        Rotor speed
        Unit: rpm; Default: None
    Id_ref : ndarray or None
        d-axis current rms value
        Unit: Arms; Default: None
    Iq_ref : ndarray or None
        q-axis current rms value
        Unit: Arms; Default: None
    Ud_ref : ndarray or None
        d-axis voltage rms value
        Unit: Vrms; Default: None
    Uq_ref : ndarray or None
        q-axis voltage rms value
        Unit: Vrms; Default: None
    Tem_av_ref : ndarray or None
        Output average electromagnetic torque
        Unit: N.m; Default: None
    Pem_av_ref : ndarray or None
        Output/Input average Electromagnetic Power
        Unit: W; Default: None
    slip_ref : ndarray or None
        Rotor mechanical slip
        Default: None
    is_output_power : bool
        True if power given in OP_matrix is the output power, False if it is the input power
        Default: True
    If_ref : ndarray or None
        DC rotor current
        Unit: Arms; Default: None
    col_names : list or None
        Name of the columns from set_OP_matrix
        Default: []
    """

    N0: np.ndarray | None = None
    """Rotor speed"""
    Id_ref: np.ndarray | None = None
    """d-axis current rms value"""
    Iq_ref: np.ndarray | None = None
    """q-axis current rms value"""
    Ud_ref: np.ndarray | None = None
    """d-axis voltage rms value"""
    Uq_ref: np.ndarray | None = None
    """q-axis voltage rms value"""
    Tem_av_ref: np.ndarray | None = None
    """Output average electromagnetic torque"""
    Pem_av_ref: np.ndarray | None = None
    """Output/Input average Electromagnetic Power"""
    slip_ref: np.ndarray | None = None
    """Rotor mechanical slip"""
    is_output_power: bool = True
    """True if power given in OP_matrix is the output power, False if it is the input power"""
    If_ref: np.ndarray | None = None
    """DC rotor current"""
    col_names: list[Any] | None = field(default_factory=list)
    """Name of the columns from set_OP_matrix"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (VarSimu,)):
            raise TypeError(
                "OPMatrix parent must be an instance of VarSimu, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Simulation.OPMatrix.get_N_OP
    def get_N_OP(self):
        """return the number of Operating point in the matrix

        Parameters
        ----------
        self : OPMatrix
            An OPMatrix object

        Returns
        -------
        N_OP : int
            Number of operating point in the OP_matrix
        """

        if self.N0 is not None:
            return len(self.N0)
        elif self.Id_ref is not None:
            return len(self.Id_ref)
        elif self.Ud_ref is not None:
            return len(self.Ud_ref)
        else:
            raise OPMatrixException(
                "Unable to get the size of the Operating Matrix (call set_OP_matrix first)"
            )

    # Inlined from Methods.Simulation.OPMatrix.get_OP
    def get_OP(self, index):
        """Return the OP at the corresponding index

        Parameters
        ----------
        self : OPMatrix
            OPMatrix object to extrat the OP from
        index : int
            Index of the OP to extract

        Returns
        -------
        OP : OP
            OP object
        """

        if self.has_slip():
            OP = OPslip()
        elif self.If_ref is not None:
            OP = OPdqf()
        else:
            OP = OPdq()

        if self.N0 is not None:
            OP.N0 = self.N0[index]
        if self.Id_ref is not None and self.Iq_ref is not None:
            OP.set_Id_Iq(Id=self.Id_ref[index], Iq=self.Iq_ref[index])
        if self.Ud_ref is not None and self.Uq_ref is not None:
            OP.set_Ud_Uq(Ud=self.Ud_ref[index], Uq=self.Uq_ref[index])
        if self.Tem_av_ref is not None:
            OP.Tem_av_ref = self.Tem_av_ref[index]
        if self.Pem_av_ref is not None:
            if self.is_output_power in [None, True]:
                OP.Pem_av_ref = self.Pem_av_ref[index]
            else:
                OP.Pem_av_in = self.Pem_av_ref[index]
        if self.slip_ref is not None:
            OP.slip_ref = self.slip_ref[index]
        if self.If_ref is not None:
            OP.If_ref = self.If_ref[index]

        return OP

    # Inlined from Methods.Simulation.OPMatrix.get_OP_array
    def get_OP_array(self, *arg_list):
        """get the OP_matrix by identifying the columns
        Ex: get_OP_array("N0", "Iq", "Iq", "Tem")
        get_OP_array() calls get_OP_array("N0", "Id", "Iq", "Tem", "Pem")

        Parameters
        ----------
        self : OPMatrix
            OPMatrix object to update
        *arg_list : list of str
            arguments to select the OP_matrix columns name

        Returns
        -------
        OP_matrix : ndarray
            Operating point matrix with the selected columns (Array (N_OP, len(arg_list)))
        """

        # Extract arg_list it the function called from another script with *arg_list
        if len(arg_list) == 1 and type(arg_list[0]) == tuple:
            arg_list = arg_list[0]
        arg_list = list(arg_list)

        # "all" returns all the columns set by the latest set_OP_array
        if len(arg_list) == 1 and arg_list[0].lower() in ["all", "al", "a"]:
            if self.col_names is not None and len(self.col_names) > 0:
                arg_list = self.col_names
            else:
                arg_list = []
                if self.N0 is not None:
                    arg_list.append("N0")
                if self.Id_ref is not None:
                    arg_list.append("Id")
                if self.Iq_ref is not None:
                    arg_list.append("Iq_ref")
                if self.Tem_av_ref is not None:
                    arg_list.append("Tem")
                if self.Pem_av_ref is not None:
                    arg_list.append("Pem")

        # Init OP_matrix
        N_OP = self.get_N_OP()
        OP_matrix = np.zeros((N_OP, len(arg_list)))

        # Setup default argument (N0, Id, Iq, Tem, Pem)
        if len(arg_list) == 0:
            if self.N0 is not None:
                arg_list.append("N0")
            if self.Id_ref is not None:
                arg_list.append("Id")
            if self.Iq_ref is not None:
                arg_list.append("Iq")
            if self.Tem_av_ref is not None:
                arg_list.append("Tem")
            if self.Pem_av_ref is not None:
                arg_list.append("Pem")

        arg_list_lower = [arg.lower() for arg in arg_list]
        # Convertion I0/Phi0 to Id/Iq will be done later
        is_convert_I0 = False
        if "i0" in arg_list_lower and (
            "phi0" in arg_list_lower or "iphi0" in arg_list_lower
        ):
            I0_index = arg_list_lower.index("i0")
            if "phi0" in arg_list_lower:
                Phi0_index = arg_list_lower.index("phi0")
            else:
                Phi0_index = arg_list_lower.index("iphi0")
            is_convert_I0 = True
            arg_list[I0_index] = "Id"
            arg_list[Phi0_index] = "Iq"
        # Convertion U0/UPhi0 to Ud/Uq
        is_convert_U0 = False
        if "u0" in arg_list_lower and "uphi0" in arg_list_lower:
            U0_index, UPhi0_index = (
                arg_list_lower.index("u0"),
                arg_list_lower.index("uphi0"),
            )
            U0 = OP_matrix[:, U0_index]
            UPhi0 = OP_matrix[:, UPhi0_index]
            is_convert_U0 = True
            arg_list[U0_index] = "Ud"
            arg_list[UPhi0_index] = "Uq"

        # Set column by column according to arg_list
        for ii in range(len(arg_list)):
            if arg_list[ii].lower() in ["n0", "no", "0n", "on"]:
                OP_matrix[:, ii] = self.N0[:]
            elif arg_list[ii].lower() in ["id", "di", "id_ref"]:
                OP_matrix[:, ii] = self.Id_ref[:]
            elif arg_list[ii].lower() in ["iq", "qi", "iq_ref"]:
                OP_matrix[:, ii] = self.Iq_ref[:]
            elif arg_list[ii].lower() in ["tem", "t", "tem_av", "tem_av_ref"]:
                OP_matrix[:, ii] = self.Tem_av_ref[:]
            elif arg_list[ii].lower() in ["pem", "p", "pem_av", "pem_av_ref"]:
                OP_matrix[:, ii] = self.Pem_av_ref[:]
            elif arg_list[ii].lower() in ["ud", "du", "ud_ref"]:
                OP_matrix[:, ii] = self.Ud_ref[:]
            elif arg_list[ii].lower() in ["uq", "qu", "uq_ref"]:
                OP_matrix[:, ii] = self.Uq_ref[:]
            elif arg_list[ii].lower() in ["if", "fi"]:
                OP_matrix[:, ii] = self.If_ref[:]
            else:
                raise OPMatrixException(
                    "Error in OP_matrix.get_OP_array, unknow column name for index "
                    + str(ii)
                    + " in "
                    + str(arg_list)
                )

        # Convertion
        if is_convert_I0:
            Z = OP_matrix[:, I0_index] + 1j * OP_matrix[:, Phi0_index]
            OP_matrix[:, I0_index] = abs(Z)
            OP_matrix[:, Phi0_index] = np.angle(Z)
        if is_convert_U0:
            Z = OP_matrix[:, U0_index] + 1j * OP_matrix[:, UPhi0_index]
            OP_matrix[:, U0_index] = abs(Z)
            OP_matrix[:, UPhi0_index] = np.angle(Z)
        return OP_matrix

    # Inlined from Methods.Simulation.OPMatrix.get_OP_list
    def get_OP_list(self):
        """Return the list of Operating Point defined by the matrix

        Parameters
        ----------
        self : OPMatrix
            An OPMatrix object

        Returns
        -------
        OP_list : [OP]
            List of OP objects
        """

        N_OP = self.get_N_OP()

        OP_list = []
        for ii in range(N_OP):
            OP_list.append(self.get_OP(ii))

        return OP_list

    # Inlined from Methods.Simulation.OPMatrix.has_Pem
    def has_Pem(self):
        """Check if the Power column is set

        Parameters
        ----------
        self : OPMatrix
            OPMatrix object

        Returns
        -------
        has_Pem : bool
            True if the Power column is set
        """

        return self.Pem_av_ref is not None

    # Inlined from Methods.Simulation.OPMatrix.has_slip
    def has_slip(self):
        """Check if the slip column is set

        Parameters
        ----------
        self : OPMatrix
            OPMatrix object

        Returns
        -------
        has_slip : bool
            True if the slip_ref column is set
        """

        return self.slip_ref is not None

    # Inlined from Methods.Simulation.OPMatrix.has_Tem
    def has_Tem(self):
        """Check if the Torque column is set

        Parameters
        ----------
        self : OPMatrix
            OPMatrix object

        Returns
        -------
        has_Tem : bool
            True if the Torque column is set
        """

        return self.Tem_av_ref is not None

    # Inlined from Methods.Simulation.OPMatrix.set_OP_array
    def set_OP_array(self, OP_matrix, *arg_list):
        """Set the OP_matrix by identifying the columns
        Ex: set_OP_array(OP_matrix, "N0", "Iq", "Iq", "Tem")
        set_OP_array(OP_matrix) calls set_OP_array(OP_matrix, "N0", "Id", "Iq", "Tem", "Pem")
        I0/Phi0 are converted to Id, Iq, U0/UPhi0 are converted to Ud, Uq

        Parameters
        ----------
        self : OPMatrix
            OPMatrix object to update
        OP_matrix : ndarray
            OP_matrix to set in the object
        *arg_list : list of str
            arguments to specify the OP_matrix columns name
        """

        # Clean previous data (keep is_output_power)
        is_output_power = self.is_output_power
        self._set_None()
        self.is_output_power = is_output_power

        # Extract arg_list it the function called from another script with *arg_list
        if len(arg_list) == 1 and type(arg_list[0]) == tuple:
            arg_list = arg_list[0]
        arg_list = list(arg_list)

        # Setup default argument (N0, Id, Iq, Tem, Pem)
        if len(arg_list) == 0:
            N = OP_matrix.shape[1]
            if N > 0:
                arg_list.append("N0")
            if N > 1:
                arg_list.append("Id")
            if N > 2:
                arg_list.append("Iq")
            if N > 3:
                arg_list.append("Tem")
            if N > 4:
                arg_list.append("Pem")
        if len(arg_list) == 3 and OP_matrix.shape[1] >= 4:
            arg_list.append("Tem")
        if len(arg_list) == 4 and OP_matrix.shape[1] == 5:
            arg_list.append("Pem")
        if len(arg_list) != OP_matrix.shape[1]:
            raise OPMatrixException(
                "Error missing column name for OP_matrix.set_OP_array, "
                + str(OP_matrix.shape[1])
                + " expected "
                + str(arg_list)
            )

        arg_list_lower = [arg.lower() for arg in arg_list]
        # Convertion I0/Phi0 to Id/Iq
        if "i0" in arg_list_lower and (
            "phi0" in arg_list_lower or "iphi0" in arg_list_lower
        ):
            I0_index = arg_list_lower.index("i0")
            if "phi0" in arg_list_lower:
                Phi0_index = arg_list_lower.index("phi0")
            else:
                Phi0_index = arg_list_lower.index("iphi0")
            I0 = OP_matrix[:, I0_index]
            Phi0 = OP_matrix[:, Phi0_index]
            Z = I0 * np.exp(1j * Phi0)
            OP_matrix[:, I0_index] = Z.real
            OP_matrix[:, Phi0_index] = Z.imag
            arg_list[I0_index] = "Id"
            arg_list[Phi0_index] = "Iq"
        # Convertion I0 to Id (assume Phi0=0)
        elif "i0" in arg_list_lower and "phi0" not in arg_list_lower:
            OP_matrix = np.hstack((OP_matrix, np.zeros((OP_matrix.shape[0], 1))))
            arg_list[arg_list_lower.index("i0")] = "Id"
            arg_list.append("Iq")

        # Convertion U0/UPhi0 to Ud/Uq
        if "u0" in arg_list_lower and "uphi0" in arg_list_lower:
            U0_index, UPhi0_index = (
                arg_list_lower.index("u0"),
                arg_list_lower.index("uphi0"),
            )
            U0 = OP_matrix[:, U0_index]
            UPhi0 = OP_matrix[:, UPhi0_index]
            Z = U0 * np.exp(1j * UPhi0)
            OP_matrix[:, U0_index] = Z.real
            OP_matrix[:, UPhi0_index] = Z.imag
            arg_list[U0_index] = "Ud"
            arg_list[UPhi0_index] = "Uq"
        # Convertion U0 to Ud (assume UPhi0=0)
        elif "u0" in arg_list_lower and "uphi0" not in arg_list_lower:
            OP_matrix = np.hstack((OP_matrix, np.zeros((OP_matrix.shape[0], 1))))
            arg_list[arg_list_lower.index("u0")] = "Ud"
            arg_list.append("Uq")

        # Set column by column according to arg_list
        for ii in range(OP_matrix.shape[1]):
            if arg_list[ii].lower() in ["n0", "no", "0n", "on"]:
                self.N0 = OP_matrix[:, ii]
            elif arg_list[ii].lower() in ["id", "di", "id_ref"]:
                self.Id_ref = OP_matrix[:, ii]
            elif arg_list[ii].lower() in ["iq", "qi", "iq_ref"]:
                self.Iq_ref = OP_matrix[:, ii]
            elif arg_list[ii].lower() in ["tem", "t", "tem_av", "tem_av_ref", "torque"]:
                self.Tem_av_ref = OP_matrix[:, ii]
            elif arg_list[ii].lower() in ["pem", "p", "pem_av", "pem_av_ref", "power"]:
                self.Pem_av_ref = OP_matrix[:, ii]
            elif arg_list[ii].lower() in ["ud", "du", "ud_ref"]:
                self.Ud_ref = OP_matrix[:, ii]
            elif arg_list[ii].lower() in ["uq", "qu", "uq_ref"]:
                self.Uq_ref = OP_matrix[:, ii]
            elif arg_list[ii].lower() in ["slip", "slip_ref"]:
                self.slip_ref = OP_matrix[:, ii]
            elif arg_list[ii].lower() in ["if", "fi"]:
                self.If_ref = OP_matrix[:, ii]
            else:
                raise OPMatrixException(
                    "Error in OP_matrix.set_OP_array, unknow column name for index "
                    + str(ii)
                    + " in "
                    + str(arg_list)
                )

        # Store column names for get_OP_array("all")
        self.col_names = arg_list

    class OPMatrixException(Exception):
        """Raise when OP_matrix was wrongly defined"""


OPMatrixException = OPMatrix.OPMatrixException
