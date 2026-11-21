from .....classes_common.logger_context import get_logger
from .....Classes_new.machine.cond_type_12 import CondType12
from .....Classes_new.machine.cond_type_11 import CondType11


def convert_conductor_to_P(self, is_stator) -> None:
    """selects step to add rules for conductor in stator

    Parameters
    ----------
    self : ConvertMC
        A ConvertMC object
    """
    if is_stator:
        winding = self.machine.stator.winding
    else:
        winding = self.machine.rotor.winding

    conductor_type = self.other_dict["[Winding_Design]"]["Wire_Type"]

    if conductor_type in ["AWG_Table", "Metric_Table", "Diameter_Input", "SWG_Table"]:
        winding.conductor = CondType12()

    elif conductor_type == "Rectangular":
        winding.conductor = CondType11()
        winding.conductor.Nwppc_rad = 1
        winding.conductor.Nwppc_tan = 2
    else:
        raise NotImplementedError(
            f"Type of conductor {conductor_type} has not equivalent or has not implement"
        )

    get_logger(self).info(
        f"Conversion {conductor_type} into {winding.conductor.__class__.__name__}"
    )
