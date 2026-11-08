# Experimental dataclass generated from Generator/ClassesRef/Output/OutMag.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions.labels import STATOR_LAB
from ..Functions.MeshSolution.get_area import get_area
from ..Functions.MeshSolution.get_indices_limited import get_indices_limited
from ..Functions.SciDataTool.derivation_integration import integrate
from ._pyleecan_class import PyleecanClass
from .data import Data
from .data_nd import DataND
from .data_time import DataTime
from .mesh_solution import MeshSolution
from .norm_ref import NormRef
from .out_internal import OutInternal
from .slice_model import SliceModel
from .vector_field import VectorField


@dataclass(eq=False)
class OutMag(PyleecanClass):
    """Gather the magnetic module outputs

    Attributes
    ----------
    axes_dict : {Data} or None
        Dict containing axes data used for Magnetics
        Default: None
    B : VectorField or None
        Airgap flux density VectorField object
        Unit: H; Default: None
    Tem : DataND or None
        Electromagnetic torque DataTime object
        Unit: N.m; Default: None
    Tem_av : float or None
        Average Electromagnetic torque
        Unit: N.m; Default: None
    Tem_rip_norm : float or None
        Peak to Peak Torque ripple normalized according to average torque (None if average torque=0)
        Default: None
    Tem_rip_pp : float or None
        Peak to Peak Torque ripple
        Unit: N.m; Default: None
    Phi_wind_stator : DataND or None
        Stator winding flux DataTime object
        Unit: Wb; Default: None
    Phi_wind : {DataND} or None
        Dict of lamination winding fluxlinkage DataTime objects
        Unit: Wb; Default: None
    emf : DataND or None
        Electromotive force DataTime object
        Unit: V; Default: None
    meshsolution : MeshSolution or None
        FEA software mesh and solution
        Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Magnetics"
    internal : OutInternal or None
        OutInternal object containg outputs related to a specific model
        Default: None
    Rag : float or None
        Radius value for air-gap computation
        Default: None
    Pem_av : float or None
        Average Electromagnetic power
        Unit: W; Default: None
    Slice : SliceModel or None
        Slice model to account for skew
        Default: None
    Tem_slice : DataND or None
        Electromagnetic torque DataTime object including torque per slice
        Unit: N; Default: None
    Phi_wind_slice : {DataND} or None
        Dict of lamination winding fluxlinkage DataTime objects per slice
        Unit: Wb/m; Default: None
    Tem_norm : float
        Torque normalization
        Unit: N.m; Default: 0.001
    """

    axes_dict: dict[str, Data] | None = None
    """Dict containing axes data used for Magnetics"""
    B: VectorField | None = None
    """Airgap flux density VectorField object"""
    Tem: DataND | None = None
    """Electromagnetic torque DataTime object"""
    Tem_av: float | None = None
    """Average Electromagnetic torque"""
    Tem_rip_norm: float | None = None
    """Peak to Peak Torque ripple normalized according to average torque (None if average torque=0)"""
    Tem_rip_pp: float | None = None
    """Peak to Peak Torque ripple"""
    Phi_wind_stator: DataND | None = None
    """Stator winding flux DataTime object"""
    Phi_wind: dict[str, DataND] | None = None
    """Dict of lamination winding fluxlinkage DataTime objects"""
    emf: DataND | None = None
    """Electromotive force DataTime object"""
    meshsolution: MeshSolution | None = None
    """FEA software mesh and solution"""
    logger_name: str = "Pyleecan.Magnetics"
    """Name of the logger to use"""
    internal: OutInternal | None = None
    """OutInternal object containg outputs related to a specific model"""
    Rag: float | None = None
    """Radius value for air-gap computation"""
    Pem_av: float | None = None
    """Average Electromagnetic power"""
    Slice: SliceModel | None = None
    """Slice model to account for skew"""
    Tem_slice: DataND | None = None
    """Electromagnetic torque DataTime object including torque per slice"""
    Phi_wind_slice: dict[str, DataND] | None = None
    """Dict of lamination winding fluxlinkage DataTime objects per slice"""
    Tem_norm: float = 0.001
    """Torque normalization"""

    # Inlined from Methods.Output.OutMag.clean
    def clean(self, clean_level=1):
        """Clean Magnetics standard outputs depending on cleaning level

        Parameters
        ----------
        self : OutMag
            the OutMag object to update
        clean_level : int
            Value to indicate which fields to clean in OutMag (default=1/min=0/max=4/5=LUT)

        """

        # if clean_level = 0:
        # keep all outputs

        if clean_level == 5:  # LUT
            # Keep B, Tem_slice, Phi_wind_slice
            self.meshsolution = None
            self.Tem = None
            self.Phi_wind = None
            self.Phi_wind_stator = None
            self.emf = None
            self.internal = None
            self.axes_dict = None
            return

        if clean_level > 0:
            # clean meshsolution
            self.meshsolution = None

        if clean_level > 1:
            # clean airgap flux density
            self.B = None

        if clean_level > 2:
            # clean Tem/Phi_wind quantities
            self.Tem = None
            self.Tem_slice = None
            self.Phi_wind_slice = None
            self.Phi_wind_stator = None
            self.Phi_wind = None
            self.emf = None

        if clean_level > 3:
            # clean all internal outputs
            self.internal = None
            self.axes_dict = None

        else:
            # clean internal depending on log_level
            self.internal.clean(clean_level)

    # Inlined from Methods.Output.OutMag.comp_emf
    def comp_emf(self):
        """Compute the Electromotive force [V]

        Parameters
        ----------
        self : OutMag
            an OutMag object

        """

        # Get stator winding flux
        Phi_wind = self.Phi_wind[self.parent.simu.machine.stator.get_label()]

        EMF = Phi_wind.get_data_along("time=derivate", "phase")

        EMF.name = "Stator Winding Electromotive Force"
        EMF.unit = "V"
        EMF.symbol = "EMF"

        self.emf = EMF

    # Inlined from Methods.Output.OutMag.comp_power
    def comp_power(self):
        """Compute the Ouput power

        Parameters
        ----------
        self : OutMag
            An OutMag object
        """

        if (
            self.parent is not None
            and self.parent.elec is not None
            and self.parent.elec.OP.get_N0() is not None
            and self.Tem_av is not None
        ):
            self.Pem_av = 2 * np.pi * self.parent.elec.OP.get_N0() / 60 * self.Tem_av
        else:
            self.Pem_av = None

    # Inlined from Methods.Output.OutMag.comp_torque_MT
    def comp_torque_MT(self):
        """Compute the rotor electromagnetic torque from Maxwell Stress Tensor.

        Parameters
        ----------
        self : OutMag
            an OutMag object

        Returns
        -------
        Tem_slice : ndarray
            Rotor electromagnetic torque per slice [N]

        """
        Tem_slice = None
        B = self.B

        if (
            B is not None
            and "radial" in B.components.keys()
            and "tangential" in B.components.keys()
        ):
            machine = self.parent.simu.machine

            # Load airgap Maxwell Stress Tensor
            Brphiz = B.get_rphiz_along(
                "time[smallestperiod]",
                "angle[smallestperiod]",
                "z[smallestpattern]",
                is_squeeze=False,
            )

            Br = Brphiz["radial"]
            Bt = Brphiz["tangential"]

            if self.Rag is None:
                R = machine.comp_Rgap_mec()
            else:
                R = self.Rag

            # Magnetic void permeability
            mu_0 = 4 * np.pi * 1e-7

            # Integrate over angle to get the electromagnetic torque per slice
            Nper, _ = B.get_axes()[1].get_periodicity()
            Tem_slice = (
                R**2
                / mu_0
                * integrate(
                    values=Br * Bt,
                    ax_val=Brphiz["angle"],
                    index=1,
                    Nper=Nper,
                    is_aper=False,
                    is_phys=True,
                )[:, 0, :]
            )

            if Tem_slice.ndim == 1:
                Tem_slice = Tem_slice[:, None]

        return Tem_slice

    # Inlined from Methods.Output.OutMag.get_demag
    def get_demag(self, Hmax, group_name=None):
        """Get the surface area of the magnets that exceed a given field strenght H

        Parameters
        ----------
        Hmax : float
            demagnetization field strenght

        group_name : str
            optional name of the group, default group is 'rotor magnets'

        Return
        ------
        area : float
            surface area that exceed the max. field strength

        area_ref : float
            total magnets surface area as a reference

        indices : list
            list of elements indices that exceed the max. field strength

        """
        if group_name is None:
            group_name = "rotor magnets"
        if group_name in self.meshsolution.group.keys():
            inds = get_indices_limited(
                self.meshsolution, label="H", group_names=group_name, max_value=Hmax
            )

            area_ref = get_area(self.meshsolution, group_names=group_name)
            area = get_area(self.meshsolution, group_names=group_name, indices=inds)
        else:
            area, area_ref, inds = None, None, []

        return area, area_ref, inds

    # Inlined from Methods.Output.OutMag.store
    def store(self, out_dict, axes_dict):
        """Store the standard outputs of Magnetics that are temporarily in out_dict as arrays into OutMag as Data object

        Parameters
        ----------
        self : OutMag
            the OutMag object to update
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in comp_flux_airgap
        axes_dict: {Data}
            Dict of axes used for magnetic calculation

        """

        # Store axes dict
        self.axes_dict = axes_dict

        # Get time/frequency axis
        if "freqs" in axes_dict:
            ax1 = axes_dict["freqs"]
            if "freqs_Tem" in axes_dict:
                ax1_Tem = axes_dict["freqs_Tem"]
            else:
                ax1_Tem = None
        else:
            ax1 = axes_dict["time"]
            if "time_Tem" in axes_dict:
                ax1_Tem = axes_dict["time_Tem"]
            else:
                ax1_Tem = None

        # Get angle/wavenumber axis
        if "wavenumber" in axes_dict:
            ax2 = axes_dict["wavenumber"]
        else:
            ax2 = axes_dict["angle"]

        # Store airgap flux as VectorField object
        # Axes for each airgap flux component
        axis_list = [ax1, ax2, axes_dict["z"]]

        # Create VectorField with empty components
        if "B_{rad}" in out_dict or "B_{circ}" in out_dict or "B_{ax}" in out_dict:
            self.B = VectorField(
                name="Air gap flux density",
                symbol="B",
            )

        # Radial flux component
        if "B_{rad}" in out_dict:
            self.B.components["radial"] = DataTime(
                name="Air gap radial flux density",
                unit="T",
                symbol="B_{rad}",
                axes=axis_list,
                values=out_dict.pop("B_{rad}"),
            )
        # Tangential flux component
        if "B_{circ}" in out_dict:
            self.B.components["tangential"] = DataTime(
                name="Air gap circumferential flux density",
                unit="T",
                symbol="B_{circ}",
                axes=axis_list,
                values=out_dict.pop("B_{circ}"),
            )
        # Axial flux component
        if "B_{ax}" in out_dict:
            self.B.components["axial"] = DataTime(
                name="Air gap axial flux density",
                unit="T",
                symbol="B_{ax}",
                axes=axis_list,
                values=out_dict.pop("B_{ax}"),
            )

        # Store electromagnetic torque over time, and global values: average, peak to peak and ripple
        if (
            "Tem" in out_dict
            or (
                self.parent is not None
                and self.parent.simu is not None
                and self.parent.simu.machine is not None
                and self.B is not None
                and "radial" in self.B.components.keys()
                and "tangential" in self.B.components.keys()
            )
            and ax1_Tem is not None
        ):
            if "Tem" in out_dict:
                Tem_slice = out_dict.pop("Tem")
            else:
                Tem_slice = self.comp_torque_MT()

            # Store electromagnetic torque per slice (in Newton)
            self.Tem_slice = DataTime(
                name="Electromagnetic torque (axial density)",
                unit="N",
                symbol="T_{em}",
                axes=[ax1_Tem, axes_dict["z"]],
                values=Tem_slice,
                normalizations={"ref": NormRef(ref=self.Tem_norm)},
            )

            # Integrate over slice axis to get overall torque (in Newton meter)
            self.Tem = self.Tem_slice.get_data_along(
                "time[smallestperiod]", "z=integrate"
            )
            self.Tem.name = "Electromagnetic torque"

            # Calculate average torque in Nm
            self.Tem_av = np.mean(self.Tem.values)
            # self.Tem_av = float(self.Tem.get_along("time=mean")[self.Tem.symbol])

            # Calculate peak to peak torque in absolute value [N.m]
            self.Tem_rip_pp = abs(np.max(self.Tem.values) - np.min(self.Tem.values))

            # Calculate torque ripple in percentage [%]
            if self.Tem_av != 0:
                self.Tem_rip_norm = self.Tem_rip_pp / self.Tem_av
            else:
                self.Tem_rip_norm = None

        # Store list of winding flux linkage, stator winding fluxlinkage
        # and calculate electromotive force
        if "Phi_wind" in out_dict:
            machine = self.parent.simu.machine
            self.Phi_wind_slice = {}
            self.Phi_wind = {}
            for key, phi_wind in out_dict["Phi_wind"].items():
                # Store stator winding flux
                lam = machine.get_lam_by_label(key)

                Phase = self.parent.elec.axes_dict["phase_" + key]
                prefix = "Stator" if lam.is_stator else "Rotor"

                # Store winding flux linkage per phase and per slice (in Weber per meter)
                self.Phi_wind_slice[key] = DataTime(
                    name=prefix + " Winding Flux (axial density)",
                    unit="Wb/m",
                    symbol="Phi_{wind}",
                    axes=[ax1, Phase, axes_dict["z"]],
                    values=phi_wind,
                )
                # Integrate over slice axis to get overall winding flux linkage (in Weber)
                self.Phi_wind[key] = self.Phi_wind_slice[key].get_data_along(
                    "time[smallestperiod]", "phase", "z=integrate"
                )
                self.Phi_wind[key].name = prefix + " Winding Flux"

            # Particular case: Phi_wind for stator-0 has its own property
            if STATOR_LAB + "-0" in out_dict["Phi_wind"].keys():
                # TODO fix for multi stator/lamination
                self.Phi_wind_stator = self.Phi_wind[STATOR_LAB + "-0"]

            # Electromotive force computation
            # self.comp_emf()

        # Store MeshSolution object
        if "meshsolution" in out_dict:
            self.meshsolution = out_dict.pop("meshsolution")

        if "Rag" in out_dict:
            self.Rag = out_dict.pop("Rag")
