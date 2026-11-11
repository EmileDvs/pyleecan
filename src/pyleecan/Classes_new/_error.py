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


class ConvertionError(Exception): ...


class DimError(Exception):
    """Raised when the dimension of the field does not match requested operation (3D vs 1D)"""


class EquivalentError(Exception): ...


class FEMMError(Exception):
    """Raised when FEMM is not possible to run"""


class FTError(Exception):
    """Raised when there is an error within the Fourier Transform methods (Data Object)"""


class AxisError(FTError):
    """Raised when the axis requested is not available (Data Object)"""


class FileError(Exception):
    """Raised when the file does not exists"""


class FormatError(Exception):
    pass


class GMSHInputError(Exception):
    """ """


class InitUnKnowClassError(CheckError):
    """ """


class InputError(Exception):
    """Raised when the input data are incomplete or incorrect"""


class LoadMissingFileError(Exception):
    """ """


class LoadMissingFolderError(Exception):
    """ """


class LoadSwitchError(Exception):
    """ """


class LoadWrongDictClassError(Exception):
    """ """


class LoadWrongTypeError(Exception):
    """ """


class MachineCheckError(Exception):
    """ """


class LaminationCheckError(MachineCheckError):
    """ """


class LMC_SlotTooLong(LaminationCheckError):
    """ """


class Lam_WindCheckError(LaminationCheckError):
    """ """


class NormError(FTError):
    """Raised when the normalization cannot be applied (Data Object)"""


class NotADictError(CheckError):
    """ """


class NotImplementedYetError(Exception):
    """NotImplementedYetError"""


class NotchError(Exception):
    """Raised when notch are coliding"""


class OPMatrixException(Exception):
    """Raise when OP_matrix was wrongly defined"""


class ParentMissingError(Exception):
    """ParentMissingError"""


class PathImportError(Exception):
    """Raised when the path could not be imported"""


class PyleecanImportError(Exception):
    """Raised when the data import or generation is not possible"""


class RetroCompatibilityError(Exception):
    pass


class SlotCheckError(LaminationCheckError):
    """ """


class SurfaceError(Exception):
    pass


class UnitError(FTError):
    """Raised when the unit requested is not available or does not match the existing one (Data Object)"""


class UnknowInitDictKeyError(CheckError):
    """ """


class WindingError(Exception):
    """ """
