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
from PySide6.QtWidgets import QGraphicsSceneMouseEvent, QGraphicsRectItem, QGraphicsItem, QGraphicsPathItem, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QApplication, QWidget, QScrollArea, QLabel
from PySide6.QtCore import QRectF, QPointF, QEvent, Signal, Slot, Qt, QPoint
from PySide6.QtGui import QLinearGradient, QPolygonF, QBrush, QColor, QPainterPath, QImage, QPixmap, QFont, QPainter, QPen, QCursor, QKeySequence
from scipy.interpolate import CubicSpline, Akima1DInterpolator
import numpy as np


class CurveEditor(QGraphicsView):
    """
    A class representing a curve editor that inherits from QGraphicsView.

    """

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.NoDrag)
        self.scene.installEventFilter(self)
        self.setMouseTracking(True)

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
        gradient.setColorAt(0, QColor(255, 255, 255))
        gradient.setColorAt(1, QColor(0, 0, 0))
        self.ruler.setBrush(QBrush(gradient))
        self.ruler_start = QGraphicsRectItem(QRectF(0, 0, 5, 5), self.ruler)
        self.ruler_start.setPos(0, 255)
        self.ruler_start.setFlags(QGraphicsItem.ItemIsSelectable)
        self.ruler_start.setBrush(QBrush(QColor(255, 255, 255)))
        self.ruler_stop = QGraphicsRectItem(QRectF(0, 0, 5, 5), self.ruler)
        self.ruler_stop.setPos(245, 255)
        self.ruler_stop.setBrush(QBrush(QColor(255, 255, 255)))
        self.ruler_stop.setFlags(QGraphicsItem.ItemIsSelectable)

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
        Computes an Akima spline interpolation based on the points added to the graphics scene.

        Returns:
            Akima1DInterpolator or None: An Akima1DInterpolator object representing the spline interpolation
                of the normalized (0, 1) points' coordinates along the x-axis and y-axis, or None if an exception occurs.

        """
        try:
            self.points.sort(key=lambda p: p.x())
            line = Akima1DInterpolator([i.pos().x() / 250 for i in self.points], [
                                       i.pos().y() / 250 for i in self.points])
            return line
        except BaseException:
            return None

    def drawSpline(self):
        """
        Draws a spline based on the computed Akima spline interpolation of the points.

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
        return (self.ruler_start.scenePos().x() / 250,
                (self.ruler_stop.scenePos().x() + 5) / 250)

    def mouseMoveEvent(self, event):
        """
        Overrides the mouseMoveEvent function to draw a spline when the left mouse button is pressed and moved.

        Parameters:
            event (QMouseEvent): The mouse event object.

        Returns:
            None

        """
        if event.buttons() == Qt.LeftButton:
            self.drawSpline()
            items = self.scene.selectedItems()
            if items:
                if self.scene.selectedItems()[0] == self.ruler_start:
                    x_start = np.clip(
                        self.mapToScene(
                            event.pos()).x(),
                        0,
                        self.ruler_stop.pos().x() - 5)
                    self.ruler_start.setPos(
                        x_start, self.ruler_start.pos().y())
                elif self.scene.selectedItems()[0] == self.ruler_stop:
                    x_stop = np.clip(
                        self.mapToScene(
                            event.pos()).x(),
                        self.ruler_start.pos().x() + 5,
                        245)
                    self.ruler_stop.setPos(x_stop, self.ruler_stop.pos().y())
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
        painter.drawEllipse(-5, -5, 10, 10)