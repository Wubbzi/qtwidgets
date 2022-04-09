import functools
from numbers import Real
from typing import Tuple

from PyQt6 import QtCore, QtGui, QtWidgets

VALID_COLORS = "0123456789abcdef"


class ColorBox(QtWidgets.QWidget):
    """
    A widget to display a color. A tooltip with the color's RGB and HEX values is set.
    the max value is based on the type of the Red channel. int clamps to 255, float clamps to 1.0
    4.0, 255, 255, 255 -> 1.0, 1.0, 1.0, 1.0
    1,4,   0, 255, 255 -> 1, 4, 255, 255
    Hex values should be in the one of the following forms: #RRGGBBAA, #RRGGBB, #RGBA, #RGB
    named colors are also supported: steelblue.
    """

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.red = self.green = self.blue = self.alpha = 0
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
    def setColor(self, red: Real, green: Real, blue: Real, alpha: Real = 1.0) -> None:
        self._color = QtGui.QColor.fromRgbF(*self.clamp(red, green, blue, alpha))
        self._rgb = self._color.getRgbF()
        self.update()

    @setColor.register(int)
    def _(self, red: int, green: int, blue: int, alpha: int = 255) -> None:
        self._color = QtGui.QColor.fromRgb(*self.clamp(red, green, blue, alpha))
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
        num_chars = len(color)

        if color in QtGui.QColor.colorNames():
            self._color = QtGui.QColor(color)
            self._rgb = self._color.getRgb()
            self.update()
            return
        if color[0] != "#" or any(char not in VALID_COLORS for char in color[1:]) or num_chars not in {4, 5, 7, 9}:
            raise ValueError(f"Invalid color string: {color} ")

        if len(color) in {7, 4}:
            self._color = QtGui.QColor(color)
            self._rgb = self._color.getRgb()
            self.update()
            return

        elif num_chars in {9, 5}:
            color = color[1:]
            if num_chars == 5:
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
        super().update()
        if any(isinstance(chan, float) in self._rgb for chan in self._rgb):
            self.red, self.green, self.blue, self.alpha = self._color.getRgbF()
            tooltip = f"R: {self.red:.3f} green: {self.green:.3f}  B: {self.blue:.3f}  A: {self.alpha:.3f}"
        else:
            self.red, self.green, self.blue, self.alpha = self._color.getRgb()
            tooltip = f"R: {self.red} green: {self.green}  B: {self.blue}  A: {self.alpha}"
        self.setToolTip(f"Hex: {self._color.name()}\n{tooltip}")

    @functools.singledispatchmethod
    def clamp(self, red, green, blue, alpha) -> Tuple[int, ...]:
        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))
        alpha = max(0, min(255, alpha))
        return red, green, blue, alpha

    @clamp.register(float)
    def _(self, red: float, green: float, blue: float, alpha: float) -> Tuple[float, ...]:
        red = max(0, min((1, red)))
        green = max(0, min((1, green)))
        blue = max(0, min((1, blue)))
        alpha = max(0, min((1, alpha)))
        return red, green, blue, alpha
