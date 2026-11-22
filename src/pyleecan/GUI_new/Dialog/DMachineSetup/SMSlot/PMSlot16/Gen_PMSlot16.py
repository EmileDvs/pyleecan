"""File generated according to PMSlot16/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_PMSlot16 import Ui_PMSlot16


class Gen_PMSlot16(Ui_PMSlot16):
    def setupUi(self, PMSlot16):
        """Set the widget limits and help texts (class information)"""
        Ui_PMSlot16.setupUi(self, PMSlot16)
        # Setup of in_W0
        txt = self.tr('Slot isthmus width.')
        self.in_W0.setWhatsThis(txt)
        self.in_W0.setToolTip(txt)

        # Setup of lf_W0
        self.lf_W0.validator().setBottom(0)
        txt = self.tr('Slot isthmus width.')
        self.lf_W0.setWhatsThis(txt)
        self.lf_W0.setToolTip(txt)

        # Setup of in_W1
        txt = self.tr('Slot Width')
        self.in_W1.setWhatsThis(txt)
        self.in_W1.setToolTip(txt)

        # Setup of lf_W1
        self.lf_W1.validator().setBottom(0)
        txt = self.tr('Slot Width')
        self.lf_W1.setWhatsThis(txt)
        self.lf_W1.setToolTip(txt)

        # Setup of in_H0
        txt = self.tr('Slot isthmus height.')
        self.in_H0.setWhatsThis(txt)
        self.in_H0.setToolTip(txt)

        # Setup of lf_H0
        self.lf_H0.validator().setBottom(0)
        txt = self.tr('Slot isthmus height.')
        self.lf_H0.setWhatsThis(txt)
        self.lf_H0.setToolTip(txt)

        # Setup of in_H1
        txt = self.tr('Slot Height')
        self.in_H1.setWhatsThis(txt)
        self.in_H1.setToolTip(txt)

        # Setup of lf_H1
        self.lf_H1.validator().setBottom(0)
        txt = self.tr('Slot Height')
        self.lf_H1.setWhatsThis(txt)
        self.lf_H1.setToolTip(txt)
