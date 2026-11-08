"""Generated shared exception classes; do not edit by hand."""


class NotImplementedYetError(Exception):
    """NotImplementedYetError"""


class ParentMissingError(Exception):
    """ParentMissingError"""


class PyleecanImportError(Exception):
    """Raised when the data import or generation is not possible"""


class MachineCheckError(Exception):
    """ """


class WindingError(Exception):
    """ """


class InputError(Exception):
    """Raised when the input data are incomplete or incorrect"""


class OPMatrixException(Exception):
    """Raise when OP_matrix was wrongly defined"""


class LaminationCheckError(MachineCheckError):
    """ """


class LMC_SlotTooLong(LaminationCheckError):
    """ """


class Lam_WindCheckError(LaminationCheckError):
    """ """


class SlotCheckError(LaminationCheckError):
    """ """
