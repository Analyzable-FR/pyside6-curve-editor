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


from PySide6.QtWidgets import QApplication, QPushButton
import sys
from level_editor import LevelEditor
import cv2
import numpy as np

# Global variable only for the example
img = cv2.imread("test.jpg")


def adjust_image(params):
    global lut
    if params[0] == "Value":
        lut = params[1]


def display():
    global img
    global lut
    img_ = lut.take(img.astype(np.int64))
    cv2.imshow("Test", img_.astype(np.uint8))


def main():
    app = QApplication([])
    widget = LevelEditor()
    widget.levelChanged.connect(adjust_image)
    widget.show()
    button = QPushButton("Display")
    button.pressed.connect(display)
    button.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
