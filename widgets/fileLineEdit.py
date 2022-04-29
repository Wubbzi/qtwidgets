from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QFile, QUrl, Qt, pyqtSignal


class FileLineEdit(QtWidgets.QWidget):
    fileUrlChanged = pyqtSignal(QUrl)

    def __init__(self, parent=None, isDirectory=False, filter=None):
        super().__init__(parent)
        self.filter = filter
        self.isDirectory = isDirectory

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sizePolicy = (QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setSizePolicy(QtWidgets.QSizePolicy(*sizePolicy))
        self.lineEdit.textEdited.connect(self.textEdited)
        self.lineEdit.textChanged.connect(self.validate)

        colorGroupRole = (QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Text)
        self.validTextColor = self.lineEdit.palette().color(*colorGroupRole)
        self.errorTextColor = QtGui.QColorConstants.Svg.red

        # Focus the lineEdit when the widget gains focus
        self.setFocusProxy(self.lineEdit)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        button = QtWidgets.QToolButton(self)
        button.setText("...")
        button.setAutoRaise(True)
        tipText = 'file directory'.split()
        button.setToolTip(f"Pick a {tipText[1] if self.isDirectory else tipText[0]}")

        layout.addWidget(self.lineEdit)
        layout.addWidget(button)

        button.clicked.connect(self.buttonClicked)
        self.lineEdit.textEdited.connect(self.textEdited)
        self.lineEdit.textChanged.connect(self.validate)

    def buttonClicked(self):
        if self.isDirectory:
            url = QtWidgets.QFileDialog.getExistingDirectoryUrl(self.window(), "Choose a Folder", self.filePath())
        else:
            url = QtWidgets.QFileDialog.getOpenFileUrl(self.window(), "Choose a File", self.filePath(), self.filter)
            if not len(url):
                return
            url = QUrl(url[0])
        if not url:
            self.validate()
            return
        self.setFileUrl(url)
        self.validate()

        self.fileUrlChanged.emit(url)

    def filePath(self):
        path = self.lineEdit.text()
        return QUrl(path)

    def isReadOnly(self):
        return self.lineEdit.isReadOnly()

    def validate(self):
        url = self.filePath()
        textColor = self.validTextColor
        if not url.isValid() or QFile.exists(url.toString(QUrl.UrlFormattingOption.PreferLocalFile)) is False:
            textColor = self.errorTextColor
        palette = self.lineEdit.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Text, textColor)
        self.lineEdit.setPalette(palette)
        self.lineEdit.update()

    def setErrorTextColor(self, color):
        self.errorTextColor = color

    def setFilter(self, filter):
        self.filter = filter

    def setIsDirectory(self, isDirectory):
        self.isDirectory = isDirectory

    def setOkTextColor(self, color):
        self.validTextColor = color

    def setText(self, text):
        self.lineEdit.setText(text)

    def text(self):
        return self.lineEdit.text()

    def setReadOnly(self, readOnly):
        self.lineEdit.setReadOnly(readOnly)

    def setFileUrl(self, url):
        path = url.toString(QUrl.UrlFormattingOption.PreferLocalFile)
        if self.lineEdit.text() != path:
            self.lineEdit.setText(path)

    def focusInEvent(self, e):
        self.lineEdit.event(e)
        if e.reason() in [Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason]:
            self.lineEdit.selectAll()
        super().focusInEvent(e)

    def focusOutEvent(self, e):
        self.lineEdit.event(e)
        super().focusOutEvent(e)

    def keyPressEvent(self, e):
        self.lineEdit.keyPressEvent(e)

    def keyReleaseEvent(self, e):
        self.lineEdit.event(e)

    def textEdited(self):
        self.fileUrlChanged.emit(self.filePath())


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = QtWidgets.QWidget()
    vLayout = QtWidgets.QVBoxLayout()
    widget.setLayout(vLayout)
    fileEdit1 = FileLineEdit()
    fileEdit2 = FileLineEdit(isDirectory=True)
    fileEdit3 = FileLineEdit()
    vLayout.addWidget(fileEdit1)
    vLayout.addWidget(fileEdit2)
    vLayout.addWidget(fileEdit3)
    widget.show()
    app.exec()
