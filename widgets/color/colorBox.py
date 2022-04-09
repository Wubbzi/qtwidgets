import functools
import sys
from numbers import Real
from typing import Tuple

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication

VALID_COLORS = "0123456789abcdef"


class ColorBox(QtWidgets.QWidget):
    """
    A widget to display a color. A tooltip with the color's RGB and HEX values is set.
    the max value is based on the type of the Red channel. int clamps to 255, float clamps to 1.0
    4.0, 255, 255, 255 -> 1.0, 1.0, 1.0, 1.0
    1,4,   0, 255, 255 -> 1, 4, 255, 255
    Strings using a hex value should be in the one of the following forms: #RRGGBBAA, #RRGGBB, #RGBA, #RGB
    named colors are also supported: steelblue.
    """

    def __init__(self, parent=None, **kwargs):
        super(ColorBox, self).__init__(parent)
        self.r = self.g = self.b = self.a = 0
        self._rgb = None
        self._rgba = None
        self._hsv = None
        self._hsl = None
        self._color = None
        self._height = kwargs['height'] if 'height' in kwargs else 24
        self._width = kwargs['width'] if 'width' in kwargs else int(self._height * 1.7777)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QtGui.QPalette.ColorRole.Base)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setFixedSize(QtCore.QSize(self._width, self._height))

    @functools.cached_property
    def pen(self) -> QtGui.QPen:
        return QtGui.QPen(QtGui.QColorConstants.Svg.black)

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    @property
    def color(self) -> QtGui.QColor:
        return self._color

    @property
    def rgba(self) -> Tuple[int, ...]:
        return self._rgb

    @property
    def rgb(self) -> Tuple[int, ...]:
        return self._rgb[:3]

    @property
    def hsl(self) -> Tuple[int, ...]:
        return self._color.getHsl()

    @property
    def hsv(self) -> Tuple[int, ...]:
        return self._color.getHsv()

    @functools.singledispatchmethod
    def setColor(self, r: Real, g: Real, b: Real, a: Real = 1.0) -> None:
        self._color = QtGui.QColor.fromRgbF(*self.clamp(r, g, b, a))
        self._rgb = self._color.getRgbF()
        self.update()

    @setColor.register(int)
    def _(self, r: int, g: int, b: int, a: int = 255) -> None:
        self._color = QtGui.QColor.fromRgb(*self.clamp(r, g, b, a))
        self._rgb = self._color.getRgb()
        self.update()

    @setColor.register(QtGui.QColor)
    def _(self, color: QtGui.QColor) -> None:
        self._color = color
        self._rgb = self._color.getRgb()
        self.update()

    @setColor.register(str)
    def _(self, color: str) -> None:
        color = color.lower().strip()
        numChars = len(color)

        if color in QtGui.QColor.colorNames():
            self._color = QtGui.QColor(color)
            self._rgb = self._color.getRgb()
            self.update()
            return

        if color[0] != "#" or any(char not in VALID_COLORS for char in color[1:]) or numChars not in {4, 5, 7, 9}:
            raise ValueError(f"Invalid color string: {color} ")

        if len(color) in {7, 4}:
            self._color = QtGui.QColor(color)
            self._rgb = self._color.getRgb()
            self.update()
            return

        elif numChars in {9, 5}:
            color = color[1:]
            if numChars == 5:
                color = (int(color[0] * 2, 16),
                         int(color[1] * 2, 16),
                         int(color[2] * 2, 16),
                         int(color[3] * 2, 16))
            else:
                color = (int(color[:2], 16),
                         int(color[2:4], 16),
                         int(color[4:6], 16),
                         int(color[6:], 16))

        self._color = QtGui.QColor(*color)
        self._rgb = self._color.getRgb()
        self.update()

    def update(self) -> None:
        super(ColorBox, self).update()
        if any(isinstance(chan, float) in self._rgb for chan in self._rgb):
            self.r, self.g, self.b, self.a = self._color.getRgbF()
            tooltip = f"R: {self.r:.3f}  G: {self.g:.3f}  B: {self.b:.3f}  A: {self.a:.3f}"
        else:
            self.r, self.g, self.b, self.a = self._color.getRgb()
            tooltip = f"R: {self.r}  G: {self.g}  B: {self.b}  A: {self.a}"
        self.setToolTip(f"Hex: {self._color.name()}\n{tooltip}")

    @functools.singledispatchmethod
    def clamp(self, r, g, b, a) -> Tuple[int, ...]:
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        a = max(0, min(255, a))
        return r, g, b, a

    @clamp.register(float)
    def _(self, r: float, g: float, b: float, a: float) -> Tuple[float, ...]:
        r = max(0, min((1, r)))
        g = max(0, min((1, g)))
        b = max(0, min((1, b)))
        a = max(0, min((1, a)))
        print(r, g, b, a)
        return r, g, b, a


app = QApplication(sys.argv)

c = ColorBox()
c.setColor(0.5, 1, 0.5, 0.5)
print(c.rgb)
print(c.rgba)
print(c.hsv)
print(c.hsl)
c.setColor(255, 255, 255, 255)
