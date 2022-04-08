from PyQt6 import QtCore, QtWidgets, sip


class HBoxLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(HBoxLayout, self).__init__(parent)
        self.setParent(parent)

        self.items = []

        self.setSpacing(spacing)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)

    def __del__(self):
        for x in self.items:
            sip.delete(x)

    def addItem(self, item):
        self.items.append(item)

    def insertItem(self, index, item):
        self.items.insert(index, item)

    def insertWidget(self, index, widget):
        self.addChildWidget(widget)
        item = QtWidgets.QWidgetItem(widget)
        self.insertItem(index, item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        return self.items[index] if 0 <= index < len(self.items) else None

    def takeAt(self, index):
        return self.items.pop(index) if 0 <= index < len(self.items) else None

    def expandingDirections(self):
        return QtCore.Qt.Orientation.Horizontal

    def hasHeightForWidth(self):
        return False

    def heightForWidth(self, width=0):
        return width or self.sizeHint().width()

    def setGeometry(self, rect):
        super(HBoxLayout, self).setGeometry(rect)
        self.doLayout(rect, testOnly=False)

    def sizeHint(self):
        l, t, r, b = self.getContentsMargins()
        w = 0
        h = 0
        s = self._spacing
        for item in self.items:
            size = item.sizeHint()
            if h < size.height():
                h = size.height()
            w += size.width()
            if w:
                w += s
        w += l + r
        h += t + b
        return QtCore.QSize(w, h)

    def minimumSize(self):
        l, t, r, b = self.getContentsMargins()
        w = 0
        h = 0
        s = self._spacing
        for item in self.items:
            size = item.minimumSize()
            if h < size.height():
                h = size.height()
            w += size.width()
            if w:
                w += s
        w += l + r
        h += t + b
        return QtCore.QSize(w, h)

    def doLayout(self, rect, testOnly):
        l, t, r, b = self.getContentsMargins()
        x = rect.x() + l
        y = rect.y() + t
        s = self._spacing
        for item in self.items:
            size = item.sizeHint()
            item.setGeometry(QtCore.QRect(x, y, size.width(), rect.height() - t - b))
            x += size.width()
            if x:
                x += s
        return y

    def expandingDirections(self):
        return QtCore.Qt.Orientation.Horizontal

    def setSpacing(self, spacing):
        self._spacing = spacing

    def spacing(self):
        if self._spacing >= 0:
            return self._spacing
        return self.smartSpacing(QtWidgets.QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        return parent.style().pixelMetric(pm, None, parent)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    w = QtWidgets.QWidget()
    layout = HBoxLayout()
    for x in 'Hello World !'.split():
        b = QtWidgets.QLabel(x)
        layout.addWidget(b)
    w.setLayout(layout)
    w.show()
    sys.exit(app.exec())