from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import pyqtSlot

from widgets.sliderLabel import SliderLabel


class SliderWidget(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, value=0, minimum=0, maximum=100, name=''):
        super().__init__(parent)
        self._value = None
        self._minimum = minimum
        self._maximum = maximum

        self._defaultValue = value
        self._name = name

        self._layout = QtWidgets.QHBoxLayout()
        self.setLayout(self._layout)

        self._slider = QtWidgets.QSlider(orientation=QtCore.Qt.Orientation.Horizontal, parent=self)
        self._slider.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

        self._spinbox = QtWidgets.QSpinBox(self)
        self._spinbox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        self._spinbox.setMinimumWidth(60)

        self.setValue(value)
        self.setMinimum(minimum)
        self.setMaximum(maximum)

        if name:
            self._label = SliderLabel()
            self._label.setText(name)
            self.setName(name)
            self._label.setBuddy(self._spinbox)
            self._label.resetRequested.connect(self._reset)

        self._spinbox.valueChanged.connect(self.setValue)
        self._slider.valueChanged.connect(self.setValue)

        self._layout.addWidget(self._spinbox)
        self._layout.addWidget(self._slider)

    @pyqtSlot()
    def _reset(self) -> None:
        self.setValue(self._defaultValue)

    def setName(self, name) -> None:
        if name:
            fm = QtGui.QFontMetrics(self._label.font())
            w1 = fm.horizontalAdvance(name)
            w2 = fm.horizontalAdvance('reset?')
            self._label.setMinimumWidth(max(w1, w2))
            self._layout.addWidget(self._label)
            self._label.setText(name)

    @pyqtSlot(int)
    def setValue(self, value) -> None:
        if value == self._value:
            if self._value is None:
                self._defaultValue = value
            return

        self._slider.blockSignals(True)
        self._spinbox.blockSignals(True)

        self._value = value
        self.valueChanged.emit(value)

        self._slider.setValue(value)
        self._spinbox.setValue(value)

        self._slider.blockSignals(False)
        self._spinbox.blockSignals(False)

    def setMinimum(self, minimum) -> None:
        self._slider.setMinimum(minimum)
        self._spinbox.setMinimum(minimum)

        if self._value < minimum:
            self.setValue(minimum)

    def setMaximum(self, maximum) -> None:
        self._slider.setMaximum(maximum)
        self._spinbox.setMaximum(maximum)

        if self._value > maximum:
            self.setValue(maximum)

    @property
    def label(self) -> SliderLabel:
        return self._label

    @property
    def slider(self) -> QtWidgets.QSlider:
        return self._slider

    @property
    def spinbox(self) -> QtWidgets.QSpinBox:
        return self._spinbox

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> int:
        return self._value

    @property
    def maximum(self) -> int:
        return self._maximum

    @property
    def minimum(self) -> int:
        return self._minimum

    @property
    def defaultValue(self) -> int:
        return self._defaultValue
