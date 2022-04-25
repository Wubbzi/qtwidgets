import functools
import random
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QKeyCombination, Qt
from PyQt6.QtWidgets import QApplication

# TODO: ability to choose a format for copied color and tooltip. Currently, it's always a hex string.
# TODO: move hover logic out of dragEnter/dragLeave and into focusIn/focusOut events.
# TODO: handle colors with an alpha channel properly. Currently the option is disabled in the color dialog.

MIME_TYPE_COLOR = 'application/x-color'


class ColorButton(QtWidgets.QPushButton):
    """
    A button that shows a color. Originally intended to be used as part of a color swatch.

    Unable to display text.

    ColorButtons can be dragged and dropped onto other ColorButton widgets.
    The dropped color will be set on the other ColorButton.

    Cmd/Ctrl+C copies the hex value of the color beneath the cursor to the clipboard.

    Cmd/Ctrl click to display a color dialog.
    setClickToOpenColorDialog(True) to open the dialog without a modifier.

    A tooltip with the current color is displayed when the mouse hovers over the button.

    the currentColorChanged signal from the colorDialog is emitted when the color is changed in the dialog
    and so is the color of the button. If the dialog is closed with the Cancel button, the previous color is restored.
    """

    colorChanged = QtCore.pyqtSignal(object)

    def __init__(self, text=None, parent=None, color=None):
        super().__init__(text, parent)
        self.setParent(parent)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setProperty('hover', False)
        self.__color = QtGui.QColor(color or (255, 255, 255))
        self.__dragStartPosition = QtCore.QPoint()
        self.__hoverPenColor = QtGui.QColor(200, 30, 0)
        self.__clickToOpen = False
        self.__outlineColor = QtGui.QColorConstants.Svg.black
        if QtWidgets.QApplication.instance().palette().base().color().lightnessF() > 0.5:
            self.__outlineColor = QtGui.QColorConstants.Svg.lightgrey

    def setText(self, text: str) -> None:
        super(ColorButton, self).setText('')

    def setClickToOpen(self, clickToOpen: bool) -> None:
        self.__clickToOpen = clickToOpen

    def isClickToOpen(self) -> bool:
        return self.__clickToOpen

    def sizeHint(self) -> QtCore.QSize:
        super(ColorButton, self).sizeHint()
        return QtCore.QSize(22, 22)

    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        event.accept()
        self.setProperty('hover', True)
        # we're setting focus here so we can use the cursor to target a color to copy in the keyPressEvent
        self.setFocus(QtCore.Qt.FocusReason.MouseFocusReason)
        return super(ColorButton, self).enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        event.accept()
        self.setProperty('hover', False)
        return super(ColorButton, self).leaveEvent(event)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QtGui.QPainter(self)

        option = QtWidgets.QStyleOptionButton()
        option.initFrom(self)
        option.rect = QtCore.QRect(self.rect())
        option.state = QtWidgets.QStyle.StateFlag.State_Raised
        option.features = QtWidgets.QStyleOptionButton.ButtonFeature.Flat

        rect = QtCore.QRectF(
            self.style().subElementRect(
                QtWidgets.QStyle.SubElement.SE_PushButtonContents, option, self
            )
        )

        r, g, b, _ = self.__color.getRgbF()

        pen = QtGui.QPen(self.__outlineColor)
        pen.setCosmetic(True)

        if self.property('hover'):
            pen = QtGui.QPen(self.__hoverPenColor)

        path = QtGui.QPainterPath()
        path.addRect(rect)

        painter.setPen(pen)
        painter.fillPath(path, self.__color)
        painter.drawPath(path)

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.setProperty('hover', False)
        self.update()

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasFormat(MIME_TYPE_COLOR):
            event.acceptProposedAction()
        self.setProperty('hover', True)
        self.update()

    def dropEvent(self, event) -> None:
        if not event.mimeData().hasFormat(MIME_TYPE_COLOR):
            event.ignore()
            return

        event.accept()
        mime = event.mimeData()
        itemData = mime.data(MIME_TYPE_COLOR)
        stream = QtCore.QDataStream(itemData, QtCore.QIODevice.OpenModeFlag.ReadOnly)
        color = QtGui.QColor()
        stream >> color
        event.setDropAction(QtCore.Qt.DropAction.MoveAction)
        self.setColor(color)

    def keyPressEvent(self, event):
        if event.keyCombination() != QKeyCombination(
                Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_C
        ):
            return super().keyPressEvent(event)
        QApplication.clipboard().setText(self.__color.name())
        event.accept()

    def mousePressEvent(self, event) -> None:
        if not event.button() & QtCore.Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        self.__dragStartPosition = event.position() if hasattr('event', 'position') else event.pos()
        self.clicked.emit()

    def mouseMoveEvent(self, event) -> None:
        super().mouseMoveEvent(event)
        pos = event.position() if hasattr('event', 'position') else event.pos()
        if event.buttons() ^ QtCore.Qt.MouseButton.LeftButton:
            return
        delta = QtCore.QPoint(pos - self.__dragStartPosition).manhattanLength()
        if delta >= QtWidgets.QApplication.startDragDistance():
            self.__dragIt()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if self.__clickToOpen or event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            self.__openDialog()
        self.released.emit()

    def __dragIt(self):
        # occasionally, the outline color isn't updated when the drag starts, so update() here to ensure it's gone.
        self.update()

        drag = QtGui.QDrag(self)

        data = QtCore.QByteArray()
        stream = QtCore.QDataStream(data, QtCore.QIODevice.OpenModeFlag.WriteOnly)

        image = QtGui.QImage(self.size(), QtGui.QImage.Format.Format_RGBA8888)
        imageRect = image.rect()
        image.fill(self.__color)

        painter = QtGui.QPainter(image)
        painter.drawImage(imageRect, image)
        painter.setPen(self.__outlineColor)
        painter.end()

        pixmap = QtGui.QPixmap.fromImage(image)

        stream << self.__color
        mimeData = QtCore.QMimeData()
        mimeData.setData(MIME_TYPE_COLOR, data)

        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.exec(QtCore.Qt.DropAction.CopyAction)

    def __openDialog(self) -> None:
        lastColor = self.__color
        color_dialog = QtWidgets.QColorDialog(self.__color)
        color_dialog.move(self.pos())
        color_dialog.currentColorChanged.connect(self.setColor)
        color_dialog.exec()
        if color_dialog.result() & QtWidgets.QColorDialog.DialogCode.Accepted:
            color_dialog.currentColorChanged.emit(color_dialog.selectedColor())
            return
        self.setColor(lastColor)

    def setColor(self, color) -> None:
        # unless the user creates the button with an invalid color, we shouldn't need to do this
        if not color.isValid():
            return
        self.__color = color
        self.colorChanged.emit(self.__color.getRgbF())
        self.setToolTip(self.__color.name())
        self.update()

    @functools.cached_property
    def hoverPen(self) -> QtGui.QColor:
        return self.__hoverPenColor

    @property
    def color(self) -> QtGui.QColor:
        return self.__color


if __name__ == '__main__':
    from layouts.hBoxLayout import HBoxLayout

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    layout = HBoxLayout()
    w = QtWidgets.QWidget()
    w.setLayout(layout)
    for _ in range(10):
        rnd = random.randint
        btn = ColorButton(color=QtGui.QColor(rnd(0, 255), rnd(0, 255), rnd(0, 255)))
        layout.addWidget(btn)

    w.show()
    app.exec()
