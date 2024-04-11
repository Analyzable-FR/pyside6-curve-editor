**CurvesWidget README**

---

**Description:**

CurvesWidget is a PySide6 widget designed for level correction of images using a curve. It provides a sophisticated tool for adjusting color, brightness, and contrast by manipulating a curve representing the tonal range of the image. This widget is particularly useful for fine-tuning RGB images.

---

**Features:**

- **Curve Adjustment:** The CurvesWidget allows users to manipulate a curve representing brightness, red, blue, and green levels individually to achieve desired adjustments.

- **Color Correction:** Users can precisely adjust the color balance by modifying the RGB channels independently.

- **Brightness and Contrast:** The widget provides control over brightness and contrast by shaping the curve according to the desired tonal range.

---

**Usage:**

1. **Installation:**
    - Ensure you have PySide6 installed. If not, you can install it via pip:
      ```
      pip install PySide6 opencv-python scipy
      ```

2. **Integration:**
    - Import the CurvesWidget module into your project.
    ```python
    from curves_widget import CurvesWidget
    ```

3. **Initialization:**
    - Create an instance of the CurvesWidget and add it to your GUI layout.
    ```python
    curves_widget = LevelEditor()
    layout.addWidget(curves_widget)
    ```

4. **Usage:**
    - Use the mouse to manipulate the curve by dragging control points. Each point represents a specific tonal range, allowing precise adjustments to brightness, red, blue, and green levels.
    - Double-click anywhere on the curve to add more control points for finer adjustments.

---

**License:**

This project is licensed under the MIT License. See the LICENSE file for details.

---
