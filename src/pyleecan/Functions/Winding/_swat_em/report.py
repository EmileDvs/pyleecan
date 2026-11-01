"""
Provides functions for reports
"""

import os
import re
import tempfile

import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from . import analyse
from .config import config, get_phase_color


def italic(txt):
    return "<i>" + txt + "</i>"


def table_header(data):
    txt = ["<tr>"]
    for d in data:
        txt.append("<th>")
        txt.append(d)
        txt.append("</th>")
    txt.append("</tr>")
    return "".join(txt)


def table_row(data, col=None):
    if col:
        txt = [f'<tr bgcolor="{col}">']
    else:
        txt = ["<tr>"]
    for d in data:
        txt.append("<td>")
        txt.append(d)
        txt.append("</td>")
    txt.append("</tr>")
    return "".join(txt)


def red(text):
    txt = ['<span style=" color:#ff0000;" >']
    txt.append(text)
    txt.append("</span>")
    return "".join(txt)


def italic(text):
    return "<i>" + text + "</i>"


def bold(text):
    return "<b>" + text + "</b>"


def table(dat, header=[]):
    txt = ['<table style="width:100%">']
    if len(header) > 0:
        txt.append(table_header(header))
    col1 = "#FFFFFF"
    col2 = "#DDDADA"
    for i, d in enumerate(dat):
        col = col1 if i % 2 != 0 else col2
        txt.append(table_row(d, col=col))

    txt.append("</table>")
    return txt


def num2str(number, maxlen=8):
    """
    Converts a number to string with max number of signs

    Parameters
    ----------
    number : scalar, string
             Number to convert
    maxlen : integer
             Max. length to convert

    Returns
    -------
    return : string / list of strings / ndarray of strings
             string with the number
    """
    if number > 0:
        maxlen -= 1
    numstring = str(number)
    ematch = re.search("[eE].+", numstring)
    if ematch:
        # number in scientific
        exp = ematch.group()
        length = min(len(numstring), maxlen) - len(exp)
        numstring = numstring[:length] + exp
    else:
        numstring = numstring[:maxlen]
    if number >= 0.0:
        numstring = " " + numstring
    return numstring


def ascii_table2(head, dat, space=3):
    """
    Returns a formatted table as a string including end of line

    Parameters
    ----------
    head  : list of strings
            header of the columns
    dat   : 2d array_like with strings / list of lists of strings
            data for the table
    space : integer
            Distance between columens

    Returns
    -------
    return : string
             Formatted table
    """
    Ncol = len(head)  # Anzahl der Spalten
    if Ncol != len(dat):
        print("WARNUNG: Number of header elements != number of data columns")

    len_col = []
    for k in range(Ncol):
        maxlen = 0
        for s in range(len(dat[0])):
            maxlen = max(maxlen, len(dat[k][s]))
        len_col.append(max(maxlen, len(head[k])))

    out = ""
    for k in range(Ncol):
        diff = len_col[k] - len(head[k]) + space
        out += head[k] + " " * diff
    out += "\n"

    for s in range(len(dat[0])):
        for k in range(Ncol):
            diff = len_col[k] - len(dat[k][s]) + space
            out += dat[k][s] + " " * diff
        out += "\n"
    return out


class HtmlReport:
    def __init__(self, data):
        """
        Class for creating HTML reports of the winding

        Parameters
        ----------
        data :   datamodel object
                 winding model for creating the report
        """
        self.data = data
        self.template = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "template", "report.html")
        )

    def _create_figures(self, tmpdir):
        """
        Creates all figures for the winding

        Parameters
        ----------
        tmpdir : string
                 name of the directory to store the figures
        """
        if not os.path.isdir(tmpdir):
            os.mkdir(tmpdir)
        self.data.plot_layout(
            os.path.join(tmpdir, "plot_layout.png"), res=config["plt"]["res"]
        )
        self.data.plot_star(
            os.path.join(tmpdir, "plot_star.png"), res=config["plt"]["res"]
        )
        self.data.plot_windingfactor(
            os.path.join(tmpdir, "plot_wf_el.png"),
            mechanical=False,
            res=config["plt"]["res"],
        )
        self.data.plot_windingfactor(
            os.path.join(tmpdir, "plot_wf_mech.png"),
            mechanical=True,
            res=config["plt"]["res"],
        )
        self.data.plot_MMK(
            os.path.join(tmpdir, "plot_MMK.png"), res=config["plt"]["res"], phase=0
        )

    def create(self, filename=None):
        """
        Generates the html-report and returns the name of the html file

        Returns
        -------
        return : string
                 The file name of the html-file which is stored in tmp directory
        """
        if filename == None:
            self.tmpdir = tempfile.mkdtemp()
            self.filename = os.path.join(self.tmpdir, "report.html")
        else:
            self.tmpdir = os.path.abspath(os.path.dirname(filename))
            self.filename = filename
        self.contentdir = os.path.splitext(self.filename)[0] + "-files"
        try:
            os.mkdir(self.contentdir)
        except:
            pass

        #  filename = '/media/ramdisk/report.html'
        #  tmpdir = '/media/ramdisk'   # for testing

        self._create_figures(self.contentdir)

        # create table of star of slots
        d = []
        ei = self.data.results["Ei_el"][0]
        for km in range(len(ei)):
            A = np.abs(np.sum(ei[km]))
            ph = np.angle(np.sum(ei[km])) / np.pi * 180
            d.append([str(km + 1), str(round(A, 1)), str(round(ph, 1))])
        _table_star = "\n".join(table(d, header=["m", "A", "phase"]))

        # create table of winding factor
        # electrical
        d = []
        nu = np.array(self.data.results["nu_el"])
        kw = np.array(self.data.results["kw_el"])
        header = ["nu"] + self.data.get_phasenames()
        for i, line in enumerate(kw):
            d.append([str(nu[i])] + [str(round(k, 3)) for k in line])
        _table_wf_el = "\n".join(table(d, header=header))

        # mechanical
        d = []
        nu = np.array(self.data.results["nu_mech"])
        kw = np.array(self.data.results["kw_mech"])
        header = ["nu"] + self.data.get_phasenames()
        for i, line in enumerate(kw):
            d.append([str(nu[i])] + [str(round(k, 3)) for k in line])
        _table_wf_mech = "\n".join(table(d, header=header))

        # create MMK
        d = []
        phi, MMK, theta = analyse.calc_MMK(
            self.data.get_num_slots(),
            self.data.get_num_phases(),
            self.data.get_phases(),
            self.data.get_turns(),
            angle=0.0,
        )
        nu = np.array(self.data.results["MMK"]["nu"])
        HA = analyse.DFT(MMK[:-1])[: len(nu)]
        A = np.abs(HA)
        header = ["nu", "Amp", "[%]"]
        for k in range(len(nu)):
            a = A[k]
            a_rel = 100.0 / max(A) * a
            d.append([str(nu[k]), str(round(a, 3)), str(round(a_rel, 1))])
        _table_MMK = "\n".join(table(d, header=header))

        # Write to template
        with open(self.template) as f:
            tmpl = f.readlines()

        _report = []
        for line in tmpl:
            line = line.strip()
            line = line.replace("{{ TITLE }}", self.data.get_title())
            line = line.replace("{{ NOTES }}", self.data.get_notes())

            line = line.replace(
                "{{ plot_layout }}", os.path.join(self.contentdir, "plot_layout.png")
            )
            txt, html = self.data.get_basic_characteristics()
            line = line.replace("{{ table_bc }}", html)

            line = line.replace(
                "{{ plot_star }}", os.path.join(self.contentdir, "plot_star.png")
            )
            line = line.replace("{{ table_star }}", _table_star)
            line = line.replace(
                "{{ plot_wf_el }}", os.path.join(self.contentdir, "plot_wf_el.png")
            )
            line = line.replace("{{ table_wf_el }}", _table_wf_el)
            line = line.replace(
                "{{ plot_wf_mech }}", os.path.join(self.contentdir, "plot_wf_mech.png")
            )
            line = line.replace("{{ table_wf_mech }}", _table_wf_mech)
            line = line.replace(
                "{{ plot_MMK }}", os.path.join(self.contentdir, "plot_MMK.png")
            )
            line = line.replace("{{ table_MMK }}", _table_wf_mech)

            _report.append(line)

        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("\n".join(_report))
        return self.filename

    def open_in_browser(self):
        """
        Open the html report in the webbrowser
        """
        if not os.path.isfile(self.filename):
            raise Exception('No html report available. Use the ".create()" before')
        else:
            import webbrowser

            webbrowser.open(self.filename)


def export_xlsx(fname, data):
    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "layout"
    worksheet["A1"] = "Windinglayout"
    worksheet["A1"].font = Font(size=14)
    for slot in range(data.machinedata["Q"]):
        cell = worksheet.cell(row=2, column=slot + 2, value=slot + 1)
        cell.alignment = Alignment(horizontal="center")
    worksheet["A2"] = "slot No."
    worksheet["A2"].alignment = Alignment(horizontal="right")

    num_layers = data.get_num_layers()
    for layer in range(num_layers):
        worksheet.cell(row=3 + layer, column=1, value=f"Layer {layer + 1}")

    _, layer_slots, layer_colors = data.get_layers()
    for layer in range(np.shape(layer_slots)[0]):
        for slot in range(np.shape(layer_slots)[1]):
            cell = worksheet.cell(
                row=3 + layer,
                column=2 + slot,
                value=layer_slots[layer, slot],
            )
            color = str(layer_colors[layer, slot]).lstrip("#")
            cell.fill = PatternFill(fill_type="solid", fgColor=f"FF{color.upper()}")
            cell.alignment = Alignment(horizontal="center")

    worksheet.column_dimensions["A"].width = 15
    for column in range(2, data.machinedata["Q"] + 2):
        column_letter = worksheet.cell(row=1, column=column).column_letter
        worksheet.column_dimensions[column_letter].width = 4.5

    row = 3 + num_layers + 2
    turns = data.machinedata["turns"]
    if isinstance(turns, list):
        cell = worksheet.cell(row=row, column=1, value="Number of turns")
        cell.font = Font(size=14)
        row += 1
        for layer in range(num_layers):
            worksheet.cell(row=row + layer, column=1, value=f"Layer {layer + 1}")

        for phase_index, phase in enumerate(data.machinedata["phases"]):
            color = get_phase_color(phase_index).lstrip("#")
            fill = PatternFill(fill_type="solid", fgColor=f"FF{color.upper()}")
            for layer_index, layer in enumerate(phase):
                for coil_side_index, coil_side in enumerate(layer):
                    value = turns[phase_index][layer_index][coil_side_index]
                    cell = worksheet.cell(
                        row=row + layer_index,
                        column=1 + abs(coil_side),
                        value=value,
                    )
                    cell.fill = fill
                    cell.alignment = Alignment(horizontal="center")
        row += num_layers
    else:
        worksheet.cell(row=row, column=1, value="Number of turns")
        worksheet.cell(row=row, column=2, value=turns)
    row += 2

    cell = worksheet.cell(row=row, column=1, value="slot number per phase")
    cell.font = Font(size=14)
    row += 1
    for phase_index, phase in enumerate(data.machinedata["phases"]):
        for layer_index, layer in enumerate(phase):
            worksheet.cell(
                row=row,
                column=1,
                value=f"Phase {phase_index + 1} layer {layer_index + 1}",
            )
            for slot_index, slot in enumerate(layer):
                cell = worksheet.cell(row=row, column=slot_index + 2, value=slot)
                cell.alignment = Alignment(horizontal="center")
            row += 1

    worksheet = workbook.create_sheet("phasors")
    worksheet["A1"] = "Voltage phasors"
    worksheet["A1"].font = Font(size=14)
    max_row = 0
    for frequency_index, phase_phasors in enumerate(data.results["Ei_el"]):
        row = max_row + 2
        worksheet.cell(
            row=row + 1,
            column=1,
            value=f"nu = {data.results['nu_el'][frequency_index]}",
        )
        row += 1
        column_offset = 0
        for phase_index, phasors in enumerate(phase_phasors):
            worksheet.cell(
                row=row + 1,
                column=column_offset + 1,
                value=f"Phase{phase_index + 1}_real",
            )
            worksheet.cell(
                row=row + 1,
                column=column_offset + 2,
                value=f"Phase{phase_index + 1}_imag",
            )
            for phasor_index, phasor in enumerate(phasors):
                worksheet.cell(
                    row=row + 2 + phasor_index,
                    column=column_offset + 1,
                    value=float(phasor.real),
                )
                worksheet.cell(
                    row=row + 2 + phasor_index,
                    column=column_offset + 2,
                    value=float(phasor.imag),
                )
            max_row = max(max_row, row + len(phasors))
            column_offset += 2

    for sheet_name, title, get_winding_factor in (
        (
            "Winding_factor_el)",
            "Winding factor (electrical)",
            data.get_windingfactor_el,
        ),
        (
            "Winding_factor_mech)",
            "Winding factor (mechanical)",
            data.get_windingfactor_mech,
        ),
    ):
        worksheet = workbook.create_sheet(sheet_name)
        worksheet["A1"] = title
        worksheet["A1"].font = Font(size=14)
        worksheet.cell(row=3, column=1, value="nu")
        for phase in range(data.get_num_phases()):
            worksheet.cell(row=3, column=phase + 2, value=f"phase{phase + 1}")

        nu, winding_factor = get_winding_factor()
        for index, value in enumerate(nu, start=4):
            worksheet.cell(row=index, column=1, value=float(value))
        for phase in range(data.get_num_phases()):
            for index, value in enumerate(winding_factor[:, phase], start=4):
                worksheet.cell(row=index, column=phase + 2, value=float(value))

    workbook.save(fname)


class TextReport:
    def __init__(self, data):
        """
        Class for creating Text reports of the winding

        Parameters
        ----------
        data :   datamodel object
                 winding model for creating the report
        """
        self.data = data
        self._txt = []

    def create(self):
        self._txt.append("TITLE")
        self._txt.append("=====")
        self._txt.append(self.data.get_title())
        self._txt.append("\n")

        self._txt.append("NOTES")
        self._txt.append("=====")
        self._txt.append(self.data.get_notes())
        self._txt.append("\n")

        self._txt.append("MACHINE DATA")
        self._txt.append("============")
        self._txt.append(f"Number of slots        Q: {self.data.get_num_slots()}")
        self._txt.append(f"Number of pole pairs   p: {self.data.get_num_polepairs()}")
        self._txt.append(f"Number of phases       m: {self.data.get_num_phases()}")
        self._txt.append(f"Number of layers      NL: {self.data.get_num_layers()}")
        self._txt.append(f"Number of slots/phase  q: {self.data.get_q()}")
        self._txt.append("\n")

        _, ls, _ = self.data.get_layers()
        self._txt.append("WINDING LAYOUT")
        self._txt.append("==============")
        self._txt.append("Layer_1: " + " | ".join([k for k in ls[0, :]]))
        if self.data.get_num_layers() > 1:
            self._txt.append("Layer_2: " + " | ".join([k for k in ls[1, :]]))
        self._txt.append("\n")

        self._txt.append("COIL CONNECTION (END WINDINGS)")
        self._txt.append("==============================")
        self._txt.append("'from_slot' contains the positive coil sides")
        self._txt.append("'direction': clockwise (1) or counter clockwise (-1)")
        ov = self.data.get_wdg_overhang()
        head = [
            "Phase",
            "from_slot",
            "to_slot",
            "coil_span",
            "direction",
            "from_layer",
            "to_layer",
        ]
        data = []
        for km in range(len(ov)):
            #  print(ov[km])
            for line in ov[km]:
                data.append(
                    [
                        str(km + 1),
                        str(line[0][0]),
                        str(line[0][1]),
                        str(line[1]),
                        str(line[2]),
                        str(line[3][0]),
                        str(line[3][1]),
                    ]
                )
        t = ascii_table2(head, np.array(data).T).split("\n")
        self._txt += t
        self._txt.append("")

        bc, txt = self.data.get_basic_characteristics()
        self._txt.append("WINDING FACTOR")
        self._txt.append("==============")
        self._txt.append("Periodic base winding                  t: {}".format(bc["t"]))
        a_ = [str(i) for i in analyse.Divisors(bc["a"])]
        self._txt.append(
            "Possible parallel winding connections  a: {}".format(", ".join(a_))
        )

        for k in range(len(bc["kw1"])):
            self._txt.append(
                "Fundamental winding factor           kw1: {} (phase{})".format(
                    round(bc["kw1"][k], 3), k + 1
                )
            )
        self._txt.append(
            "Double linked leakage            sigma_d: {} (from MMF)".format(
                round(bc["sigma_d"], 3)
            )
        )
        self._txt.append("\n")

        self._txt.append("Harmonic content of the winding faktor (electrical)")
        self._txt.append(
            "nu_el\t"
            + "\t".join(["kw (" + k + ")" for k in self.data.get_phasenames()])
        )
        nu, kw = self.data.get_windingfactor_el()

        for knu in range(len(nu)):
            kw_ = [num2str(k, 8) for k in kw[knu]]
            self._txt.append(str(nu[knu]) + "\t" + "\t".join(kw_))
        self._txt.append("\n")

        self._txt.append("Harmonic content of the winding faktor (mechanical)")
        self._txt.append(
            "nu_mech\t"
            + "\t".join(["kw (" + k + ")" for k in self.data.get_phasenames()])
        )
        nu, kw = self.data.get_windingfactor_mech()

        for knu in range(len(nu)):
            kw_ = [num2str(k, 8) for k in kw[knu]]
            self._txt.append(str(nu[knu]) + "\t" + "\t".join(kw_))
        self._txt.append("\n")

        self._txt.append("MAGNETO MOTIVE FORCE / MMF")
        self._txt.append("==========================")

        threshold = config["threshold_MMF_harmonics"]
        nu, Cnu, phase = self.data.get_MMF_harmonics(threshold=threshold)
        Cnu_rel = 100 / np.max(Cnu) * Cnu

        self._txt.append(
            "Harmonic content of the MMF (airgap field caused by the winding)"
        )
        self._txt.append(
            f"Harmonics lower than {threshold * 100}% of the max. amplitude are not shown"
        )
        self._txt.append("nu_mech\tA^\tArel in %\tphase in °")

        for knu in range(len(nu)):
            self._txt.append(
                str(nu[knu])
                + "\t"
                + num2str(Cnu[knu])
                + "\t"
                + str(round(Cnu_rel[knu], 1))
                + "\t"
                + str(round(phase[knu] / np.pi * 180, 1))
            )

        self._txt.append("\n")

        self._txt.append("FORCES")
        self._txt.append("======")
        self._txt.append(
            "Cogging torque ordinal numbers for pm-machines: {}, {}, {}, ...".format(
                bc["lcmQP"], bc["lcmQP"] * 2, bc["lcmQP"] * 3
            )
        )
        r_ = [str(i) for i in bc["r"]]
        self._txt.append(
            "The winding leads to radial forces with modes r: {}, ...".format(
                ", ".join(r_)
            )
        )

        #  self._txt.append()

        #  self._txt.append()
        #  self._txt.append()

    def get_report(self):
        if len(self._txt) == 0:
            self.create()
        return "\n".join(self._txt)

    def save(self, fname):
        with open(fname, "w") as f:
            f.write(self.get_report())
