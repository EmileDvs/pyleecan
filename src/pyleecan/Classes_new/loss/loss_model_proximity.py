# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModelProximity.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import numpy as np

from ...classes_common.errors import FieldMissingError
from ...classes_common.parents import container_or_parent
from .loss_model import LossModel

if TYPE_CHECKING:
    from ..mesh.mesh_solution import MeshSolution
    from ..output.output import Output
    from ..scidatatool.data import Data
    from ..simulation.simulation import Simulation
    from .loss import Loss


@dataclass(eq=False)
class LossModelProximity(LossModel):
    """Proximity Loss Model Class

    Attributes
    ----------
    k_p : float or None
        Proximity loss coefficient
        Unit: W/kg; Default: None
    """

    k_p: float | None = field(default=None, metadata={"unit": "W/kg"})
    """Proximity loss coefficient"""

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Loss.LossModelProximity.comp_coeff
    def comp_coeff(
        self, loss: Loss | None = None, simu: Simulation | None = None
    ) -> None:
        """Compute the Proximity loss coefficient [W/kg]

        Parameters
        ----------
        self : LossModelProximity
            a LossModelProximity object
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        simu : Simulation, optional
            Simulation of the loss model (default: the parent of the Loss object)
        """
        loss = container_or_parent(self, loss, "loss")
        simu = container_or_parent(self, simu, "simu", depth=2)
        T_op = loss.Tsta
        winding = simu.machine.stator.winding
        sigma = winding.conductor.cond_mat.elec.get_conductivity(T_op=T_op)
        d = winding.conductor.Wwire
        kf = simu.machine.stator.comp_fill_factor()

        # Proximity loss coefficient [W/kg]
        self.k_p = kf * np.pi**2 / 8 * sigma * d**2

    # Inlined from Methods.Loss.LossModelProximity.comp_loss
    def comp_loss(
        self,
        meshsol: MeshSolution | None = None,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate proximity loss density assuming it is given by:

            P = k_p * f^2 * B^2

        Parameters
        ----------
        self: LossModelProximity
            a LossModelProximity object
        meshsol : MeshSolution
            magnetic meshsolution with stator and rotor solutions merged (default: OutMag.get_meshsolution())
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pcore_density : ndarray
            Core loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise Exception("Cannot calculate core losses if simu is not in an Output")

        machine = output.simu.machine

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        lamination = machine.stator if "stator" in self.group else machine.rotor
        Lst = lamination.L1

        # Compute the Proximity loss coefficient (if not enforced)
        if self.k_p is None:
            self.comp_coeff(loss=loss, simu=output.simu)
        k_p = self.k_p

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        if output.mag is None:
            raise Exception("Cannot calculate core losses if OutMag is None")

        if meshsol is None:
            if output.mag.meshsolution is None:
                raise Exception(
                    "Cannot calculate core losses if OutMag.meshsolution is None"
                )
            # Merge stator and rotor frame solutions on the same Time axis
            meshsol = output.mag.get_meshsolution()

        if meshsol.group is None:
            raise FieldMissingError(
                "MeshSolution.group is None: the mesh solution has no element groups"
            )
        group_list = list(meshsol.group.keys())

        if self.group not in group_list:
            raise Exception("Cannot calculate core losses for group=" + self.group)

        try:
            solution_B = meshsol["B"]
        except ValueError:
            raise ValueError("Cannot calculate core losses if B is not in meshsolution")

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = meshsol.mesh.get_element_area()[Igrp]

        Bvect = solution_B.field
        axes_list = Bvect.get_axes()
        Time_orig = axes_list[0]
        Time = Time_orig.copy()

        # Check Time axis periodicity in function of group
        is_change_Time = False
        if "rotor" in self.group:
            if "antiperiod" in Time_orig.symmetries:
                Time.symmetries = {"period": Time_orig.symmetries["antiperiod"]}
                is_change_Time = True
        if is_change_Time:
            for comp in Bvect.components.values():
                comp.axes[0] = Time

        # Compute magnetic flux density FFT
        Bfft = Bvect.get_xyz_along("freqs", "indice=" + str(Igrp), "z=mean")
        freqs = Bfft["freqs"]
        Bfft_magnitude = np.sqrt(
            np.abs(Bfft["comp_x"]) ** 2 + np.abs(Bfft["comp_y"]) ** 2
        )

        # Proximity loss density for each frequency and element
        Pcore_density = k_p * freqs[:, None] ** 2 * Bfft_magnitude**2

        if is_change_Time:
            # Change periodicity back to original periodicity
            for comp in Bvect.components.values():
                comp.axes[0] = Time_orig

        # Get frequency orders
        n = freqs / felec

        # Integrate loss density over group volume to get polynomial coefficients
        coeff = Lst * per_a * np.matmul(Bfft_magnitude**2, Se)
        A = np.sum(k_p * coeff * n**2)
        self.coeff_dict = {"2": A}

        return Pcore_density, freqs

    # Inlined from Methods.Loss.LossModelProximity.comp_loss_freq
    def comp_loss_freq(
        self, loss: Loss | None = None, output: Output | None = None
    ) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
        """Calculate proximity loss density assuming it is given by an eddy-current loss model depending on frequency:

            P = k_p * f^2 * B^2

        Parameters
        ----------
        self: LossModelProximity
            a LossModelProximity object
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pprox_density : ndarray
            Average proximity loss density (frequency=0Hz) for all elements [W/m3]
        Pprox_dict: {ndarray}
            Dict containing the array of proximity losses by contribution and for all frequencies in magnetic flux density [W]
        freqs: ndarray
            frequency vector of magnetic flux density harmonics [Hz]
        """
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise ValueError(
                "Cannot calculate proximity losses if simu is not in an Output"
            )
        else:
            pass

        machine = output.simu.machine

        lamination = machine.stator if "stator" in self.group else machine.rotor
        Lst = lamination.L1

        # Compute the Proximity loss coefficient (if not enforced)
        if self.k_p is None:
            self.comp_coeff(loss=loss, simu=output.simu)
        k_p = self.k_p

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
        meshsol, suffix = output.get_frame_meshsolution(self.group, "proximity losses")

        if "B" + suffix in meshsol:
            Bvect = meshsol["B" + suffix].field
        else:
            raise ValueError(
                "Cannot calculate proximity losses if B is not in meshsolution"
            )

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = meshsol.mesh.get_element_area()[Igrp]

        # Compute magnetic flux density FFT
        Bfft = Bvect.get_xyz_along("freqs", "indice=" + str(Igrp), "z=mean")
        freqs = Bfft["freqs"]
        Bfft_square = np.abs(Bfft["comp_x"]) ** 2 + np.abs(Bfft["comp_y"]) ** 2

        # Compute the loss density for each frequency and element
        Pprox_density = k_p * freqs[:, None] ** 2 * Bfft_square

        # Integrate volumic density over core volume to get loss value
        Pprox = Lst * per_a * np.matmul(Pprox_density, Se)

        # Sum over frequencies to get average loss density value per element
        Pprox_density = np.sum(Pprox_density, axis=0, keepdims=True)

        # Store losses contribution for each frequency in dict
        Pprox_dict = {self.group + " losses": Pprox}

        # Get eddy-current proximity loss polynomial coefficient
        A = np.sum(Pprox) / felec**2
        self.coeff_dict = {"2.0": A}

        return Pprox_density, Pprox_dict, freqs

    # Inlined from Methods.Loss.LossModelProximity.comp_loss_time
    def comp_loss_time(
        self,
        axes_dict: dict[str, Data],
        is_mirror: bool,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Calculate proximity loss density over time

            Pprox_density = k_p * (dB/dt)^2

        Parameters
        ----------
        self: LossModelProximity
            a LossModelProximity object
        axes_dict: {Data}
            Dict containing Time (including (anti-)periodicties) and Indices axes used in any Loss module
        is_mirror : bool
            True to mirror magnetic mesh quantities calculate in stator and rotor frames to get the same Time axis
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pprox_density : ndarray
            Proximity loss density function of time and elements [W/m3]
        Pprox_dict: {ndarray}
            Dict containing the array of proximity losses over time
        """
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise ValueError(
                "Cannot calculate proximity losses if simu is not in an Output"
            )
        else:
            pass

        machine = output.simu.machine

        lamination = machine.stator if "stator" in self.group else machine.rotor
        Lst = lamination.L1

        # Compute the Proximity loss coefficient (if not enforced)
        if self.k_p is None:
            self.comp_coeff(loss=loss, simu=output.simu)
        k_p = self.k_p

        # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
        meshsol, suffix = output.get_frame_meshsolution(self.group, "proximity losses")

        if "B" + suffix in meshsol:
            Bvect = meshsol["B" + suffix].field
        else:
            raise ValueError(
                "Cannot calculate proximity losses if B is not in meshsolution"
            )

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get surface and number of all elements
        Se_all = meshsol.mesh.get_element_area()

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = Se_all[Igrp]

        # Compute magnetic flux density derivative over time
        dB_dt_v = Bvect.get_vectorfield_along("time=derivate", "indice", "z")

        if is_mirror:
            # Rebuild mesh quantities on time steps given by axes_dict
            time_val = axes_dict["time"].get_values(is_smallestperiod=True)
            dB_dt = dB_dt_v.get_xyz_along(
                "time=axis_data",
                "indice=" + str(Igrp),
                "z=mean",
                axis_data={"time": time_val},
            )
        else:
            dB_dt = dB_dt_v.get_xyz_along(
                "time[smallestperiod]", "indice=" + str(Igrp), "z=mean"
            )

        # Compute the loss density for each element function of time
        Pprox_density = (
            k_p / (2 * np.pi**2) * (dB_dt["comp_x"] ** 2 + dB_dt["comp_y"] ** 2)
        )

        # Integrate volumic density over core volume
        Pprox = Lst * per_a * np.matmul(Pprox_density, Se)

        Pprox_dict = {self.group + " losses": Pprox}

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        # Save coefficients to rebuild losses for same (Id,Iq) but at a different speed
        A = Pprox.mean() / felec**2
        self.coeff_dict = {"2": A}

        return Pprox_density, Pprox_dict
