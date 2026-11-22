# Experimental pydantic model generated from Generator/ClassesRef/Simulation/ForceMT.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import numpy as np

from ...classes_common.errors import FieldMissingError, NotImplementedYetError
from .force import Force

if TYPE_CHECKING:
    from ..output.output import Output
    from ..scidatatool.data import Data


class ForceMT(Force):
    """Force Maxwell tensor model for radial flux machines

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.ForceMT.comp_force
    def comp_force(self, output: Output, axes_dict: dict[str, Data]) -> dict:
        """Compute the air-gap surface force based on Maxwell Tensor (MT).

        Parameters
        ----------
        self : ForceMT
            A ForceMT object
        output : Output
            an Output object (to update)
        axes_dict: {Data}
            Dict of axes used for force calculation

        Returns
        -------
        out_dict: dict
            Dict containing the following quantities:
                AGSF_r : ndarray
                    Airgap radial Maxwell stress (Nt,Na,Nz) [N/m²]
                AGSF_t : ndarray
                    Airgap tangential Maxwell stress (Nt,Na,Nz) [N/m²]
                AGSF_z : ndarray
                    Airgap axial Maxwell stress (Nt,Na,Nz) [N/m²]

        """

        # Init output dict
        out_dict = {}

        Rag = output.mag.Rag
        out_dict["Rag"] = Rag

        # Get time and angular axes
        Angle = axes_dict["angle"]
        Time = axes_dict["time"]

        # Import angular vector from Angle Data object
        is_periodicity_a, is_antiper_a = Angle.get_periodicity()

        if self.is_periodicity_a is not None:
            is_periodicity_a = self.is_periodicity_a

        angle = Angle.get_values(
            is_oneperiod=is_periodicity_a,
            is_antiperiod=is_antiper_a and is_periodicity_a,
        )

        if self.is_periodicity_t is not None:
            is_periodicity_t = self.is_periodicity_t

        # Import time vector from Time Data object
        is_periodicity_t, is_antiper_t = Time.get_periodicity()
        time = Time.get_values(
            is_oneperiod=is_periodicity_t,
            is_antiperiod=is_antiper_t and is_periodicity_t,
        )

        # Load magnetic flux
        if output.mag.B is None:
            raise FieldMissingError(
                "OutMag.B is None: the magnetic flux density is not computed"
            )
        Brphiz = output.mag.B.get_rphiz_along(
            "time=axis_data",
            "angle=axis_data",
            axis_data={"time": time, "angle": angle},
        )
        Br = Brphiz["radial"]

        # Magnetic void permeability
        mu_0 = 4 * np.pi * 1e-7

        # Get flux density component lists
        comp_list = list(output.mag.B.components.keys())

        # Calculate Maxwell Stress Tensor
        if "radial" in comp_list:
            if "tangential" not in comp_list and "axial" not in comp_list:
                out_dict["AGSF_r"] = -Br * Br / (2 * mu_0)

            elif "tangential" in comp_list:
                Bt = Brphiz["tangential"]
                out_dict["AGSF_t"] = -Br * Bt / mu_0

                if "axial" not in comp_list:
                    out_dict["AGSF_r"] = -(Br * Br - Bt * Bt) / (2 * mu_0)

                else:
                    Bz = Brphiz["axial"]
                    out_dict["AGSF_r"] = -(Br * Br - Bt * Bt - Bz * Bz) / (2 * mu_0)
                    out_dict["AGSF_z"] = -Br * Bz / mu_0

        return out_dict

    # Inlined from Methods.Simulation.ForceMT.comp_force_nodal
    def comp_force_nodal(self, output: Output):
        """Compute the nodal air-gap surface force based on Maxwell Tensor (MT).

        Parameters
        ----------
        self : ForceMT
            A ForceMT object

        output : Output
            an Output object (to update)
        """

        raise NotImplementedYetError("Nodal force not available yet for Maxwell tensor")
