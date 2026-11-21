import numpy as np

from ....Classes_new.slot.hole_m_50 import HoleM50
from ....Classes_new.slot.hole_m_51 import HoleM51
from ....Classes_new.slot.hole_m_52 import HoleM52
from ....Classes_new.slot.hole_m_53 import HoleM53
from ....Classes_new.slot.hole_m_57 import HoleM57
from ....Classes_new.slot.hole_m_58 import HoleM58
from ....Classes_new.machine.lam_hole import LamHole
from ....Classes_new.machine.lam_slot_mag import LamSlotMag
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def comp_kseg(self, machine: Machine) -> float:
    """Calculate segmentation coefficient from:
    "Effect of Eddy-Current Loss Reduction by Magnet Segmentation in Synchronous Motors With Concentrated Windings
    Katsumi Yamazaki, Member, IEEE, and Yu Fukushima, Equation (9)

    Parameters
    ----------
    self: LossModelMagnet
        a LossModelMagnet object
    machine: Machine
        a machine object

    Returns
    -------
    kseg : float
        Magnet segmentation coefficient
    """

    # Calculate segmentation coefficient from:
    # "Effect of Eddy-Current Loss Reduction by Magnet Segmentation in Synchronous Motors With Concentrated Windings"
    # Katsumi Yamazaki, Member, IEEE, and Yu Fukushima, Equation (9)
    # Get Hmag for segmentation calculation
    if isinstance(machine.rotor, LamSlotMag):
        magnet = machine.rotor.magnet
        slot = machine.rotor.slot
        if hasattr(slot, "Hmag"):
            Hmag = slot.Hmag
        else:
            Hmag = np.sqrt(slot.comp_surface_active())
        if hasattr(slot, "Wmag"):
            Wmag = slot.Wmag
        else:
            Wmag = np.sqrt(slot.comp_surface_active())

    elif isinstance(machine.rotor, LamHole):
        hole0 = machine.rotor.hole[0]
        magnet = hole0.get_magnet_dict()["magnet_0"]
        if isinstance(hole0, HoleM50):
            Hmag = hole0.H3
            Wmag = hole0.W4
        elif isinstance(hole0, (HoleM51, HoleM53, HoleM57, HoleM58)):
            Hmag = hole0.H2
            if isinstance(hole0, HoleM51):
                Wmag = (hole0.W3 + hole0.W5 + hole0.W7) / 3
            elif isinstance(hole0, HoleM53):
                Wmag = hole0.W3
            elif isinstance(hole0, HoleM57):
                Wmag = hole0.W4
            elif isinstance(hole0, HoleM58):
                Wmag = hole0.W1
        elif isinstance(hole0, HoleM52):
            Hmag = hole0.H1
            Wmag = hole0.W0
        else:  # HoleUD
            Hmag = np.sqrt(hole0.comp_surface_magnet_id(0))
            Wmag = Hmag
    else:
        raise Exception(
            "Cannot calculate magnet losses for rotor lamination other than LamSlotMag or LamHole"
        )
    Lmag = magnet.Lmag
    Nseg = magnet.Nseg
    kseg = ((Lmag + Wmag) / (Lmag * Nseg + Wmag)) ** 2

    return kseg
