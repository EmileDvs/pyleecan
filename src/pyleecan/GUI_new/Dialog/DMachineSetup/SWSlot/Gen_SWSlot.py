"""File generated according to SWSlot/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_SWSlot import Ui_SWSlot


class Gen_SWSlot(Ui_SWSlot):
    def setupUi(self, SWSlot):
        """Set the widget limits and help texts (class information)"""
        Ui_SWSlot.setupUi(self, SWSlot)
        # Setup of in_Zs
        txt = self.tr('slot number')
        self.in_Zs.setWhatsThis(txt)
        self.in_Zs.setToolTip(txt)

        # Setup of si_Zs
        self.si_Zs.setMinimum(0)
        self.si_Zs.setMaximum(999999)
        txt = self.tr('slot number')
        self.si_Zs.setWhatsThis(txt)
        self.si_Zs.setToolTip(txt)
