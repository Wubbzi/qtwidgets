import decimal
import functools
import random
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QKeyCombination, Qt
from PyQt6.QtGui import QAction, QActionGroup

# TODO: move hover logic out of dragEnter/dragLeave and into focusIn/focusOut events.
# TODO: handle colors with an alpha channel properly. Currently the option is disabled in the color dialog.

MIME_TYPE_COLOR = 'application/x-color'

decimal.setcontext(decimal.Context(prec=4, rounding=decimal.ROUND_HALF_UP))


class ColorButton(QtWidgets.QPushButton):
    """
    A button that displays a color. Originally intended to be used as part of a color swatch.

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
    colorFormat = 'RGB'

    def __init__(self, text=None, parent=None, color=None, sizeHint=None, outlineColor=None):
        super().__init__(text, parent)

        self.setParent(parent)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.contextMenu = QtWidgets.QMenu(self)
        self.customContextMenuRequested.connect(self.onContextMenu)
        self.addActionsToContextMenu()
        self.__colorString = ''
        self.__color = color or QtGui.QColor('Invalid')
        self.__dragStartPosition = QtCore.QPoint()
        self.__hoverOutlineColor = QtGui.QColor(200, 30, 0)
        self.__clickToOpen = False
        self.__outlineColor = outlineColor or QtGui.QColorConstants.Svg.black
        self.__sizeHintSize = sizeHint or QtCore.QSize(24, 24)

        self.setColor(self.__color)

        if QtWidgets.QApplication.instance().palette().base().color().lightnessF() > 0.5:
            self.__outlineColor = QtGui.QColorConstants.Svg.lightgrey

    def copyColorString(self) -> None:
        """
        Copy the current color string to the clipboard.
        """

        QtWidgets.QApplication.clipboard().setText(self.__colorString)

    def addActionsToContextMenu(self):
        copyAction = QAction('Copy', self)
        copyAction.triggered.connect(self.copyColorString)
        self.contextMenu.addAction(copyAction)

        colorFormatGroup = QActionGroup(self)
        colorFormatMenu = self.contextMenu.addMenu('Value Type')

        for x in "Hex RGB HSL".split():
            a = colorFormatMenu.addAction(x)
            a.setCheckable(True)
            if x == self.colorFormat:
                a.setChecked(True)
            colorFormatGroup.addAction(a)

        colorFormatGroup.triggered.connect(self.onColorFormatChanged)
        colorFormatGroup.setExclusive(True)

    def onContextMenu(self):
        self.setProperty('contextMenuVisible', True)
        center = self.mapToGlobal(self.rect().center())
        self.contextMenu.exec(center)
        self.contextMenu.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setProperty('contextMenuVisible', False)

    def onColorFormatChanged(self, action: QAction):
        text = action.text()
        self.colorFormat = text.lower()
        self.__parseColor()

    def setSizeHint(self, size: QtCore.QSize) -> None:
        self.__sizeHintSize = size

    def setText(self, text: str) -> None:
        super(ColorButton, self).setText('')

    def setClickToOpen(self, clickToOpen: bool) -> None:
        """
        when True, the color dialog is shown when the left mouse button is released.
        """
        self.__clickToOpen = clickToOpen

    def isClickToOpen(self) -> bool:
        return self.__clickToOpen

    def sizeHint(self) -> QtCore.QSize:
        return self.__sizeHintSize

    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        event.accept()
        self.setProperty('hover', True)
        # we're setting focus here so we can use the cursor to target a color to copy in the keyPressEvent
        self.setFocus(QtCore.Qt.FocusReason.MouseFocusReason)
        return super(ColorButton, self).enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        event.accept()
        # make sure we don't leave the button highlighted when the cursor leaves the button
        self.setProperty('hover', False)
        return super(ColorButton, self).leaveEvent(event)

    def paintEvent(self, event) -> None:
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

        pen = QtGui.QPen(self.__outlineColor)
        pen.setCosmetic(True)

        if self.property('hover') or self.property('contextMenuVisible'):
            pen = QtGui.QPen(self.__hoverOutlineColor)
        painter.setPen(pen)

        path = QtGui.QPainterPath()
        path.addRect(rect)

        if self.__color.isValid():
            painter.fillPath(path, self.__color)
        else:
            self.paintErrorBox(painter, path, rect)
        painter.drawPath(path)

    def paintErrorBox(self, painter, path, rect):
        """
        Draw a red outline around the button and paint a red X across the button

        """

        b = QtGui.QBrush(QtGui.QColor(QtGui.QColorConstants.Svg.black))
        # lazy attempt to make a checkerboard pattern
        b.setStyle(QtCore.Qt.BrushStyle.Dense4Pattern)
        painter.fillPath(path, b)
        # define the error color here incase the outline color is changed.
        painter.setPen(QtGui.QPen(QtGui.QColor(QtGui.QColorConstants.Svg.red)))

        if self.property('hover'):
            # if for some reason the red outline and the red X don't standout enough
            # fill the button rect with a translucent red when the cursor is hovering over the button
            b = QtGui.QBrush(QtGui.QColor(QtGui.QColor(255, 0, 0, 40)))
            painter.fillPath(path, b)
        # paint the X
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.topRight(), rect.bottomLeft())

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.setProperty('hover', False)
        self.update()

    def dragEnterEvent(self, event) -> None:
        if not event.mimeData().hasFormat(MIME_TYPE_COLOR):
            return

        event.acceptProposedAction()
        self.setProperty('hover', True)
        self.update()

    def dropEvent(self, event) -> None:
        if not event.mimeData().hasFormat(MIME_TYPE_COLOR):
            event.ignore()
            return

        event.accept()
        color = QtGui.QColor()
        mime = event.mimeData()
        itemData = mime.data(MIME_TYPE_COLOR)
        stream = QtCore.QDataStream(itemData, QtCore.QIODevice.OpenModeFlag.ReadOnly)
        stream >> color

        event.setDropAction(QtCore.Qt.DropAction.MoveAction)
        self.setColor(color)

    def keyPressEvent(self, event):
        if event.keyCombination() != QKeyCombination(
                Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_C
        ):
            return super().keyPressEvent(event)
        event.accept()
        self.copyColorString()

    def mousePressEvent(self, event) -> None:
        if not event.button() & QtCore.Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        self.__dragStartPosition = event.position() if hasattr('event', 'position') else event.pos()
        self.clicked.emit()

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() ^ QtCore.Qt.MouseButton.LeftButton:
            event.ignore()
            return super().mouseMoveEvent(event)

        pos = event.position() if hasattr('event', 'position') else event.pos()
        delta = QtCore.QPoint(pos - self.__dragStartPosition).manhattanLength()
        if delta >= QtWidgets.QApplication.startDragDistance():
            self.__dragIt()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if self.__clickToOpen or event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            self.__openDialog()
        self.released.emit()

    def __dragIt(self):
        if not self.__color.isValid():
            return
        # occasionally, the outline color isn't updated when the drag starts, so update() here to ensure it's gone.

        drag = QtGui.QDrag(self)
        self.update()

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
        colorDialog = QtWidgets.QColorDialog(self.__color)
        colorDialog.move(self.pos())
        colorDialog.currentColorChanged.connect(self.setColor)
        colorDialog.exec()
        if colorDialog.result() & QtWidgets.QColorDialog.DialogCode.Accepted:
            colorDialog.currentColorChanged.emit(colorDialog.selectedColor())
            return
        self.setColor(lastColor)

    def __parseColor(self) -> None:

        # TODO: Is there a way to get the color profile from the system in python without using OCIO?

        """
        Parses a QColor and updates the string used when copying a color to the clipboard and setting the tooltip.
        Called when the color format is changed from the context menu and from setColor()

        Occasionally, one of the values from QColor.getRgb() and QColor.getHsl() would contain
        a value that was off by one according to the Digital Color Meter utility and XScope.
        converting values from getRgbF() and getHslF() to decimal and scaling fixes this issue.

        example:
            hsl(223, 97%, 45%)
            rgb(4, 66, 227)
            #0442E3

        """

        s = ''
        colorFormat = self.colorFormat.lower()
        color = self.__color

        match colorFormat:
            case 'hex':
                s = color.name().upper()
            case 'rgb':
                rgb = color.getRgbF()
                red, green, blue, _ = [decimal.Decimal(c) * 255 for c in rgb]
                s = f'rgb({red:.0f}, {green:.0f}, {blue:.0f}) '
            case 'hsl':
                hsl = color.getHslF()
                h = decimal.Decimal(color.hslHueF()) * 360
                saturation, lightness = [decimal.Decimal(c) * 100 for c in hsl[1:-1]]
                s = f'hsl({h:.0f}, {saturation:.0f}%, {lightness:.0f}%) '

        if self.__colorString == s:
            # nothing to do
            return
        self.__colorString = s
        self.updateToolTip()

    def updateToolTip(self) -> None:
        self.setToolTip(self.__colorString)

    def setColor(self, color) -> None:
        self.__color = color
        self.__parseColor()
        self.update()
        self.colorChanged.emit(color)

    @functools.cached_property
    def hoverOutlineColor(self) -> QtGui.QColor:
        return self.__hoverOutlineColor

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
        btn = ColorButton(color=QtGui.QColor(rnd(0, 255), rnd(0, 255), rnd(0, 255)), sizeHint=QtCore.QSize(30, 30))
        layout.addWidget(btn)
        btn.setClickToOpen(rnd(0, 1))
    btn = ColorButton(sizeHint=QtCore.QSize(30, 30))
    layout.addWidget(btn)
    w.show()
    app.exec()
