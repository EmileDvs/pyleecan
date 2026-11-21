# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModelWindagePyrhonen.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import numpy as np

from ...classes_common.parents import container_or_parent
from .loss_model import LossModel

if TYPE_CHECKING:
    from ..mesh.mesh_solution import MeshSolution
    from ..output.output import Output
    from ..scidatatool.data import Data
    from .loss import Loss


@dataclass(eq=False)
class LossModelWindagePyrhonen(LossModel):
    """Windage loss model

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Loss.LossModelWindagePyrhonen.comp_loss
    def comp_loss(
        self,
        meshsol: MeshSolution | None = None,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate Windage losses
        Equation from "Design of Rotating Electrical Machines", Second Edition, Pyrhönen, Jokinen, Hrabovcovà p528

        Parameters
        ----------
        self: LossModelWindagePyrhonen
            a LossModelWindagePyrhonen object
        meshsol : MeshSolution
            magnetic meshsolution (default: OutMag.meshsolution, only mesh and groups are used)
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pjoule_density : ndarray
            loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """
        loss = container_or_parent(self, loss, "loss")
        output = container_or_parent(self, output, "output", depth=3)

        if output is None and self.parent.parent is None:
            raise ValueError("Cannot calculate losses if simu is not in an Output")
        else:
            pass

        if output.elec is None:
            raise ValueError("Cannot calculate losses if OutElec is None")

        if loss.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate losses if OutMag is None")

        machine = output.simu.machine
        L = machine.rotor.L1
        OP = output.elec.OP
        felec = OP.get_felec()

        Ploss = self.comp_loss_value(loss=loss, output=output)

        power = 3

        coeff = Ploss / felec**power

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        # Get surface elements for windings
        ms = meshsol if meshsol is not None else output.mag.meshsolution
        Se = ms.mesh.get_element_area()[ms.group["rotor core"]]

        # Constant component and twice the electrical frequency have same joule density values
        freqs = np.array([felec])
        P_density = np.zeros((freqs.size, Se.size))
        P_density[0, :] = Ploss / (per_a * L * np.sum(Se))

        self.coeff_dict = {str(power): coeff}

        return P_density, freqs

    # Inlined from Methods.Loss.LossModelWindagePyrhonen.comp_loss_freq
    def comp_loss_freq(
        self, loss: Loss | None = None, output: Output | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate Windage losses
        Equation from "Design of Rotating Electrical Machines", Second Edition, Pyrhönen, Jokinen, Hrabovcovà p528

        Parameters
        ----------
        self: LossModelWindagePyrhonen
            a LossModelWindagePyrhonen object
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pjoule_density : ndarray
            loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """
        loss = container_or_parent(self, loss, "loss")
        output = container_or_parent(self, output, "output", depth=3)

        if output is None and self.parent.parent is None:
            raise ValueError("Cannot calculate losses if simu is not in an Output")
        else:
            pass

        if output.elec is None:
            raise ValueError("Cannot calculate losses if OutElec is None")

        if loss.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate losses if OutMag is None")

        # Get magnetic meshsolution (airgap group contains elements of both stator and rotor frames)
        meshsol, _ = output.get_frame_meshsolution(self.group, "windage losses")

        # Get element indices associated to airgap group
        Igrp = list(meshsol.group[self.group])

        machine = output.simu.machine
        L = machine.rotor.L1
        OP = output.elec.OP
        felec = OP.get_felec()

        Ploss = self.comp_loss_value(loss=loss, output=output)

        power = 3

        coeff = Ploss / felec**power

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get surface elements for airgap
        Se = meshsol.mesh.get_element_area()[Igrp]

        # Compute the loss density for each element
        # When distributing windage losses on airgap elements, missing area of sliding band
        freqs = np.array([felec])
        Pwindage_density = np.zeros((freqs.size, Se.size))
        Pwindage_density[0, :] = Ploss / (per_a * L * np.sum(Se))

        Pwindage_dict = {"Airgap windage losses": np.array([Ploss])}

        self.coeff_dict = {str(power): coeff}

        return Pwindage_density, Pwindage_dict, freqs

    # Inlined from Methods.Loss.LossModelWindagePyrhonen.comp_loss_time
    def comp_loss_time(
        self,
        axes_dict: dict[str, Data],
        is_mirror: bool,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Calculate windage losses and assume they are constant over time

        Parameters
        ----------
        self: LossModelWindagePyrhonen
            a LossModelWindagePyrhonen object
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
        Pwindage_density : ndarray
            Windage loss density function of time and elements [W/m3]
        Pwindage_dict: {ndarray}
            Dict containing the array of windage losses over time
        """
        loss = container_or_parent(self, loss, "loss")
        output = container_or_parent(self, output, "output", depth=3)

        if output is None and self.parent.parent is None:
            raise ValueError(
                "Cannot calculate windage losses if simu is not in an Output"
            )
        else:
            pass

        if output.elec is None:
            raise ValueError("Cannot calculate windage losses if OutElec is None")

        if loss.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate windage losses if OutMag is None")

        # Get magnetic meshsolution (airgap group contains elements of both stator and rotor frames)
        meshsol, _ = output.get_frame_meshsolution(self.group, "windage losses")

        Nt = axes_dict["time"].get_length(is_smallestperiod=True)

        # Get element indices associated to airgap group
        Igrp = list(meshsol.group[self.group])

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        machine = output.simu.machine
        Lst = machine.stator.L1

        # Get airgap windage losses
        Ploss = self.comp_loss_value(loss=loss, output=output)

        # Assign same airgap windage losses at every time step
        Pwindage = Ploss * np.ones(Nt, dtype=float)

        # Get surface and number of all elements
        Se_all = meshsol.mesh.get_element_area()

        # Get element surface associated to group
        Se = Se_all[Igrp]

        # Compute the loss density for each element
        # When distributing windage losses on airgap elements, missing area of sliding band
        Pwindage_density = Pwindage[:, None] / (per_a * Lst * Se.sum())

        Pwindage_dict = {"Airgap windage losses": Pwindage}

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        # Save coefficients to rebuild losses for same (Id,Iq) but at a different speed
        self.coeff_dict = {"3": Ploss / felec**3}

        return Pwindage_density, Pwindage_dict

    # Inlined from Methods.Loss.LossModelWindagePyrhonen.comp_loss_value
    def comp_loss_value(
        self, loss: Loss | None = None, output: Output | None = None
    ) -> float:
        """Calculate Windage losses
        Equation from "Design of Rotating Electrical Machines", Second Edition, Pyrhönen, Jokinen, Hrabovcovà p528

        Parameters
        ----------
        self: LossModelWindagePyrhonen
            a LossModelWindagePyrhonen object
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Ploss : float
            overall windage loss value [W/m3]
        """
        loss = container_or_parent(self, loss, "loss")
        output = container_or_parent(self, output, "output", depth=3)

        if output is None and self.parent.parent is None:
            raise ValueError("Cannot calculate losses if simu is not in an Output")
        else:
            pass

        if output.elec is None:
            raise ValueError("Cannot calculate losses if OutElec is None")

        if loss.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate losses if OutMag is None")

        machine = output.simu.machine

        OP = output.elec.OP
        felec = OP.get_felec()

        Dr = machine.rotor.Rext * 2
        L = machine.rotor.L1
        p = machine.get_pole_pair_number()
        rho = 1.225  # air density
        k = 1
        omega = 2 * np.pi / p * felec
        delta = machine.comp_length_airgap_active()
        mu = 18.5e-6  # Dynamic viscosity of air
        # Couette Reynolds number
        Re_delta = rho * omega * Dr * delta / (2 * mu)
        # ------------------------------------------ Warning ---------------------------------------------
        # As C_M depends on Re_delta, which depends on the frequency, the coefficient that will be stored
        # in the coeff_dict below depends on frequency. So the coefficient may change with frequency and should be
        # computed again. But to build the coeff_dict, the assumption that C_M will not change must be made.
        # ------------------------------------------------------------------------------------------------
        if Re_delta < 64:
            C_M = 10 * (2 * delta / Dr) ** 0.3 / Re_delta
        elif Re_delta < 5e2:
            C_M = 2 * (2 * delta / Dr) ** 0.3 / Re_delta**0.6
        elif Re_delta < 1e4:
            C_M = 1.03 * (2 * delta / Dr) ** 0.3 / Re_delta**0.5
        else:
            C_M = 0.065 * (2 * delta / Dr) ** 0.3 / Re_delta**0.2

        P1 = 1 / 32 * k * C_M * np.pi * rho * omega**3 * Dr**4 * L

        Dri = machine.rotor.Rint

        # tip Reynolds number
        Re_r = rho * omega * Dr**2 / (4 * mu)

        if Re_r < 3e5:
            C_M = 3.87 / Re_r**0.5
        else:
            C_M = 0.146 / Re_r**0.2

        P2 = 1 / 64 * C_M * rho * omega**3 * (Dr**5 - Dri**5)

        Ploss = P1 + P2

        return Ploss
