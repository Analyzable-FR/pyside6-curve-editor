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

from curve_editor import CurveEditor
import copy
import numpy as np

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, QPushButton
from PySide6.QtCore import Signal


class LevelEditor(QWidget):

    levelChanged = Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.layout = QGridLayout()

        self.channel = QComboBox(self)
        self.channel.addItems(["Value", "Red", "Green", "Blue"])
        self.layout.addWidget(self.channel)
        self.channel.currentIndexChanged.connect(self.changeChannel)
        self.currentChannel = 0

        self.view = CurveEditor(self)
        self.layout.addWidget(self.view)
        self.view.splineChanged.connect(self.viewChanged)

        self.presets = [copy.copy(self.view.defaultState)] * 4

        self.reset = QPushButton(self.tr("Reset"), self)
        self.layout.addWidget(self.reset)
        self.setLayout(self.layout)
        self.reset.pressed.connect(self.view.reset)

    def compute_lut(self, spline, limits, bit=8):
        """
        Computes the look-up table (LUT) based on the spline interpolation and limits.

        Parameters:
            spline (PchipInterpolator): The Pchip spline interpolation.
            limits (tuple): A tuple containing the normalized start and end positions of the ruler.
            bit (int): The bit depth of the LUT. Defaults to 8.

        Returns:
            numpy.ndarray: The computed look-up table.

        """
        lut = np.clip(spline(np.linspace(0, 1, 2**bit)), limits[0], limits[1])
        return (1 - lut) * 2**bit

    def viewChanged(self, spline, limits):
        """
        Emits a signal with the channel name and the computed look-up table when the view changes.

        Parameters:
            spline (PchipInterpolator): The Pchip spline interpolation.
            limits (tuple): A tuple containing the normalized start and end positions of the ruler.

        Returns:
            None

        """
        lut = self.compute_lut(spline, limits)
        self.levelChanged.emit((self.channel.currentText(), lut))

    def changeChannel(self, index):
        """
        Changes the active channel to the specified index.

        Parameters:
            index (int): The index of the channel to switch to.

        Returns:
            None

        """
        self.presets[self.currentChannel] = copy.copy(self.view.getState())
        self.view.setState(self.presets[index])
        self.currentChannel = index
