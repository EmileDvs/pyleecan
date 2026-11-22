"""File generated according to PBoreFlower/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_PBoreFlower import Ui_PBoreFlower


class Gen_PBoreFlower(Ui_PBoreFlower):
    def setupUi(self, PBoreFlower):
        """Set the widget limits and help texts (class information)"""
        Ui_PBoreFlower.setupUi(self, PBoreFlower)
        # Setup of in_N
        txt = self.tr('Number of flower arc')
        self.in_N.setWhatsThis(txt)
        self.in_N.setToolTip(txt)

        # Setup of si_N
        self.si_N.setMinimum(0)
        self.si_N.setMaximum(999999)
        txt = self.tr('Number of flower arc')
        self.si_N.setWhatsThis(txt)
        self.si_N.setToolTip(txt)

        # Setup of in_Rarc
        txt = self.tr('Radius of the flower arc')
        self.in_Rarc.setWhatsThis(txt)
        self.in_Rarc.setToolTip(txt)

        # Setup of lf_Rarc
        self.lf_Rarc.validator().setBottom(0)
        txt = self.tr('Radius of the flower arc')
        self.lf_Rarc.setWhatsThis(txt)
        self.lf_Rarc.setToolTip(txt)
