"""Generated shared exception classes; do not edit by hand."""


class CheckDimError(Exception):
    """ """


class CheckError(Exception):
    """ """


class CheckMaxError(CheckError):
    """ """


class CheckMinError(CheckError):
    """ """


class CheckTypeError(CheckError):
    """ """


class InitUnKnowClassError(CheckError):
    """ """


class InputError(Exception):
    """Raised when the input data are incomplete or incorrect"""


class MachineCheckError(Exception):
    """ """


class LaminationCheckError(MachineCheckError):
    """ """


class LMC_SlotTooLong(LaminationCheckError):
    """ """


class Lam_WindCheckError(LaminationCheckError):
    """ """


class NotADictError(CheckError):
    """ """


class NotImplementedYetError(Exception):
    """NotImplementedYetError"""


class OPMatrixException(Exception):
    """Raise when OP_matrix was wrongly defined"""


class ParentMissingError(Exception):
    """ParentMissingError"""


class PyleecanImportError(Exception):
    """Raised when the data import or generation is not possible"""


class SlotCheckError(LaminationCheckError):
    """ """


class UnknowInitDictKeyError(CheckError):
    """ """


class WindingError(Exception):
    """ """
