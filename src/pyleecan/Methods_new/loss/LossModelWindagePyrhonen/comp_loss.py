from ....classes_common.errors import FieldMissingError
from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.loss.loss import Loss
    from ....Classes_new.mesh.mesh_solution import MeshSolution
    from ....Classes_new.output.output import Output



def comp_loss(self, meshsol: MeshSolution | None = None, loss: Loss | None = None, output: Output | None = None) -> tuple[np.ndarray, np.ndarray]:
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

    if output is None:
        raise ValueError("Cannot calculate losses if simu is not in an Output")

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
    if ms is None:
        raise FieldMissingError("OutMag.meshsolution is None: the magnetic model stored no mesh solution")
    if ms.group is None:
        raise FieldMissingError("MeshSolution.group is None: the mesh solution has no element groups")
    Se = ms.mesh.get_element_area()[ms.group["rotor core"]]

    # Constant component and twice the electrical frequency have same joule density values
    freqs = np.array([felec])
    P_density = np.zeros((freqs.size, Se.size))
    P_density[0, :] = Ploss / (per_a * L * np.sum(Se))

    self.coeff_dict = {str(power): coeff}

    return P_density, freqs
