"""Generated shared exception classes; do not edit by hand."""


class AbstractClassError(Exception):
    pass


class AngleArc2Error(Exception):
    """ """


class AnglePolarArcError(Exception):
    """ """


class AngleRotationArc1Error(Exception):
    """ """


class AngleRotationArc2Error(Exception):
    """ """


class AngleRotationArc3Error(Exception):
    """ """


class AngleRotationCircleError(Exception):
    """ """


class AngleRotationSegmentError(Exception):
    """ """


class BHShapeError(Exception):
    """Raised when the BH curve has not the expected shape"""


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


class CircleBuildGeometryError(Exception):
    """ """


class ConvertionError(Exception): ...


class DataKeeperError(Exception):
    pass


class DimError(Exception):
    """Raised when the dimension of the field does not match requested operation (3D vs 1D)"""


class ElmerResultsVTUError(Exception):
    pass


class ElmerSectionError(Exception):
    pass


class EquivalentError(Exception): ...


class FEMMError(Exception):
    """Raised when FEMM is not possible to run"""


class FTError(Exception):
    """Raised when there is an error within the Fourier Transform methods (Data Object)"""


class AxisError(FTError):
    """Raised when the axis requested is not available (Data Object)"""


class FieldMissingError(Exception):
    """A field needed by a method is None"""


class FileError(Exception):
    """Raised when the file does not exists"""


class FormatError(Exception):
    pass


class GMSHInputError(Exception):
    """ """


class GetOutError(Exception):
    """Raised when an output can't be returned"""


class InitUnKnowClassError(CheckError):
    """ """


class InputError(Exception):
    """Raised when the input data are incomplete or incorrect"""


class KeyInputError(Exception):
    """ """


class LabelInputError(Exception):
    """ """


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


class LC_RadiusError(LaminationCheckError):
    """ """


class LC_VentYokeIn(LaminationCheckError):
    """ """


class LC_VentYokeOut(LaminationCheckError):
    """ """


class LMC_SlotTooLong(LaminationCheckError):
    """ """


class LamSlotMultiAlphaError(LaminationCheckError):
    """ """


class Lam_SlotCheckError(LaminationCheckError):
    """ """


class LSC_SlotTooLong(Lam_SlotCheckError):
    """ """


class Lam_WindCheckError(LaminationCheckError):
    """ """


class CondCheckError(Lam_WindCheckError):
    """ """


class Cond12CheckError(CondCheckError):
    """ """


class C12_WireDontFit(Cond12CheckError):
    """ """


class LWC_SlotTooLong(Lam_WindCheckError):
    """ """


class M1C_RingTooLarge(MachineCheckError):
    """ """


class M1C_SquirrelCagePError(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    winding
        have a different p value as the rotor one

    """


class M1C_WrongRotor(MachineCheckError):
    """ """


class M1C_WrongStator(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    with
        Winding

    """


class M2C_MagnetTooLarge(MachineCheckError):
    """ """


class M2C_PError(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    values


    """


class M2C_WrongRotor(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    Magnet


    """


class M2C_WrongStator(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    with
        Winding

    """


class M3C_PError(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    values


    """


class M3C_WrongRotor(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    with
        Magnet

    """


class M3C_WrongStator(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    with
        Winding

    """


class M4C_PError(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    different
        p value

    """


class M4C_WrongRotor(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    with
        Winding

    """


class M4C_WrongStator(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    with
        Winding

    """


class MC_AbstractError(MachineCheckError):
    """ """


class MC_BothExternal(MachineCheckError):
    """ """


class MC_BothInternal(MachineCheckError):
    """ """


class MC_MecAirgapError(MachineCheckError):
    """ """


class MC_RotorDontFit(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    stator


    """


class MC_RotorIsStator(MachineCheckError):
    """ """


class MC_ShaftTooBig(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    rotor


    """


class MC_ShaftTooSmall(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    rotor


    """


class MC_StatorDontFit(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    rotor


    """


class MC_StatorNotStator(MachineCheckError):
    """ """


class MSy_PError(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    values


    """


class MSy_WrongRotor(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    with
        Magnet

    """


class MSy_WrongStator(MachineCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    with
        Winding

    """


class MagnetIndexError(Exception):
    """Raise when trying to access a non existing magnet"""


class NbPointArc1DError(Exception):
    """ """


class NbPointArc2DError(Exception):
    """ """


class NbPointArc3DError(Exception):
    """ """


class NbPointPolarArcError(Exception):
    """ """


class NbPointSegmentDError(Exception):
    """ """


class NormError(FTError):
    """Raised when the normalization cannot be applied (Data Object)"""


class NotADictError(CheckError):
    """ """


class NotImplementedYetError(Exception):
    """NotImplementedYetError"""


class NotPlotableError(Exception):
    """ """


class NotchError(Exception):
    """Raised when notch are coliding"""


class OPMatrixException(Exception):
    """Raise when OP_matrix was wrongly defined"""


class OptimizationAttributeError(Exception):
    """Class to Raise an error"""

    def __init__(self, message) -> None:
        self.message = message


class ParamExplorerError(Exception):
    pass


class ParentMissingError(Exception):
    """ParentMissingError"""


class PathImportError(Exception):
    """Raised when the path could not be imported"""


class PlotError(Exception):
    pass


class PointArc1Error(Exception):
    """ """


class PointArc2Error(Exception):
    """ """


class PointArc3Error(Exception):
    """ """


class PointSegmentError(Exception):
    """ """


class PointTranslateArc1Error(Exception):
    """ """


class PointTranslateArc2Error(Exception):
    """ """


class PointTranslateArc3Error(Exception):
    """ """


class PointTranslateCircleError(Exception):
    """ """


class PointTranslateSegmentError(Exception):
    """ """


class PolarArcBuildGeometryError(Exception):
    """ """


class PyleecanImportError(Exception):
    """Raised when the data import or generation is not possible"""


class GenSinDimError(PyleecanImportError):
    """Raised when the ImportGenVectSin of the sin_list has different size (N)"""


class GenSinEmptyError(PyleecanImportError):
    """Raised when the sin_list is empty"""


class GenSinTransposeError(PyleecanImportError):
    """Raised when the ImportGenVectSin of the sin_list has different is_transpose"""


class InitSinMatDimError(PyleecanImportError):
    """Raised when the init_vector is called with wrong arguments"""


class MatFileError(PyleecanImportError):
    """Raised when the file_path is wrong or the variable is missing"""


class RadiusArc1Error(Exception):
    """ """


class RadiusCircleError(Exception):
    """ """


class RetroCompatibilityError(Exception):
    pass


class SRM_WrongRotor(MachineCheckError):
    pass


class SRM_WrongStator(MachineCheckError):
    pass


class Slot26_H1(Exception):
    """ """


class SlotCheckError(LaminationCheckError):
    """ """


class H54_R1CheckError(SlotCheckError):
    """ """


class H54_W0CheckError(SlotCheckError):
    """ """


class S10_H1rCheckError(SlotCheckError):
    """ """


class S10_W01CheckError(SlotCheckError):
    """ """


class S10_W02CheckError(SlotCheckError):
    """ """


class S11_2_H1rCheckError(SlotCheckError):
    """ """


class S11_2_R1CheckError(SlotCheckError):
    """ """


class S11_2_RHCheckError(SlotCheckError):
    """ """


class S11_2_RWCheckError(SlotCheckError):
    """ """


class S11_2_W01CheckError(SlotCheckError):
    """ """


class S11_H1rCheckError(SlotCheckError):
    """ """


class S11_R1CheckError(SlotCheckError):
    """ """


class S11_RHCheckError(SlotCheckError):
    """ """


class S11_RWCheckError(SlotCheckError):
    """ """


class S11_W01CheckError(SlotCheckError):
    """ """


class S12_R20CheckError(SlotCheckError):
    """ """


class S12_RboCheckError(SlotCheckError):
    """ """


class S13_H1rCheckError(SlotCheckError):
    """ """


class S13_W01CheckError(SlotCheckError):
    """ """


class S13_W12CheckError(SlotCheckError):
    """ """


class S14_Rbo0CheckError(SlotCheckError):
    """ """


class S14_Rbo1CheckError(SlotCheckError):
    """ """


class S15InnerError(SlotCheckError):
    """ """


class S16AlphaT(SlotCheckError):
    """ """


class S16OutterError(SlotCheckError):
    """ """


class S16_W01CheckError(SlotCheckError):
    """ """


class S19_W1CheckError(SlotCheckError):
    """ """


class S21_H1rCheckError(SlotCheckError):
    """ """


class S21_W01CheckError(SlotCheckError):
    """ """


class S22_A02CheckError(SlotCheckError):
    """ """


class S22_SpCheckError(SlotCheckError):
    """ """


class S23_H1rCheckError(SlotCheckError):
    """ """


class S23_W01CheckError(SlotCheckError):
    """ """


class S24_HWCheckError(SlotCheckError):
    """ """


class S24_W3CheckError(SlotCheckError):
    """ """


class S25_HWCheckError(SlotCheckError):
    """ """


class S25_W4CheckError(SlotCheckError):
    """ """


class S26_WCheckError(SlotCheckError):
    """ """


class S27_W01CheckError(SlotCheckError):
    """ """


class S27_W03CheckError(SlotCheckError):
    """ """


class S27_W12CheckError(SlotCheckError):
    """ """


class S28_R1R1CheckError(SlotCheckError):
    """ """


class S28_R1W3CheckError(SlotCheckError):
    """ """


class S28_RboW0CheckError(SlotCheckError):
    """ """


class S28_ZsCheckError(SlotCheckError):
    """ """


class S29_H2CheckError(SlotCheckError):
    """ """


class S29_W01CheckError(SlotCheckError):
    """ """


class S30_R1Error(SlotCheckError):
    """ """


class S30_R2Error(SlotCheckError):
    """ """


class S30_W0Error(SlotCheckError):
    """ """


class S30_W3Error(SlotCheckError):
    """ """


class S50_H01CheckError(SlotCheckError):
    """ """


class S50_H23CheckError(SlotCheckError):
    """ """


class S50_NoneError(SlotCheckError):
    """Raised when a propery of HoleM50 is None"""


class S50_SpCheckError(SlotCheckError):
    """ """


class S50_W01CheckError(SlotCheckError):
    """ """


class S50_W3CheckError(SlotCheckError):
    """ """


class S50_W5CheckError(SlotCheckError):
    """ """


class S51_AlphaCheckError(SlotCheckError):
    """ """


class S51_NoneError(SlotCheckError):
    """Raised when a propery of HoleM51 is None"""


class S51_RHCheckError(SlotCheckError):
    """ """


class S51_WCheckError(SlotCheckError):
    """ """


class S52R_H12CheckError(SlotCheckError):
    """ """


class S52R_NoneError(SlotCheckError):
    """Raised when a propery of HoleM52R is None"""


class S52R_R0CheckError(SlotCheckError):
    """ """


class S52R_widthCheckError(SlotCheckError):
    """ """


class S52_H12CheckError(SlotCheckError):
    """ """


class S52_NoneError(SlotCheckError):
    """Raised when a propery of HoleM52 is None"""


class S52_W1CheckError(SlotCheckError):
    """ """


class S52_alphaCheckError(SlotCheckError):
    """ """


class S53_NoneError(SlotCheckError):
    """Raised when a propery of HoleM53 is None"""


class S53_Rext0CheckError(SlotCheckError):
    """ """


class S53_Rext1CheckError(SlotCheckError):
    """ """


class S53_W4CheckError(SlotCheckError):
    """ """


class S53_W5CheckError(SlotCheckError):
    """ """


class S54_NoneError(SlotCheckError):
    """Raised when a propery of HoleM54 is None"""


class S57_NoneError(SlotCheckError):
    """Raised when a propery of HoleM57 is None"""


class S58_NoneError(SlotCheckError):
    """Raised when a propery of HoleM58 is None"""


class S58_WCheckError(SlotCheckError):
    """ """


class S60_InnerCheckError(SlotCheckError):
    """ """


class S60_NoneError(SlotCheckError):
    """Raised when a propery of HoleM58 is None"""


class S60_RCheckError(SlotCheckError):
    """ """


class S60_W21CheckError(SlotCheckError):
    """ """


class S60_WCheckError(SlotCheckError):
    """ """


class S60_WindError(SlotCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    winding


    """


class S60_WindHError(SlotCheckError):
    """ """


class S60_WindWError(SlotCheckError):
    """ """


class S61_InnerCheckError(SlotCheckError):
    """ """


class S61_NoneError(SlotCheckError):
    """Raised when a propery of HoleM58 is None"""


class S61_W21CheckError(SlotCheckError):
    """ """


class S61_WCheckError(SlotCheckError):
    """ """


class S61_WindError(SlotCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    winding


    """


class S61_WindHError(SlotCheckError):
    """ """


class S61_WindWError(SlotCheckError):
    """ """


class S62_H1Error(SlotCheckError):
    """ """


class S62_H2Error(SlotCheckError):
    """ """


class S62_InnerCheckError(SlotCheckError):
    """ """


class S62_NoneError(SlotCheckError):
    """Raised when a propery of HoleM62 is None"""


class S62_W0Error(SlotCheckError):
    """ """


class S62_W1Error(SlotCheckError):
    """ """


class S62_W2Error(SlotCheckError):
    """ """


class S62_WindError(SlotCheckError):
    """ """


class S62_WindHError(SlotCheckError):
    """ """


class S63_H0CheckError(SlotCheckError):
    """ """


class S63_InnerCheckError(SlotCheckError):
    """ """


class S63_NoneError(SlotCheckError):
    """Raised when a propery of HoleM63 is None"""


class S63_W0CheckError(SlotCheckError):
    """ """


class S63_WindError(SlotCheckError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    winding


    """


class SLSRPMOutterError(SlotCheckError):
    """ """


class SLSRPM_NoneError(SlotCheckError):
    """Raised when a propery of HoleM52 is None"""


class Slot53InterError(SlotCheckError):
    """ """


class SquirrelCageCheckError(Lam_WindCheckError):
    """ """


class SCC_NotARotor(SquirrelCageCheckError):
    """ """


class SCC_WrongCond(SquirrelCageCheckError):
    """ """


class SurfaceError(Exception):
    pass


class TrapezeBuildGeometryError(Exception):
    """raised when the parameter have not good type"""


class TrapezeError(Exception):
    """ """


class UnitError(FTError):
    """Raised when the unit requested is not available or does not match the existing one (Data Object)"""


class UnknowInitDictKeyError(CheckError):
    """ """


class VarOptiConstraintError(Exception):
    pass


class VarOptiDataKeeperError(Exception):
    pass


class VarOptiDesignVarError(Exception):
    pass


class VarOptiError(Exception):
    pass


class VarOptiObjectiveError(Exception):
    pass


class VarOptiSolverError(Exception):
    pass


class VarSimuError(Exception):
    pass


class VentilationCircInstanceError(Exception):
    """ """


class VentilationPolarInstanceError(Exception):
    """ """


class VentilationTrapInstanceError(Exception):
    """Raised when a Ventilation Trap parameter is not int or float"""


class WindingError(Exception):
    """ """


class WindingDefMsError(WindingError):
    """ """


class WindingT10DefQsError(WindingError):
    """ """


class WindingT1DefMsError(WindingError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    must
        be 0

    """


class WindingT2DefNtError(WindingError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    must
        be 0

    """


class WindingT5DefMsError(WindingError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    must
        be 0

    """


class XOutputError(Exception):
    pass


class XlsFileError(PyleecanImportError):
    """Raised when the file_path is wrong"""
