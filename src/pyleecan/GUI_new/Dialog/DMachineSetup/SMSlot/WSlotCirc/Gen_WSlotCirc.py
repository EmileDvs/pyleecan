"""File generated according to WSlotCirc/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_WSlotCirc import Ui_WSlotCirc


class Gen_WSlotCirc(Ui_WSlotCirc):
    def setupUi(self, WSlotCirc):
        """Set the widget limits and help texts (class information)"""
        Ui_WSlotCirc.setupUi(self, WSlotCirc)
        # Setup of in_W0
        txt = self.tr('Slot isthmus width.')
        self.in_W0.setWhatsThis(txt)
        self.in_W0.setToolTip(txt)

        # Setup of lf_W0
        self.lf_W0.validator().setBottom(0)
        txt = self.tr('Slot isthmus width.')
        self.lf_W0.setWhatsThis(txt)
        self.lf_W0.setToolTip(txt)

        # Setup of in_H0
        txt = self.tr('Slot height')
        self.in_H0.setWhatsThis(txt)
        self.in_H0.setToolTip(txt)

        # Setup of lf_H0
        self.lf_H0.validator().setBottom(0)
        txt = self.tr('Slot height')
        self.lf_H0.setWhatsThis(txt)
        self.lf_H0.setToolTip(txt)
