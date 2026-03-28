
import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QColorDialog, QSlider, QFileDialog, QInputDialog
)
from PyQt5.QtGui import QPainter, QPen, QPixmap, QFont
from PyQt5.QtCore import Qt, QPoint, QRect


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 500)

        self.canvas = QPixmap(self.size())
        self.canvas.fill(Qt.white)

        self.last_point = QPoint()
        self.start_point = QPoint()
        self.drawing = False

        self.pen_color = Qt.black
        self.pen_width = 3

        self.eraser_mode = False
        self.shape_mode = None
        self.text_mode = False
        self.text_to_draw = ""

        self.rainbow_mode = False  # UNIQUE FEATURE

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.canvas)

    def resizeEvent(self, event):
        new_canvas = QPixmap(self.size())
        new_canvas.fill(Qt.white)

        painter = QPainter(new_canvas)
        painter.drawPixmap(0, 0, self.canvas)
        self.canvas = new_canvas

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:

            # TEXT MODE
            if self.text_mode and self.text_to_draw:
                painter = QPainter(self.canvas)
                painter.setPen(QPen(self.pen_color))
                font = QFont("Arial", 16)
                painter.setFont(font)
                painter.drawText(event.pos(), self.text_to_draw)

                self.text_mode = False
                self.text_to_draw = ""
                self.update()
                return

            self.drawing = True
            self.start_point = event.pos()
            self.last_point = self.start_point

    def mouseMoveEvent(self, event):
        if self.drawing and self.shape_mode is None:
            painter = QPainter(self.canvas)

            # PEN LOGIC
            if self.eraser_mode:
                pen = QPen(Qt.white, self.pen_width * 2,
                           Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

            elif self.rainbow_mode:
                color = Qt.GlobalColor(random.randint(7, 19))
                pen = QPen(color, self.pen_width,
                           Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

            else:
                pen = QPen(self.pen_color, self.pen_width,
                           Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())

            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            end = event.pos()

            if self.shape_mode:
                painter = QPainter(self.canvas)
                pen = QPen(self.pen_color, self.pen_width)
                painter.setPen(pen)

                rect = QRect(self.start_point, end)

                if self.shape_mode == "rect":
                    painter.drawRect(rect)
                elif self.shape_mode == "circle":
                    painter.drawEllipse(rect)

            self.drawing = False
            self.update()

    def clear(self):
        self.canvas.fill(Qt.white)
        self.update()

    def save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG Files (*.png)"
        )
        if path:
            self.canvas.save(path)


class DrawingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing App")
        self.setGeometry(100, 100, 900, 650)

        self.canvas = Canvas()

        # Buttons
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.canvas.clear)

        eraser_btn = QPushButton("Eraser")
        eraser_btn.clicked.connect(self.toggle_eraser)

        color_btn = QPushButton("Color")
        color_btn.clicked.connect(self.pick_color)

        rect_btn = QPushButton("Rectangle")
        rect_btn.clicked.connect(lambda: self.set_shape("rect"))

        circle_btn = QPushButton("Circle")
        circle_btn.clicked.connect(lambda: self.set_shape("circle"))

        text_btn = QPushButton("Text")
        text_btn.clicked.connect(self.add_text)

        rainbow_btn = QPushButton("Rainbow")
        rainbow_btn.clicked.connect(self.toggle_rainbow)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.canvas.save)

        # Slider
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(20)
        slider.setValue(3)
        slider.valueChanged.connect(self.change_size)

        # Layout
        top = QHBoxLayout()
        for w in [clear_btn, eraser_btn, color_btn, rect_btn,
                  circle_btn, text_btn, rainbow_btn, save_btn, slider]:
            top.addWidget(w)

        main = QVBoxLayout()
        main.addLayout(top)
        main.addWidget(self.canvas)

        self.setLayout(main)

    def toggle_eraser(self):
        self.canvas.eraser_mode = not self.canvas.eraser_mode
        self.canvas.shape_mode = None
        self.canvas.text_mode = False
        self.canvas.rainbow_mode = False

    def toggle_rainbow(self):
        self.canvas.rainbow_mode = not self.canvas.rainbow_mode
        self.canvas.eraser_mode = False
        self.canvas.shape_mode = None
        self.canvas.text_mode = False

    def set_shape(self, shape):
        self.canvas.shape_mode = shape
        self.canvas.eraser_mode = False
        self.canvas.text_mode = False
        self.canvas.rainbow_mode = False

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.pen_color = color
            self.canvas.eraser_mode = False
            self.canvas.text_mode = False
            self.canvas.rainbow_mode = False

    def change_size(self, value):
        self.canvas.pen_width = value

    def add_text(self):
        text, ok = QInputDialog.getText(self, "Enter Text", "Text:")
        if ok and text:
            self.canvas.text_mode = True
            self.canvas.text_to_draw = text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec_())
