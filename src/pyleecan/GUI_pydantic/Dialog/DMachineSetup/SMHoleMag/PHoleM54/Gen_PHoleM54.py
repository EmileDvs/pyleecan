"""File generated according to PHoleM54/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_PHoleM54 import Ui_PHoleM54


class Gen_PHoleM54(Ui_PHoleM54):
    def setupUi(self, PHoleM54):
        """Set the widget limits and help texts (class information)"""
        Ui_PHoleM54.setupUi(self, PHoleM54)
        # Setup of in_R1
        txt = self.tr('Hole radius')
        self.in_R1.setWhatsThis(txt)
        self.in_R1.setToolTip(txt)

        # Setup of lf_R1
        self.lf_R1.validator().setBottom(0)
        txt = self.tr('Hole radius')
        self.lf_R1.setWhatsThis(txt)
        self.lf_R1.setToolTip(txt)

        # Setup of in_W0
        txt = self.tr('Hole angular width')
        self.in_W0.setWhatsThis(txt)
        self.in_W0.setToolTip(txt)

        # Setup of lf_W0
        self.lf_W0.validator().setBottom(0)
        txt = self.tr('Hole angular width')
        self.lf_W0.setWhatsThis(txt)
        self.lf_W0.setToolTip(txt)

        # Setup of in_H0
        txt = self.tr('Hole depth')
        self.in_H0.setWhatsThis(txt)
        self.in_H0.setToolTip(txt)

        # Setup of lf_H0
        self.lf_H0.validator().setBottom(0)
        txt = self.tr('Hole depth')
        self.lf_H0.setWhatsThis(txt)
        self.lf_H0.setToolTip(txt)

        # Setup of in_H1
        txt = self.tr('Hole width')
        self.in_H1.setWhatsThis(txt)
        self.in_H1.setToolTip(txt)

        # Setup of lf_H1
        self.lf_H1.validator().setBottom(0)
        txt = self.tr('Hole width')
        self.lf_H1.setWhatsThis(txt)
        self.lf_H1.setToolTip(txt)
