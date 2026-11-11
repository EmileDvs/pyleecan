# Experimental dataclass generated from Generator/ClassesRef/Simulation/VarLoad.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np

from ..Functions.load import load_init_dict
from ._check import check_var
from ._import import import_class
from .op_matrix import OPMatrix
from .var_simu import VarSimu


@dataclass(eq=False)
class VarLoad(VarSimu):
    """Abstract class to generate multi-simulation by changing the operating point

    Attributes
    ----------
    OP_matrix : OPMatrix or None
        Operating point matrix object
        Default: None
    """

    NAME: ClassVar = "Variable Load"
    OP_matrix: OPMatrix | None = field(
        default=None, metadata={"default_class": "OPMatrix"}
    )
    """Operating point matrix object"""

    # Inlined from Methods.Simulation.VarLoad._set_OP_matrix
    def _set_OP_matrix(self, value):
        """setter of OP_matrix"""
        if isinstance(value, list):
            value = np.array(value)
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(value.get("__class__"), "OP_matrix")
            value = class_obj(init_dict=value)
        elif isinstance(value, np.ndarray):
            # Conver matrix to OP_matrix object
            class_obj = import_class("OPMatrix", "OP_matrix")
            value_obj = class_obj()
            value_obj._set_None()
            # N0, Id, Iq, Tem, Pem is the most commun OP_matrix format
            if value.shape[1] == 5:
                value_obj.set_OP_array(value, "N0", "Id", "Iq", "Tem", "Pem")
            elif value.shape[1] == 4:
                value_obj.set_OP_array(value, "N0", "Id", "Iq", "Tem")
            else:
                value_obj.set_OP_array(value, "N0", "Id", "Iq")
            value = value_obj
        elif type(value) is int and value == -1:  # Default constructor
            OP_matrix = import_class("OPMatrix", "OP_matrix")
            value = OP_matrix()
        check_var("OP_matrix", value, "OPMatrix")
        self._OP_matrix = value

        if self._OP_matrix is not None:
            self._OP_matrix.parent = self

    # Inlined from Methods.Simulation.VarLoad.get_OP_array
    def get_OP_array(self, *arg_list):
        """Return the OP matrix

        Parameters
        ----------
        self : VarLoadCurrent
            A VarLoadCurrent object

        Returns
        -------
        OP_matrix : ndarray
            Operating Points matrix
        """

        return self.OP_matrix.get_OP_array(*arg_list)

    # Inlined from Methods.Simulation.VarLoad.get_ref_simu_index
    def get_ref_simu_index(self, ref_simu, simu_dict):
        """Get the index of the reference simulation (None if must be computed)

        Parameters
        ----------
        self : VarLoadCurrent
            A VarLoadCurrent object
        ref_simu : Simulation
            A Simulation object (reference simulation)
        simu_dict : dict
            Dict of simulations

        Returns
        -------
        ref_simu_index : int
            index of the reference simulation (None if must be computed)
        """
        ref_simu_index = None
        logger = self.get_logger()
        for ii, simu in enumerate(simu_dict["simulation_list"]):
            diff_list = simu.input.compare(ref_simu.input, name="input")
            # # Remove not meaningfull differences
            # if "simu.mag.file_name" in diff_list:
            #     diff_list.remove("simu.mag.file_name")
            if len(diff_list) == 0:
                ref_simu_index = ii
                break
        if ref_simu_index is None:
            logger.warning(
                "Reference Operating point is not in OP_matrix, one extra simulation will be computed"
            )

        return ref_simu_index

    # Inlined from Methods.Simulation.VarLoad.set_OP_array
    def set_OP_array(self, OP_matrix, *arg_list, is_update_input=True, input_index=0):
        """Set the OP_matrix and update the input if needed
        (To make sure that ref simu is in the OP_matrix)
        Ex: set_OP_array(OP_matrix, "N0", "Iq", "Iq", "Tem")

        Parameters
        ----------
        self : VarLoad
            A VarLoad object
        OP_matrix : ndarray
            OP_matrix to set
        *arg_list : several str
            To specify the OP_matrix column ("N0", "Id", "Iq"...)
        is_update_input : bool
            True to update the input
        input_index : int
            Index of the OP from the OP_matrix to set in the input (if is_update_input)
        """

        if isinstance(OP_matrix, np.ndarray):
            self.OP_matrix = OPMatrix()
            self.OP_matrix.set_OP_array(OP_matrix, *arg_list)
        else:
            self.OP_matrix = OP_matrix

        if not is_update_input or OP_matrix is None:
            return

        # Scan parent to find the input
        Sinput = None
        if self.parent is not None and hasattr(self.parent, "input"):
            Sinput = self.parent.input
        elif (
            self.parent is not None
            and self.parent.parent is not None
            and hasattr(self.parent.parent, "input")
        ):
            Sinput = self.parent.parent.input
        if Sinput is None:
            self.get_logger().warning("Can't find input when setting OP_matrix")
            return

        # Set the input OP
        if input_index >= self.OP_matrix.get_N_OP():
            self.get_logger.warning(
                "Index "
                + str(input_index)
                + " is not in the OP_matrix with "
                + str(self.OP_matrix.get_N_OP())
                + " OP(s)"
            )
            input_index = 0
        Sinput.OP = self.OP_matrix.get_OP(input_index)
