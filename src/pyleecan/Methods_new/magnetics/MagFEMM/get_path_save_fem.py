import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def get_path_save_fem(self, output: Output) -> str:
    """Return the path to save the FEMM simulation

    Parameters
    ----------
    self : MagFEMM
        a MagFEMM object
    output : Output
        an Output object

        Returns
    -------
    save_path: str
        Path to save the .fem file

    """
    save_dir = self.get_path_save(output)

    if self.file_name not in [None, ""]:
        if self.file_name[-4:] != ".fem":
            file_name = self.file_name + ".fem"
        else:
            file_name = self.file_name
    elif output.simu.machine.name not in [None, ""]:
        file_name = output.simu.machine.name + "_model.fem"
    elif output.simu.name not in [None, ""]:
        file_name = output.simu.name + "_model.fem"
    else:  # Default name
        file_name = "FEMM_simulation.fem"

    return os.path.join(save_dir, file_name)
