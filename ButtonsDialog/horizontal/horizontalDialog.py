from PyQt5 import QtWidgets, QtCore, QtGui
try:
    import horizontal_icons_rc
except ImportError:
    from ButtonsDialog.horizontal import horizontal_icons_rc


class Button(QtWidgets.QPushButton):
    def __init__(self, icon, hoveredIcon, iconSize, onClick, parent=None):
        super(Button, self).__init__(parent)
        self.regularIcon = QtGui.QIcon(icon)
        self.hoverIcon = QtGui.QIcon(hoveredIcon)
        self.hovered = False
        self.clicked.connect(onClick)
        self.installEventFilter(self)
        self.setIcon(self.regularIcon)

        self.setMaximumWidth(iconSize)
        self.setIconSize(QtCore.QSize(iconSize, iconSize))
        self.setStyleSheet('background-color: transparent; border:none;')

    def eventFilter(self, obj, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.Enter and not self.hovered:
            self.hovered = True
            self.setIcon(self.hoverIcon)
        elif event.type() == QtCore.QEvent.Leave and self.hovered:
            self.hovered = False
            self.setIcon(self.regularIcon)
        return super(Button, self).eventFilter(obj, event)


class horizontalButtonsDialog(QtWidgets.QMainWindow):
    def __init__(self, copyClick, saveClick, printClick, translateClick, parent=None):
        super(horizontalButtonsDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.mainWidget.setLayout(self.horizontalLayout)

        self.scale = 25
        self.setupButtons(copyClick, saveClick, printClick, translateClick)
        self.setStyleSheet('background-color: rgba(220, 220, 220, 230); border-radius: 4px;')

        self.setGeometry(self.x() + 500, self.y() + 500, self.scale * 4, self.scale)

    def setupButtons(self, copyClick, saveClick, printClick, translateClick):
        self.copyButton = Button(':/icons/icons/copy.png', r':/icons/icons/blue copy.png', self.scale,
                                 copyClick, self)
        self.saveButton = Button(':/icons/icons/save.png', r':/icons/icons/blue save.png', self.scale,
                                 saveClick, self)
        self.printButton = Button(':/icons/icons/print.png', r':/icons/icons/blue print.png', self.scale,
                                  printClick, self)

        self.translateButton = QtWidgets.QPushButton('T', self)
        self.translateButton.clicked.connect(translateClick)
        self.translateButton.setMaximumWidth(self.scale)
        self.translateButton.setMinimumSize(QtCore.QSize(self.scale, self.scale))
        self.translateButton.setFont(QtGui.QFont('roboto', self.scale * 0.7))
        self.translateButton.setStyleSheet('QPushButton{'
                                           '    background-color: transparent;'
                                           '    border:none;'
                                           '}'
                                           ''
                                           'QPushButton:hover{'
                                           '    color:rgb(22, 146, 203);'
                                           '}')


        self.horizontalLayout.addWidget(self.copyButton)

        self.horizontalLayout.addWidget(self.saveButton)
        self.horizontalLayout.addWidget(self.printButton)
        self.horizontalLayout.addWidget(self.translateButton)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = horizontalButtonsDialog(
        lambda: print('copy'),
        lambda: print('save'),
        lambda: print('print'),
        lambda: print('translate'),
    )
    win.show()
    sys.exit(app.exec_())
