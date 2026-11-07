# Experimental dataclass generated from Generator/ClassesRef/Simulation/Force.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._pyleecan_class import PyleecanClass
from .data_1d import Data1D
from .data_freq import DataFreq
from .simulation import Simulation
from .vector_field import VectorField


@dataclass(eq=False)
class Force(PyleecanClass):
    """Forces module abstract object

    Attributes
    ----------
    is_periodicity_t : bool or None
        True to compute only on one time periodicity (use periodicities defined in axes_dict[time]). If None, automatically calculated based on Magnetics periodicities.
        Default: None
    is_periodicity_a : bool or None
        True to compute only on one angle periodicity (use periodicities defined in axes_dict[angle]). If None, automatically calculated based on Magnetics periodicities.
        Default: None
    is_agsf_transfer : bool
        True to compute the AGSF transfer from air-gap to stator bore radius.
        Default: False
    max_wavenumber_transfer : int or None
        Maximum value to apply agsf transfer (to be used with FEA to avoid numerical noise amplification)
        Default: None
    Rsbo_enforced_transfer : float or None
        To enforce the value of the radius for AGSF transfer
        Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Force"
    """

    is_periodicity_t: bool | None = None
    """True to compute only on one time periodicity (use periodicities defined in axes_dict[time]). If None, automatically calculated based on Magnetics periodicities."""
    is_periodicity_a: bool | None = None
    """True to compute only on one angle periodicity (use periodicities defined in axes_dict[angle]). If None, automatically calculated based on Magnetics periodicities."""
    is_agsf_transfer: bool = False
    """True to compute the AGSF transfer from air-gap to stator bore radius."""
    max_wavenumber_transfer: int | None = None
    """Maximum value to apply agsf transfer (to be used with FEA to avoid numerical noise amplification)"""
    Rsbo_enforced_transfer: float | None = None
    """To enforce the value of the radius for AGSF transfer"""
    logger_name: str = "Pyleecan.Force"
    """Name of the logger to use"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Simulation,)):
            raise TypeError(
                "Force parent must be an instance of Simulation, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Simulation.Force.comp_AGSF_transfer
    def comp_AGSF_transfer(self, output, rnoise=None):
        """Method to compute Air-Gap Surface Force transfer from middle air-gap
        radius to stator bore radius.

        From publication:
            PILE, Raphaël, LE BESNERAIS, Jean, PARENT, Guillaume, et al. Analytical
            study of air-gap surface force–application to electrical machines. Open
            Physics, 2020, vol. 18, no 1, p. 658-673.
            https://www.degruyter.com/view/journals/phys/18/1/article-p658.xml

        Parameters
        ----------
        self: Force
            a Force object
        output : Output
            an Output object

        """

        # Inputs
        Rag = output.force.Rag

        if self.Rsbo_enforced_transfer is None:
            Rsbo = output.simu.machine.stator.Rint
        else:
            Rsbo = self.Rsbo_enforced_transfer

        AGSF = output.force.AGSF

        arg_list = ["freqs", "wavenumber"]
        result_freq = AGSF.get_rphiz_along(*arg_list)
        Prad_wr = result_freq["radial"]
        Ptan_wr = result_freq["tangential"]
        wavenumber = result_freq["wavenumber"]
        freqs = result_freq["freqs"]
        Nf = len(freqs)

        Ratio = Rag / Rsbo

        # Transfer coefficients Eq. (46)
        Sn = (
            (Ratio**2)
            * (np.power(Ratio, wavenumber) + np.power(Ratio, -wavenumber))
            / 2
        )
        Cn = (
            (Ratio**2)
            * (np.power(Ratio, wavenumber) - np.power(Ratio, -wavenumber))
            / 2
        )

        # Noise filtering (useful with magnetic FEA)
        if rnoise is not None:
            Inoise = np.where(abs(wavenumber) > rnoise)[0]
            Sn[Inoise] = 1
            Cn[Inoise] = 0

        XSn = np.repeat(Sn[..., np.newaxis], Nf, axis=1).transpose()
        XCn = np.repeat(Cn[..., np.newaxis], Nf, axis=1).transpose()

        # Transfer law Eq. (45)
        Prad_wr_TR = np.multiply(XSn, Prad_wr) + 1j * np.multiply(XCn, Ptan_wr)
        Ptan_wr_TR = np.multiply(XSn, Ptan_wr) - 1j * np.multiply(XCn, Prad_wr)

        # Save results as Data objects
        Datafreqs = Data1D(name="freqs", values=freqs)
        Datawavenumbers = Data1D(name="wavenumber", values=wavenumber)

        axes_list = [Datafreqs, Datawavenumbers]

        AGSF_TR = VectorField(
            name="Air gap Surface Force",
            symbol="AGSF",
        )

        AGSF_TR.components["radial"] = DataFreq(
            name="Radial AGSF",
            unit="N/m^2",
            symbol="AGSF_r",
            axes=axes_list,
            values=Prad_wr_TR,
        )

        AGSF_TR.components["tangential"] = DataFreq(
            name="Tangential AGSF",
            unit="N/m^2",
            symbol="AGSF_t",
            axes=axes_list,
            values=Ptan_wr_TR,
        )

        # Replace original AGSF
        output.force.AGSF = AGSF_TR
        output.force.Rag = Rsbo

    # Inlined from Methods.Simulation.Force.comp_axes
    def comp_axes(self, output):
        """Compute the axes required in any Force module

        Parameters
        ----------
        self : Force
            a Force object
        output : Output
            an Output object (to update)

        Returns
        -------
        axes_dict: {Data}
            Dict containing Time and Angle axes including (anti-)periodicties used in any Force module
        """

        # Get geometry output
        outgeo = output.geo

        # Get axis dict from OutMag
        axes_dict_mag = output.mag.axes_dict

        # Add periodicities to time and angle axes
        axes_dict = output.simu.input.comp_axes(
            axes_list=["time", "angle"],
            axes_dict_in=axes_dict_mag,
            is_periodicity_a=self.is_periodicity_a,
            is_periodicity_t=self.is_periodicity_t,
        )

        # Remove time anti-periodicity if any
        if "antiperiod" in axes_dict["time"].symmetries:
            axes_dict["time"].symmetries["period"] = axes_dict["time"].symmetries.pop(
                "antiperiod"
            )

        # Check Time periodicities regarding Force model input
        per_t0, is_antiper_t0 = axes_dict["time"].get_periodicity()
        is_periodicity_t0 = per_t0 > 1 or is_antiper_t0
        if self.is_periodicity_t is None:
            self.is_periodicity_t = is_periodicity_t0
        if not is_periodicity_t0 and self.is_periodicity_t:
            # Remove time periodicity in Force model
            self.is_periodicity_t = False
            Nt_tot = axes_dict["time"].get_length(is_oneperiod=False)
            self.get_logger().warning(
                "In Force model, Nt_tot="
                + str(Nt_tot)
                + " is not divisible by the machine time periodicity ("
                + str(outgeo.per_t_S)
                + "). Time periodicity removed"
            )

        # Remove angular anti-periodicity if any
        if "antiperiod" in axes_dict["angle"].symmetries:
            axes_dict["angle"].symmetries["period"] = axes_dict["angle"].symmetries.pop(
                "antiperiod"
            )

        # Check Angle periodicities regarding Force model input
        per_a0, is_antiper_a0 = axes_dict["angle"].get_periodicity()
        is_periodicity_a0 = per_a0 > 1 or is_antiper_a0
        if self.is_periodicity_a is None:
            self.is_periodicity_a = is_periodicity_a0
        if not is_periodicity_a0 and self.is_periodicity_a:
            # Remove time periodicity in Magnetic model
            self.is_periodicity_a = False
            Na_tot = axes_dict["angle"].get_length(is_oneperiod=False)
            self.get_logger().warning(
                "In Force model, Na_tot="
                + str(Na_tot)
                + " is not divisible by the machine angular periodicity ("
                + str(outgeo.per_a)
                + "). Angular periodicity removed"
            )

        return axes_dict

    # Inlined from Methods.Simulation.Force.run
    def run(self):
        """Run the Force module"""
        if self.parent is None:
            raise InputError(
                "ERROR: The Force object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError(
                "ERROR: The Force object must be in an Output object to run"
            )

        self.get_logger().info("Starting Force module")

        output = self.parent.parent

        # Compute and store time and angle axes from previous output
        # and returns additional axes in axes_dict
        axes_dict = self.comp_axes(output)

        # Compute the magnetic force according to the Force model
        out_dict = self.comp_force(output, axes_dict)

        # Store force quantities contained in out_dict in OutForce, as Data object if necessary
        output.force.store(out_dict, axes_dict)

        # Compute the air-gap surface force transfer if required
        if self.is_agsf_transfer:
            self.comp_AGSF_transfer(output, self.max_wavenumber_transfer)

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""


InputError = Force.InputError
