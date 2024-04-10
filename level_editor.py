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

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, QPushButton


class LevelEditor(QWidget):

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
        self.presets = [copy.copy(self.view.defaultState)] * 4

        self.reset = QPushButton(self.tr("Reset"), self)
        self.layout.addWidget(self.reset)
        self.setLayout(self.layout)
        self.reset.pressed.connect(self.view.reset)

    def changeChannel(self, index):
        self.presets[self.currentChannel] = copy.copy(self.view.getState())
        self.view.setState(self.presets[index])
        self.currentChannel = index
