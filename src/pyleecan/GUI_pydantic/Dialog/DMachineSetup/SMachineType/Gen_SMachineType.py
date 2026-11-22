"""File generated according to SMachineType/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_SMachineType import Ui_SMachineType


class Gen_SMachineType(Ui_SMachineType):
    def setupUi(self, SMachineType):
        """Set the widget limits and help texts (class information)"""
        Ui_SMachineType.setupUi(self, SMachineType)
        # Setup of si_p
        self.si_p.setMinimum(1)
        self.si_p.setMaximum(999999)
        txt = self.tr('pole pairs number')
        self.si_p.setWhatsThis(txt)
        self.si_p.setToolTip(txt)

        # Setup of in_p
        txt = self.tr('pole pairs number')
        self.in_p.setWhatsThis(txt)
        self.in_p.setToolTip(txt)
