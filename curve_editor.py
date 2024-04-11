'''
MIT License

Copyright (c) 2024 Analyzable

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from PySide6.QtWidgets import QGraphicsSceneMouseEvent, QGraphicsRectItem, QGraphicsItem, QGraphicsPathItem, QGraphicsScene, QGraphicsView
from PySide6.QtCore import Signal, QRectF, QPointF, QEvent, Signal, Slot, Qt, QPoint
from PySide6.QtGui import QLinearGradient, QPolygonF, QBrush, QColor, QPainterPath, QPainter, QPen

import numpy as np
from scipy.interpolate import PchipInterpolator, PPoly


class CurveEditor(QGraphicsView):
    """
    A class representing a curve editor that inherits from QGraphicsView.

    """

    splineChanged = Signal(PPoly, tuple)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.NoDrag)
        self.scene.installEventFilter(self)
        self.setMouseTracking(True)

        self.scene.addLine(0, 250, 250, 0, QPen(Qt.DotLine))
        for i in [63, 188, 125]:
            self.scene.addLine(
                i, 0, i, 250, QPen(
                    QColor(
                        0, 0, 0, 100), 1, Qt.DotLine))
            self.scene.addLine(
                0, i, 250, i, QPen(
                    QColor(
                        0, 0, 0, 100), 1, Qt.DotLine))

        self.background = self.scene.addRect(
            0, 0, 250, 250, brush=QBrush(QColor(50, 50, 50, 50)))

        self.path = QGraphicsPathItem(self.background)

        self.points = []
        self.addPoint(QPointF(-1, 250), False)
        self.addPoint(QPointF(125, 125))
        self.addPoint(QPointF(251, 0), False)
        self.drawSpline()

        self.ruler = QGraphicsRectItem(QRectF(0, 255, 250, 5), self.background)
        gradient = QLinearGradient(0, 250, 250, 250)
        gradient.setColorAt(0, QColor(0, 0, 0))
        gradient.setColorAt(1, QColor(255, 255, 255))
        self.ruler.setBrush(QBrush(gradient))
        self.rulerStart = QGraphicsRectItem(QRectF(0, 0, 5, 5), self.ruler)
        self.rulerStart.setPos(0, 255)
        self.rulerStart.setFlags(QGraphicsItem.ItemIsSelectable)
        self.rulerStart.setBrush(QBrush(QColor(255, 255, 255)))
        self.rulerStop = QGraphicsRectItem(QRectF(0, 0, 5, 5), self.ruler)
        self.rulerStop.setPos(245, 255)
        self.rulerStop.setBrush(QBrush(QColor(255, 255, 255)))
        self.rulerStop.setFlags(QGraphicsItem.ItemIsSelectable)

        self.defaultState = self.getState()

    def reset(self):
        """
        Resets the state of the curve editor to the default state.

        Returns:
            None

        """
        self.setState(self.defaultState)

    def setState(self, params):
        """
        Sets the state of the curve editor with the specified parameters.

        Parameters:
            params (tuple): A tuple containing the points and limits to set.

        Returns:
            None

        """
        for i in self.points:
            self.scene.removeItem(i)
        self.points = []
        for i in params[0]:
            self.addPoint(i)
        self.drawSpline()

        self.setLimits(params[1])

    def getState(self):
        """
        Retrieves the current state of the curve editor.

        Returns:
            list: A list of QPointF objects representing the current points.

        """
        return ([i.pos() for i in self.points], self.getLimits())

    def addPoint(self, coord, isMovable=True):
        """
        Adds a point to the graphics scene.

        Parameters:
            coord (tuple): A tuple containing the coordinates (x, y) of the point.
            isMovable (bool, optional): Indicates whether the added point is movable or not.
                Defaults to True.

        Returns:
            None

        """
        point = PointItem(coord, self.background)
        if isMovable:
            point.setFlags(QGraphicsItem.ItemIsMovable)
        self.points.append(point)

    def getSpline(self):
        """
        Computes a spline interpolation based on the points added to the graphics scene.

        Returns:
            PchipInterpolator or None: An PchipInterpolator object representing the spline interpolation
                of the normalized (0, 1) points' coordinates along the x-axis and y-axis, or None if an exception occurs.

        """
        try:
            self.points.sort(key=lambda p: p.x())
            line = PchipInterpolator([i.pos().x() / 250 for i in self.points], [
                i.pos().y() / 250 for i in self.points])
            return line
        except BaseException:
            return None

    def drawSpline(self):
        """
        Draws a spline based on the computed spline interpolation of the points.

        Returns:
            None

        """
        spline = self.getSpline()
        if spline:
            path = QPainterPath(QPointF(0, 250))
            x = np.linspace(0, 1, 250)
            y = np.clip(spline(x), 0, 1)
            for i, j in zip(x, y):
                path.lineTo(i * 250, j * 250)
            self.path.setPath(path)

    def getLimits(self):
        """
        Retrieves the limits of the ruler.

        Returns:
            tuple: A tuple containing the normalized start and end positions of the ruler
            within the range of 0 to 1 relative to the total width of the scene (250 pixels).

        """

        limits = (self.rulerStart.scenePos().x() / 250,
                  (self.rulerStop.scenePos().x() + 5) / 250)
        return limits

    def setLimits(self, limits):
        """
        Sets the limits of the ruler.

        Parameters:
            limits (tuple): A tuple containing the normalized start and end positions of the ruler.

        Returns:
            None

        """
        self.rulerStart.setPos(limits[0] * 250, 255)
        self.rulerStop.setPos(limits[1] * 250 - 5, 255)

    def mouseReleaseEvent(self, event):
        """
        Overrides the mouseReleaseEvent method to clear the selection in the scene after the mouse is released.

        Parameters:
            event (QMouseEvent): The mouse release event object.

        Returns:
            None

        """
        self.scene.clearSelection()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """
        Overrides the mouseMoveEvent function to draw a spline when the left mouse button is pressed and moved.

        Parameters:
            event (QMouseEvent): The mouse event object.

        Returns:
            None

        """
        if event.buttons() == Qt.LeftButton:
            items = self.scene.selectedItems()
            if items:
                if self.scene.selectedItems()[0] == self.rulerStart:
                    xStart = np.clip(
                        self.mapToScene(
                            event.pos()).x(),
                        0,
                        self.rulerStop.pos().x() - 5)
                    self.rulerStart.setPos(
                        xStart, self.rulerStart.pos().y())
                    self.splineChanged.emit(self.getSpline(), self.getLimits())
                elif self.scene.selectedItems()[0] == self.rulerStop:
                    xStop = np.clip(
                        self.mapToScene(
                            event.pos()).x(),
                        self.rulerStart.pos().x() + 5,
                        245)
                    self.rulerStop.setPos(xStop, self.rulerStop.pos().y())
                    self.splineChanged.emit(self.getSpline(), self.getLimits())
            elif self.itemAt(event.pos()) in self.points:
                self.drawSpline()
                self.splineChanged.emit(self.getSpline(), self.getLimits())
        super().mouseMoveEvent(event)

    def eventFilter(self, obj, event):
        """
        Overrides the eventFilter function to handle mouse double-click and mouse move events in the graphics scene.

        Parameters:
            obj: The object being watched for events.
            event (QEvent): The event object.

        Returns:
            bool: True if the event was handled, otherwise returns the value returned by the base class eventFilter.

        """
        if obj is self.scene:
            if event.type() == QEvent.GraphicsSceneMouseDoubleClick and self.background.contains(
                    event.scenePos()):
                self.addPoint(event.scenePos())
                self.drawSpline()
            elif event.type() == QEvent.GraphicsSceneMouseMove and not self.background.contains(event.scenePos()):
                return True
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        """
        Overrides the resizeEvent method to fit the view within the scene's bounding rectangle while maintaining aspect ratio.

        Parameters:
            event (QResizeEvent): The resize event object.

        Returns:
            None

        """
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


class PointItem(QGraphicsItem):
    """
    A class representing a point item in a QGraphicsScene.

    Attributes:
        coord (tuple): A tuple containing the coordinates (x, y) of the point.
        parent (QObject): The parent object for this QGraphicsItem.

    """

    def __init__(self, coord, parent):
        """
        Initializes the PointItem with the given coordinates and parent object.

        Parameters:
            coord (tuple): A tuple containing the coordinates (x, y) of the point.
            parent (QObject): The parent object for this QGraphicsItem.

        Returns:
            None

        """
        super().__init__(parent)
        self.setPos(coord)

    def boundingRect(self):
        """
        Returns the bounding rectangle of the point item.

        Returns:
            QRectF: The bounding rectangle of the point item.

        """
        return QRectF(-5, -5, 10, 10)

    def paint(self, painter, option, widget):
        """
        Paints the point item.

        Parameters:
            painter (QPainter): The QPainter object used for painting.
            option (QStyleOptionGraphicsItem): Style options for the item.
            widget (QWidget): The widget being painted.

        Returns:
            None

        """
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawEllipse(-3, -3, 6, 6)
