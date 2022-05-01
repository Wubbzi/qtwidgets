from PyQt6 import QtCore, QtGui, QtWidgets


class SliderLabel(QtWidgets.QLabel):
    resetRequested = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(SliderLabel, self).__init__(parent)
        self._name = ""
        self._hovering = False
        self._delay = 250

        self.setParent(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.showResetTextTimer = QtCore.QTimer()
        self.showResetTextTimer.timeout.connect(self.showResetText)
        self.showResetTextTimer.setSingleShot(True)

        self.setToolTip("Click to reset to default value")

    def showResetText(self) -> None:
        self.showResetTextTimer.stop()
        if self._hovering:
            self.setText('reset?')

    def switchText(self) -> None:
        self.setText(self.name)

    def setText(self, name: str) -> None:
        super(SliderLabel, self).setText(name)
        if not self._name:
            self._name = name

    def enterEvent(self, event: QtCore.QEvent.Type.Enter) -> None:
        super(SliderLabel, self).enterEvent(event)
        self._hovering = True
        self.showResetTextTimer.start(self._delay)
        event.accept()

    def leaveEvent(self, event: QtCore.QEvent.Type.Leave) -> None:
        super(SliderLabel, self).leaveEvent(event)
        self._hovering = False
        self.switchText()
        event.accept()

    @property
    def delay(self) -> int:
        return self._delay

    @property
    def name(self) -> str:
        return self._name

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super(SliderLabel, self).mousePressEvent(event)
        if self.text() == 'reset?':
            self.resetRequested.emit()
