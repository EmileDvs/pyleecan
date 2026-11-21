

def get_elec_datakeeper(self, symbol_list: list, is_multi: bool = False) -> list:
    """Generate DataKeepers to store by default results from electric module
    Parameters
    ----------
    self: VarLoad
        A VarLoad object
    symbol_list : list
        List of the existing datakeeper (to avoid duplicate)
    is_multi : bool
        True for multi-simulation of multi-simulation
    Returns
    -------
    dk_list: list
        list of DataKeeper
    """

    dk_dict = self.get_elec_datakeeper_dict()
    dk_list = []
    quantity_list = ["Id", "Iq", "Ud", "Uq"]

    # Save Id
    if not is_multi:
        for key in quantity_list:
            if key not in symbol_list:
                dk_list.append(dk_dict[key])

    return dk_list
