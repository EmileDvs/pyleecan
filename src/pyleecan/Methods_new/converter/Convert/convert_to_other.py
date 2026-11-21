from ....classes_common.logger_context import get_logger
from ....classes_common.errors import ConvertionError
from .... import __version__
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def convert_to_other(self, machine: Machine) -> dict:
    """conversion obj machine in dict

    Parameters
    ----------
    self : ConvertMC
        A ConvertMC object
    machine : Machine
        A pyleecan machine

    Returns
    ---------
    other_dict : dict
        A dict with the conversion obj machine
    """
    self.machine = machine
    self.is_P_to_other = True
    self.other_dict = {}
    self.rules_list = []

    self.init_other_unit()

    get_logger(self).info(f"Pyleecan version : {__version__}")
    get_logger(self).info("Conversion obj machine into dict")

    # conversion machine in dict
    self.select_machine_rules()

    # conversion rule in dict
    for rule in self.rules_list:
        try:
            self.other_dict = rule.convert_to_other(
                self.other_dict, self.machine, self.other_unit_dict
            )
        except Exception as e:
            raise ConvertionError(f"Error while running rule {rule.get_name()}:\n{e}")

    get_logger(self).info("End of conversion, dict is create")

    get_logger(self)

    return self.other_dict
