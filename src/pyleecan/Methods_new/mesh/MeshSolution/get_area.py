def get_area(self, group_names: list[str] | None = None, indices: list | None = None):
    """Get the surface area of the specified groups of a MeshSolution

    Parameters
    ----------
    self : MeshSolution
        a MeshSolution object
    group_names : list of str
        list of the groups names or string of a single group
    indices : list
        list of indices, if not given all indices are considered
    Return
    ------
    area : float
        surface area of the specified groups and indices

    """
    if group_names is not None:
        meshsol = self.get_group(group_names=group_names)
    else:
        meshsol = self

    msh = meshsol.mesh

    return msh.get_element_area(indices=indices).sum()
