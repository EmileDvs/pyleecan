import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output



def get_path_save(self, output: Output) -> str:
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
        Path to save the FEMM simulation

    """
    path_res = output.get_path_result()

    save_dir = os.path.join(path_res, "Femm")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    return save_dir
