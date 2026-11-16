def plot_mesh(self, group_names: list | None = None, save_path: str | None = None):
    """Plot the losses on the mesh solution

    Parameters
    ----------
    self : OutLossModel
        An OutLossModel object
    group_names : list
        a list of str corresponding to group name(s)
    save_path : str
        path to save the figure

    """

    return (
        self.get_mesh_solution()
        .get_group(group_names)
        .plot_contour(
            "freqs=sum",
            label=f"{self.name} loss density",
            save_path=save_path,
        )
    )
