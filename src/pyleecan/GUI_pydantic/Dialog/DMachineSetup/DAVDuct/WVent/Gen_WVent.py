"""File generated according to WVent/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_WVent import Ui_WVent


class Gen_WVent(Ui_WVent):
    def setupUi(self, WVent):
        """Set the widget limits and help texts (class information)"""
        Ui_WVent.setupUi(self, WVent)
        # Setup of in_Alpha0
        txt = self.tr('Shift angle of the holes around circumference')
        self.in_Alpha0.setWhatsThis(txt)
        self.in_Alpha0.setToolTip(txt)

        # Setup of lf_Alpha0
        self.lf_Alpha0.validator().setBottom(0)
        self.lf_Alpha0.validator().setTop(6.29)
        txt = self.tr('Shift angle of the holes around circumference')
        self.lf_Alpha0.setWhatsThis(txt)
        self.lf_Alpha0.setToolTip(txt)
