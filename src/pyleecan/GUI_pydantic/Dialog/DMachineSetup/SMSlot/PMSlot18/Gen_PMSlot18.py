"""File generated according to PMSlot18/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_PMSlot18 import Ui_PMSlot18


class Gen_PMSlot18(Ui_PMSlot18):
    def setupUi(self, PMSlot18):
        """Set the widget limits and help texts (class information)"""
        Ui_PMSlot18.setupUi(self, PMSlot18)
        # Setup of in_H0
        txt = self.tr('Magnet Height')
        self.in_H0.setWhatsThis(txt)
        self.in_H0.setToolTip(txt)

        # Setup of lf_H0
        self.lf_H0.validator().setBottom(0)
        txt = self.tr('Magnet Height')
        self.lf_H0.setWhatsThis(txt)
        self.lf_H0.setToolTip(txt)
