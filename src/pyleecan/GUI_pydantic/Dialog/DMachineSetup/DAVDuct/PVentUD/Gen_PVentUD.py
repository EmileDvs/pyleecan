"""File generated according to PVentUD/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_PVentUD import Ui_PVentUD


class Gen_PVentUD(Ui_PVentUD):
    def setupUi(self, PVentUD):
        """Set the widget limits and help texts (class information)"""
        Ui_PVentUD.setupUi(self, PVentUD)
        # Setup of in_Zh
        txt = self.tr('Number of Hole around the circumference')
        self.in_Zh.setWhatsThis(txt)
        self.in_Zh.setToolTip(txt)

        # Setup of si_Zh
        self.si_Zh.setMinimum(0)
        self.si_Zh.setMaximum(999999)
        txt = self.tr('Number of Hole around the circumference')
        self.si_Zh.setWhatsThis(txt)
        self.si_Zh.setToolTip(txt)
