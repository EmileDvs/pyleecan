from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def comp_joule_losses(self, out_dict: dict, machine: Machine) -> dict:
    """Compute the electrical Joule losses

    Parameters
    ----------
    self : EEC_PMSM
        an EEC_PMSM object
    out_dict : dict
        Dict containing all magnetic quantities that have been calculated in comp_parameters of EEC
    machine : Machine
        a Machine object

    Returns
    ------
    out_dict : dict
        Dict containing all magnetic quantities that have been calculated in EEC
    """

    qs = machine.stator.winding.qs
    Id, Iq = out_dict["Id"], out_dict["Iq"]
    R1 = self.R1

    # Id and Iq are in RMS
    Pj_losses = qs * R1 * (Id**2 + Iq**2)

    out_dict["Pj_losses"] = Pj_losses

    return out_dict
