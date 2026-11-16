from . import XOutputError


def get_paramexplorer(self, symbol: str):
    """Get the ParamExplorer with symbol
    Parameters
    ----------
    symbol: str
        ParamExplorer symbol
    """
    for paramexplorer in self.paramexplorer_list:
        if paramexplorer.symbol == symbol:
            return paramexplorer

    raise XOutputError("Unknown symbol {}".format(symbol))
