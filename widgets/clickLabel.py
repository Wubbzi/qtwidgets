from PyQt6 import QtCore, QtWidgets


class ClickLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, text='', parent=None):
        super(ClickLabel, self).__init__(text, parent)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()
