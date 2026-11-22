# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModelJoule.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import numpy as np

from ...classes_common.errors import FieldMissingError
from ...classes_common.parents import container_or_parent
from .loss_model import LossModel

if TYPE_CHECKING:
    from ..mesh.mesh_solution import MeshSolution
    from ..output.output import Output
    from ..scidatatool.data import Data
    from .loss import Loss


@dataclass(eq=False)
class LossModelJoule(LossModel):
    """Joule loss model

    Attributes
    ----------
    type_skin_effect : int
        0 to ignore skin effect, 1 to consider it
        Default: 1
    """

    type_skin_effect: int = 1
    """0 to ignore skin effect, 1 to consider it"""

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Loss.LossModelJoule.comp_coeff
    def comp_coeff(
        self, T_op: float = 20, T_ref: float = 20, output: Output | None = None
    ) -> float:
        """Compute the skin effect factor on resistance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
        All parameters are defined p.270 / 271
        In this method, the returned value is the one from the reference divided by the frequency, as the effect of
        frequency will be taken into account in the coeff_dict

        Parameters
        ----------
        self : LossModelJoule
            a LossModelJoule object
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        ----------
        kr_skin : float
            skin effect coeff for resistance at given frequency and temperature
        """

        output = container_or_parent(self, output, "output", depth=3)
        if output is None:
            raise Exception("Cannot calculate core losses if simu is not in an Output")

        machine = output.simu.machine
        lamination = machine.stator if "stator" in self.group else machine.rotor
        conductor = lamination.winding.conductor

        # Compute slot average width
        slot = lamination.slot
        b = slot.comp_width()

        # Get number of turns in series per coil
        zt = lamination.winding.Ntcoil

        # check if wires are round or rectangular
        is_round_wire = conductor.is_round_wire()

        # conductor height
        hc0 = conductor.comp_height_wire()
        # conductor width
        bc0 = conductor.comp_width_wire()
        # Number of circumferential adjacent wires
        za = conductor.comp_nb_circumferential_wire()
        # Number of radial adjacent wires
        zp = conductor.comp_nb_radial_wire()
        # Equivalent height of conductor
        hc = zp * hc0

        # Electrical conductivity accounting for temperature increase
        sigma = conductor.cond_mat.elec.get_conductivity(T_op=T_op, T_ref=T_ref)

        # Magnetic permeability
        mu0 = 4 * np.pi * 1e-7
        if conductor.cond_mat.mag is None or conductor.cond_mat.mag.mur_lin is None:
            mur = 1
        else:
            mur = conductor.cond_mat.mag.mur_lin

        # reduced conductor height Eq(5.24) p.270 divided by the frequency + adding relative permeatibility
        ksi = hc * np.sqrt(np.pi * mu0 * mur * sigma * za * bc0 / b)

        if not isinstance(ksi, float):
            # Avoid numerical error with 0
            ksi[ksi == 0] = 1e-4

        # average resistance factor
        if is_round_wire:
            # Use round wire approximation Eq(5.30) p.271
            # --> kr_skin = 1 + 0.59 * ((zt ** 2 - 0.2) / 9) * ksi ** 4
            k = 0.59 * ((zt**2 - 0.2) / 9) * ksi**4
        else:
            # Use rectangular wire approximation Eq(5.29) p.271
            # --> kr_skin = 1 + (zt ** 2 - 0.2) / 9 * ksi ** 4
            k = (zt**2 - 0.2) / 9 * ksi**4

        return k

    # Inlined from Methods.Loss.LossModelJoule.comp_loss
    def comp_loss(
        self,
        meshsol: MeshSolution | None = None,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate joule losses in stator windings

        Parameters
        ----------
        self: LossModelJoule
            a LossModelJoule object
        meshsol : MeshSolution
            magnetic meshsolution (default: OutMag.meshsolution, only mesh and groups are used)
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pjoule_density : ndarray
            Joule loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """
        loss = container_or_parent(self, loss, "loss")
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise ValueError(
                "Cannot calculate joule losses if simu is not in an Output"
            )

        if output.elec is None:
            raise ValueError("Cannot calculate joule losses if OutElec is None")

        if loss.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate joule losses if OutMag is None")

        machine = output.simu.machine
        lam = machine.stator if "stator" in self.group else machine.rotor
        T_op = loss.Tsta if "stator" in self.group else loss.Trot

        OP = output.elec.OP
        felec = OP.get_felec()

        Rs = lam.comp_resistance_wind(T=T_op)
        qs = lam.winding.qs

        if self.type_skin_effect > 0:
            # Account for skin effect
            k = self.comp_coeff(
                output=output,
                T_op=T_op,
            )
        else:
            k = 0

        # Calculate overall joule losses
        # #TODO if the model is applied to the rotor of an SCIM, use the rotor current computed from the EEC.
        Id_Iq = OP.get_Id_Iq()
        coeff = qs * Rs * (Id_Iq["Id"] ** 2 + Id_Iq["Iq"] ** 2)
        Pjoule = coeff * (1 + k * felec**2)

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        Lst = lam.L1

        # Get surface elements for windings
        ms = meshsol if meshsol is not None else output.mag.meshsolution
        if ms is None:
            raise FieldMissingError(
                "OutMag.meshsolution is None: the magnetic model stored no mesh solution"
            )
        if ms.group is None:
            raise FieldMissingError(
                "MeshSolution.group is None: the mesh solution has no element groups"
            )
        Se = ms.mesh.get_element_area()[ms.group[self.group]]

        # Constant component and twice the electrical frequency have same joule density values
        freqs = np.array([felec])
        Pjoule_density = np.zeros((freqs.size, Se.size))
        Pjoule_density[0, :] = Pjoule / (per_a * Lst * np.sum(Se))

        A = coeff * k
        B = coeff
        self.coeff_dict = {"2": A, "0": B}

        return Pjoule_density, freqs

    # Inlined from Methods.Loss.LossModelJoule.comp_loss_freq
    def comp_loss_freq(
        self, loss: Loss | None = None, output: Output | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate joule losses in stator windings

        Parameters
        ----------
        self: LossModelJoule
            a LossModelJoule object
        loss : Loss, optional
            Loss object holding the model (default: the parent)
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Returns
        -------
        Pjoule_density : ndarray
            Joule loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """
        loss = container_or_parent(self, loss, "loss")
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise ValueError(
                "Cannot calculate joule losses if simu is not in an Output"
            )

        if output.elec is None:
            raise ValueError("Cannot calculate joule losses if OutElec is None")

        if loss.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate Joule losses if OutMag is None")

        # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
        meshsol, suffix = output.get_frame_meshsolution(self.group, "Joule losses")

        machine = output.simu.machine
        lam = machine.stator if "stator" in self.group else machine.rotor
        T_op = loss.Tsta if "stator" in self.group else loss.Trot
        Lst = lam.L1

        OP = output.elec.OP
        felec = OP.get_felec()

        Rs = lam.comp_resistance_wind(T=T_op)
        qs = lam.winding.qs

        if self.type_skin_effect > 0:
            # Account for skin effect
            k = self.comp_coeff(
                output=output,
                T_op=T_op,
            )
        else:
            k = 0

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get stator currents over frequency and phases
        Is = output.elec.get_Is(output=output)
        result = Is.get_along("freqs", "phase[]")
        Is_val = result[Is.symbol]
        freqs = result["freqs"]

        # Calculate Joule losses over time (Assuming fundamental skin correction factor the same for all harmonics)
        Pjoule = (
            Rs * (1 + k * felec**2) * np.sum(0.5 * np.abs(Is_val) ** 2, axis=1)
        )  # Sum over phases

        # Get surface and number of all elements
        Se_all = meshsol.mesh.get_element_area()

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = Se_all[Igrp]

        # Calculate uniform element density and sum over frequencies to get average loss density value per element
        Pjoule_density = np.zeros((1, Se.size))
        Pjoule_val = Pjoule.sum()
        Pjoule_density[0, :] = Pjoule_val / (per_a * Lst * Se.sum())

        # Store losses contribution for each frequency in dict
        Pjoule_dict = {self.group + " losses": Pjoule}

        # Get eddy-current proximity loss polynomial coefficient
        A = Pjoule_val / (1 + k * felec**2) * k
        B = Pjoule_val / (1 + k * felec**2)
        self.coeff_dict = {"2": A, "0": B}

        return Pjoule_density, Pjoule_dict, freqs

    # Inlined from Methods.Loss.LossModelJoule.comp_loss_time
    def comp_loss_time(
        self,
        axes_dict: dict[str, Data],
        is_mirror: bool,
        loss: Loss | None = None,
        output: Output | None = None,
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Calculate Joule losses in stator windings over time

        Parameters
        ----------
        self: LossModelJoule
            a LossModelJoule object
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
        Pjoule_density : ndarray
            Joule loss density function of time and elements [W/m3]
        Pjoule_dict: {ndarray}
            Dict containing the array of Joule losses over time
        """
        loss = container_or_parent(self, loss, "loss")
        output = container_or_parent(self, output, "output", depth=3)

        if output is None:
            raise ValueError(
                "Cannot calculate Joule losses if simu is not in an Output"
            )

        if output.elec is None:
            raise ValueError("Cannot calculate Joule losses if OutElec is None")

        if loss.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate Joule losses if OutMag is None")

        # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
        meshsol, suffix = output.get_frame_meshsolution(self.group, "Joule losses")

        machine = output.simu.machine
        lam = machine.stator if "stator" in self.group else machine.rotor
        T_op = loss.Tsta if "stator" in self.group else loss.Trot
        Lst = lam.L1
        Rs = lam.comp_resistance_wind(T=T_op)

        if self.type_skin_effect > 0:
            # Account for skin effect
            k = self.comp_coeff(
                output=output,
                T_op=T_op,
            )
        else:
            k = 0

        # Get mesh spatial symmetries (including (anti)-periodicities)
        per_a = meshsol.mesh.sym

        # Get stator currents over time and phases
        Is = output.elec.get_Is(output=output)
        if is_mirror:
            # Rebuild mesh quantities on time steps given by axes_dict
            time_val = axes_dict["time"].get_values(is_smallestperiod=True)
            Is_val = Is.get_along(
                "time=axis_data", "phase[]", axis_data={"time": time_val}
            )[Is.symbol]
        else:
            Is_val = Is.get_along("time[smallestperiod]", "phase[]")[Is.symbol]

        # Calculate Joule losses over time
        Pjoule = Rs * (1 + k) * np.sum(Is_val**2, axis=1)  # Sum over phases

        # Get surface and number of all elements
        Se_all = meshsol.mesh.get_element_area()

        # Get element indices associated to group
        Igrp = meshsol.group[self.group]

        # Get element surface associated to group
        Se = Se_all[Igrp]

        # Calculate uniform element density
        Pjoule_density = Pjoule[:, None] / (per_a * Lst * Se.sum())

        Pjoule_dict = {self.group + " losses": Pjoule}

        OP = output.elec.OP
        felec = OP.get_felec()
        Pjoule_val = Pjoule.mean()
        A = Pjoule_val / (1 + k * felec**2) * k
        B = Pjoule_val / (1 + k * felec**2)

        self.coeff_dict = {"2": A, "0": B}

        return Pjoule_density, Pjoule_dict
