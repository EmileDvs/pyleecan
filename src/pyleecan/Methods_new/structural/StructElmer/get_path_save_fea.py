import os


# TODO improve path


def get_path_save_fea(self, output):
    """Return the path to save the FEA simulation

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
    path_res = output.get_path_result()

    save_dir = os.path.join(path_res, "Elmer_Elasticity")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    return save_dir
