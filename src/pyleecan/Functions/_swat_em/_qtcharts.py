"""Small QtCharts helpers used by the vendored SWAT-EM plots."""

import math
import os

from PySide6 import QtCharts, QtCore, QtGui, QtSvg, QtWidgets

_app = None


def mkQApp():
    global _app
    app = QtWidgets.QApplication.instance()
    if app is None:
        _app = QtWidgets.QApplication([])
        app = _app
    return app


def mkPen(color="k", width=1.0, style=None):
    if isinstance(color, dict):
        options = color
        color = options.get("color", "k")
        width = options.get("width", width)
        style = options.get("style", style)
    pen = QtGui.QPen(QtGui.QColor(color))
    pen.setWidthF(float(width))
    if style is not None:
        pen.setStyle(style)
    return pen


def mkBrush(color):
    return QtGui.QBrush(QtGui.QColor(color))


class _TextItem(QtWidgets.QGraphicsTextItem):
    def __init__(self, text="", anchor=(0, 0)):
        super().__init__()
        self._data_pos = QtCore.QPointF()
        self._anchor = anchor
        self.setPlainText(text)

    def setPos(self, x, y=None):
        if y is None:
            super().setPos(x)
        else:
            self._data_pos = QtCore.QPointF(x, y)

    def setColor(self, color):
        self.setDefaultTextColor(QtGui.QColor(color))

    def update_chart_position(self, chart, series):
        position = chart.mapToPosition(self._data_pos, series)
        rect = self.boundingRect()
        super().setPos(
            position.x() - rect.width() * self._anchor[0],
            position.y() - rect.height() * self._anchor[1],
        )


class _ArrowItem(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, angle=0, headLen=12, pen=None, brush=None):
        super().__init__()
        self._angle = math.radians(angle)
        self._head_len = headLen
        self._data_pos = QtCore.QPointF()
        self.setPen(pen if isinstance(pen, QtGui.QPen) else mkPen(pen or "k"))
        self.setBrush(
            brush if isinstance(brush, QtGui.QBrush) else mkBrush(brush or "k")
        )

    def setPos(self, x, y=None):
        if y is None:
            super().setPos(x)
        else:
            self._data_pos = QtCore.QPointF(x, y)

    def update_chart_position(self, chart, series):
        tip = chart.mapToPosition(self._data_pos, series)
        direction = QtCore.QPointF(math.cos(self._angle), -math.sin(self._angle))
        normal = QtCore.QPointF(-direction.y(), direction.x())
        base = tip - direction * self._head_len
        points = [
            tip,
            base + normal * (self._head_len * 0.45),
            base - normal * (self._head_len * 0.45),
        ]
        self.setPolygon(QtGui.QPolygonF(points))
        super().setPos(0, 0)


class _AreaPolygonItem(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, points, brush=None, pen=None):
        super().__init__()
        self.data_points = [QtCore.QPointF(x, y) for x, y in points]
        self.setBrush(
            brush if isinstance(brush, QtGui.QBrush) else mkBrush(brush or "k")
        )
        self.setPen(
            pen if isinstance(pen, QtGui.QPen) else QtGui.QPen(self.brush().color())
        )

    def update_chart_position(self, chart, series):
        points = [chart.mapToPosition(point, series) for point in self.data_points]
        self.setPolygon(QtGui.QPolygonF(points))
        super().setPos(0, 0)


class _AreaSeries:
    def __init__(self, upper, lower, brush=None):
        points = [(point.x(), point.y()) for point in upper.points()]
        points.extend((point.x(), point.y()) for point in reversed(lower.points()))
        self.graphic = _AreaPolygonItem(points, brush=brush)


class _BarGraphItem:
    def __init__(self, x, height, width, brush=None, pen=None):
        self.graphics = []
        for center, top in zip(x, height):
            left = center - width / 2
            right = center + width / 2
            self.graphics.append(
                _AreaPolygonItem(
                    [(left, 0), (left, top), (right, top), (right, 0)],
                    brush=brush,
                    pen=pen,
                )
            )


def PlotCurveItem(x, y, symbol=None, pen=None, name=None, connect=None):
    color_pen = pen if isinstance(pen, QtGui.QPen) else mkPen(pen or "k")
    if symbol == ".":
        series = QtCharts.QScatterSeries()
        series.setMarkerSize(max(3.0, color_pen.widthF() * 2))
        series.setMarkerShape(QtCharts.QScatterSeries.MarkerShape.MarkerShapeCircle)
        series.setColor(color_pen.color())
    else:
        series = QtCharts.QLineSeries()
        series.setPen(color_pen)
    if name:
        series.setName(name)
    for x_value, y_value in zip(x, y):
        if math.isfinite(float(x_value)) and math.isfinite(float(y_value)):
            series.append(float(x_value), float(y_value))
    return series


class _Legend:
    def __init__(self, chart):
        self._chart = chart

    @property
    def items(self):
        return []

    def removeItem(self, _item):
        return None


class PlotWidget(QtCharts.QChartView):
    def __init__(self, parent=None):
        chart = QtCharts.QChart()
        chart.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("white")))
        chart.setBackgroundRoundness(0)
        chart.legend().setVisible(False)
        super().__init__(chart, parent)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self._axis_x = QtCharts.QValueAxis()
        self._axis_y = QtCharts.QValueAxis()
        self._axis_x.setRange(0, 1)
        self._axis_y.setRange(0, 1)
        chart.addAxis(self._axis_x, QtCore.Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(self._axis_y, QtCore.Qt.AlignmentFlag.AlignLeft)
        self._text_items = []
        self._graphic_items = []
        chart.plotAreaChanged.connect(self._update_graphics)
        self._axis_x.rangeChanged.connect(self._update_graphics)
        self._axis_y.rangeChanged.connect(self._update_graphics)
        self.plotItem = chart

    def addItem(self, item, ignoreBounds=False):
        if isinstance(item, _TextItem):
            item.setParentItem(self.chart())
            self._text_items.append(item)
            self._update_graphics()
        elif isinstance(item, (_ArrowItem, _AreaPolygonItem)):
            item.setParentItem(self.chart())
            self._graphic_items.append(item)
            self._update_graphics()
        elif isinstance(item, _AreaSeries):
            item.graphic.setParentItem(self.chart())
            self._graphic_items.append(item.graphic)
            self._update_graphics()
        elif isinstance(item, _BarGraphItem):
            for graphic in item.graphics:
                graphic.setParentItem(self.chart())
                self._graphic_items.append(graphic)
            self._update_graphics()
        else:
            for series in [item]:
                self.chart().addSeries(series)
                series.attachAxis(self._axis_x)
                series.attachAxis(self._axis_y)

    def _update_graphics(self, *_args):
        series = next(iter(self.chart().series()), None)
        if series is None:
            return
        for item in self._text_items:
            item.update_chart_position(self.chart(), series)
        for item in self._graphic_items:
            item.update_chart_position(self.chart(), series)

    def clear(self):
        for item in self._text_items + self._graphic_items:
            scene = item.scene()
            if scene is not None:
                scene.removeItem(item)
        self._text_items.clear()
        self._graphic_items.clear()
        for series in self.chart().series():
            self.chart().removeSeries(series)

    def setAspectLocked(self, lock=True, ratio=1):
        self._aspect_locked = lock
        self._aspect_ratio = ratio
        self._apply_aspect_lock()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_aspect_lock()

    def _apply_aspect_lock(self):
        if not getattr(self, "_aspect_locked", False) or self.height() <= 0:
            return
        x_center = (self._axis_x.min() + self._axis_x.max()) / 2
        y_center = (self._axis_y.min() + self._axis_y.max()) / 2
        x_span = self._axis_x.max() - self._axis_x.min()
        y_span = self._axis_y.max() - self._axis_y.min()
        target_ratio = self.width() / self.height() / self._aspect_ratio
        if x_span == 0 or y_span == 0 or target_ratio <= 0:
            return
        if x_span / y_span < target_ratio:
            x_span = y_span * target_ratio
            self._axis_x.setRange(x_center - x_span / 2, x_center + x_span / 2)
        else:
            y_span = x_span / target_ratio
            self._axis_y.setRange(y_center - y_span / 2, y_center + y_span / 2)

    def getAxis(self, name):
        return self._axis_x if name == "bottom" else self._axis_y

    def addLegend(self, offset=None):
        self.chart().legend().setVisible(True)
        return _Legend(self.chart())

    def disableAutoRange(self):
        return None

    def setXRange(self, minimum, maximum):
        self._axis_x.setRange(minimum, maximum)
        self._apply_aspect_lock()

    def setYRange(self, minimum, maximum):
        self._axis_y.setRange(minimum, maximum)
        self._apply_aspect_lock()

    def autoRange(self):
        points = []
        for series in self.chart().series():
            if isinstance(series, QtCharts.QAreaSeries):
                points.extend(series.upperSeries().points())
                points.extend(series.lowerSeries().points())
            else:
                points.extend(series.points())
        if not points:
            points = [
                point
                for item in self._graphic_items
                if isinstance(item, _AreaPolygonItem)
                for point in item.data_points
            ]
        if not points:
            return
        x_values = [point.x() for point in points]
        y_values = [point.y() for point in points]
        self._set_padded_range(self._axis_x, min(x_values), max(x_values))
        self._set_padded_range(self._axis_y, min(y_values), max(y_values))
        self._apply_aspect_lock()
        self._update_graphics()

    @staticmethod
    def _set_padded_range(axis, minimum, maximum):
        span = maximum - minimum
        padding = span * 0.05 if span else max(abs(minimum) * 0.05, 0.5)
        axis.setRange(minimum - padding, maximum + padding)

    def setLabel(self, orientation, text):
        axis = self._axis_x if orientation == "bottom" else self._axis_y
        axis.setTitleText(text.replace("<div>", "").replace("</div>", ""))

    def showGrid(self, x=False, y=False):
        self._axis_x.setGridLineVisible(x)
        self._axis_y.setGridLineVisible(y)

    def setLimits(self, xMin=None, xMax=None, yMin=None, yMax=None):
        if xMin is not None:
            self._axis_x.setMin(xMin)
        if xMax is not None:
            self._axis_x.setMax(xMax)
        if yMin is not None:
            self._axis_y.setMin(yMin)
        if yMax is not None:
            self._axis_y.setMax(yMax)

    def save(self, filename, resolution):
        save_widget(self, filename, resolution)


class GraphicsLayoutWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._layout = QtWidgets.QGridLayout(self)
        self.ci = self

    def addPlot(self, row=0, col=0, rowspan=1):
        view = PlotWidget(self)
        self._layout.addWidget(view, row, col, rowspan, 1)
        return view

    def show(self):
        super().show()

    def save(self, filename, resolution):
        save_widget(self, filename, resolution)


TextItem = _TextItem
ArrowItem = _ArrowItem
FillBetweenItem = _AreaSeries
BarGraphItem = _BarGraphItem


def save_widget(widget, filename, resolution):
    app = QtWidgets.QApplication.instance()
    if app is not None:
        app.processEvents()
    width, height = map(int, resolution)
    widget_width = max(widget.width(), 1)
    widget_height = max(widget.height(), 1)
    if os.path.splitext(filename)[-1].lower() == ".svg":
        generator = QtSvg.QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(QtCore.QSize(width, height))
        generator.setViewBox(QtCore.QRect(0, 0, width, height))
        painter = QtGui.QPainter(generator)
        painter.scale(width / widget_width, height / widget_height)
        _render_widget(widget, painter, widget_width, widget_height)
        painter.end()
        return
    pixmap = QtGui.QPixmap(width, height)
    pixmap.fill(QtGui.QColor("white"))
    painter = QtGui.QPainter(pixmap)
    painter.scale(width / widget_width, height / widget_height)
    _render_widget(widget, painter, widget_width, widget_height)
    painter.end()
    pixmap.save(filename)


def _render_widget(widget, painter, width, height):
    if isinstance(widget, QtWidgets.QGraphicsView):
        rect = QtCore.QRect(0, 0, width, height)
        widget.render(painter, rect, rect)
    else:
        widget.render(painter, QtCore.QPoint(0, 0))
