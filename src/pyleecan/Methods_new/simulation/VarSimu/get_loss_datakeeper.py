from ....classes_common.functions import SourceFunction
from ....Classes_new.simulation.data_keeper import DataKeeper


def get_loss_datakeeper(self, symbol_list: list, is_multi: bool = False) -> list:
    """Generate DataKeepers to store by default results from loss module

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

    dict_loss = {
        "L_{tot}": "overall",
        "L_{sta}": "stator core",
        "L_{joule}": "stator joule",
        "L_{prox}": "stator proximity",
        "L_{rot}": "rotor core",
        "L_{mag}": "rotor magnets",
    }

    dk_list = [
        DataKeeper(
            name="Input power",
            unit="W",
            symbol="P_{in}",
            keeper=SourceFunction('lambda output: output.loss.P_in'),
            error_keeper=SourceFunction('lambda simu: np.nan'),
        ),
        DataKeeper(
            name="Output power",
            unit="W",
            symbol="P_{out}",
            keeper=SourceFunction('lambda output: output.loss.P_out'),
            error_keeper=SourceFunction('lambda simu: np.nan'),
        ),
        DataKeeper(
            name="Efficiency",
            unit="%",
            symbol="\\eta",
            keeper=SourceFunction('lambda output: 100*output.loss.efficiency'),
            error_keeper=SourceFunction('lambda simu: np.nan'),
        ),
    ]

    dk_list.extend(
        [
            DataKeeper(
                name=group_name + " losses",
                unit="W",
                symbol=symb,
                keeper=SourceFunction(
                    "lambda output: output.loss.loss_dict['"
                    + str(group_name)
                    + "'].get_loss_scalar(output.elec.OP.felec)"
                ),
                error_keeper=SourceFunction('lambda simu: np.nan'),
            )
            for symb, group_name in dict_loss.items()
        ]
    )

    dk_list.append(
        DataKeeper(
            name="Mechanical torque",
            unit="Nm",
            symbol="Tmech_{av}",
            keeper=SourceFunction('lambda output: output.loss.Tmech_av'),
            error_keeper=SourceFunction('lambda simu: np.nan'),
        )
    )

    return dk_list
