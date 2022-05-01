from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QStaticText


class HorizontalDivider(QtWidgets.QWidget):
    def __init__(self, parent=None, name=''):
        super(HorizontalDivider, self).__init__(parent)
        self.__name = name
        self.__label = None
        self.__spacing = None
        self.__labelWidth = 0
        self.__labelHeight = 0

        self.palette = QtWidgets.QApplication.instance().palette()
        self.setSpacing(6)
        self.setName(name)

    @property
    def name(self) -> str:
        return self.__name

    def setName(self, name: str) -> None:
        """The name on the label to the left of the divider."""
        self.__name = name
        self.__label = QStaticText(name)
        self.__label.setText(name)
        self.__calculateSize()

    def label(self) -> QStaticText:
        return self.__label

    def spacing(self) -> int:
        return self.__spacing

    def setSpacing(self, width: int) -> None:
        """Sets the gap width between the divider and text."""
        self.__spacing = width
        self.update()

    def paintEvent(self, event) -> None:
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(self.palette.color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Text), 1)
        painter.setPen(pen)

        cy = self.rect().center().y()
        textPos = QtCore.QPointF(0, cy - int(self.__labelHeight) / 2)
        painter.drawStaticText(textPos, self.__label)

        pen = QtGui.QPen(self.palette.color(QtGui.QPalette.ColorRole.Mid), 1)
        painter.setPen(pen)
        painter.drawLine(self.__labelWidth, cy, self.width(), cy)

    def __calculateSize(self) -> None:
        fm = self.fontMetrics()
        self.__labelHeight = fm.height()
        self.__labelWidth = fm.horizontalAdvance(self.__name) + self.__spacing
        self.setFixedHeight(self.__labelHeight - 1)
        self.update()
