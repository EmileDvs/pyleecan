import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output



def get_path_save(self, output: Output) -> str:
    """Return the path to save the Elmer simulation

    Parameters
    ----------
    self : MagElmer
        a MagElmer object
    output : Output
        an Output object

        Returns
    -------
    save_path: str
        Path to save the Elmer simulation

    """
    path_res = output.get_path_result()

    save_dir = os.path.join(path_res, "Elmer")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    return save_dir
