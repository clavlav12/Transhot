from PyQt5 import QtWidgets, QtCore, QtGui
try:
    import vertical_icons_rc
except ImportError:
    from ButtonsDialog.vertical import vertical_icons_rc
import numpy as np
import cv2
from time import time


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


class ColorDialog(QtWidgets.QColorDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOptions(self.options() | QtWidgets.QColorDialog.DontUseNativeDialog)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.hidden = []

        self.expandButtonText = ['Expand >>>', 'Reduce <<<']
        self.expandButton = QtWidgets.QPushButton('Expand >>>', self)
        self.expandButton.setMaximumWidth(250)
        self.expandButton.clicked.connect(self.
                                          showHideHidden)
        self.layout().addWidget(self.expandButton)
        # self.setGeometry(self.x(), self.y(), 1, 1)
        for children in self.findChildren(QtWidgets.QWidget):
            classname = children.metaObject().className()
            # print(classname)
            if classname == "QDialogButtonBox":
                self.layout().removeWidget(children)
                self.layout().addWidget(children, alignment=QtCore.Qt.AlignLeft)

            elif classname not in ("QLabel", "QWellArray", "QPushButton"):
                children.hide()
                self.hidden.append(children)

    def showHideHidden(self):
        self.expandButton.setText(self.expandButtonText[
                                      (self.expandButtonText.index(self.expandButton.text()) + 1) % 2])
        for widget in self.hidden:
            widget.setVisible(widget.isHidden())

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        for children in self.findChildren(QtWidgets.QWidget):
            classname = children.metaObject().className()
            if classname == 'QPushButton':
                self.expandButton.setMaximumWidth(children.width())
                break
        return super(ColorDialog, self).resizeEvent(a0)


class paintButton(Button):
    rightClick = QtCore.pyqtSignal()
    colorChanged = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, regularIcon, hoveredIcon, iconSize, onClick, onRightClick, parent=None):
        super(paintButton, self).__init__(regularIcon, hoveredIcon, iconSize, onClick, parent)
        self.holdingRight = False
        self.rightClick.connect(onRightClick)
        self.rightClick.connect(self.openColorDialog)
        self.color = QtGui.QColor('#FFFFFF')
        self.iconMat = self.convertQPixmapToMat(QtGui.QPixmap(regularIcon))

        self.blockSignals(True)
        self.setColor((255, 0, 0))
        self.blockSignals(False)

        self.setCheckable(True)
        self.setStyleSheet(
            """
            QPushButton{
                background-color: transparent; border:none;
            }

            QPushButton::checked {
                background-color: rgba(0, 0, 0, 40);
            }
            """
        )

    def currentColor(self):
        return self.color

    def openColorDialog(self):
        dialog = ColorDialog()
        ok = dialog.exec_()
        if ok:
            color = dialog.currentColor().getRgb()
            if len(color) == 4:
                color = color[:-1]
            self.color = QtGui.QColor(*color)
            self.colorChanged.emit(dialog.currentColor())
            LongOperation(self.setColor, self, color)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.RightButton:
            self.holdingRight = True
        return super(paintButton, self).mousePressEvent(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.RightButton:
            if self.holdingRight and self.hitButton(QMouseEvent.pos()):
                self.rightClick.emit()
            self.holdingRight = False
        return super(paintButton, self).mouseReleaseEvent(QMouseEvent)

    def setColor(self, *color: tuple):
        if len(color) == 1:
            color = color[0]

        if len(color) == 4:
            color = color[:-1]

        # cv2.waitKey(0)
        self.color = QtGui.QColor(*color)

        pxMap = self.tintImage(self.iconMat, color)
        self.regularIcon = QtGui.QIcon(pxMap)
        self.setIcon(self.regularIcon)

    @staticmethod
    def tintImage(cvSource: np.array, color) -> QtGui.QPixmap:
        cvImg = (cvSource * np.array([*color, 255]) / 255).astype(np.uint8)
        height, width, channel = cvImg.shape
        bytesPerLine = 4 * width
        qImg = QtGui.QImage(cvImg.data, width, height, bytesPerLine, QtGui.QImage.Format_RGBA8888)
        return QtGui.QPixmap(qImg)

    @staticmethod
    def convertQPixmapToMat(incomingImage: QtGui.QPixmap):
        """ Converts a QImage into an opencv MAT format  """

        incomingImage = incomingImage.toImage().convertToFormat(QtGui.QImage.Format_RGBA8888)

        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  # Copies the data

        return arr


class verticalButtonsDialog(QtWidgets.QMainWindow):
    def __init__(self, settingsClick, uploadClick, googleClick, paintLeftClick, paintRightClick, parent=None):
        super(verticalButtonsDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.mainWidget.setLayout(self.verticalLayout)

        self.scale = 25
        self.setupButtons(settingsClick, uploadClick, googleClick, paintLeftClick, paintRightClick)
        self.setStyleSheet('background-color: rgba(220, 220, 220, 230); border-radius: 4px;')

        self.setGeometry(self.x() + 500, self.y() + 500, self.scale, self.scale * 4)
        # self.repaint()

    def setupButtons(self, settingsClick, uploadClick, googleClick, paintLeftClick, paintRightClick):
        self.settingsButton = Button(':/icons/icons/gear.png', r':/icons/icons/blue gear.png', self.scale,
                                     settingsClick, self)
        self.uploadButton = Button(':/icons/icons/export.png', r':/icons/icons/blue export.png', self.scale,
                                   uploadClick, self)
        self.googleButton = Button(':/icons/icons/google.png', r':/icons/icons/blue google.png', self.scale,
                                   googleClick, self)
        self.paintButton = paintButton(':/icons/icons/paint.png', r':/icons/icons/blue paint.png', self.scale,
                                       paintLeftClick, paintRightClick, self)

        self.verticalLayout.addWidget(self.uploadButton)
        self.verticalLayout.addWidget(self.paintButton)
        self.verticalLayout.addWidget(self.settingsButton)
        self.verticalLayout.addWidget(self.googleButton)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)


class LongOperation(QtCore.QThread):
    def __init__(self, function, parent=None, *args, **kwargs):
        super(LongOperation, self).__init__(parent)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.start()

    def run(self):
        self.function(*self.args, **self.kwargs)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = verticalButtonsDialog(
        lambda: print('settings'),
        lambda: print('upload'),
        lambda: print('google'),
        lambda: print('paint left'),
        lambda: print('paint right')
    )
    win.show()
    sys.exit(app.exec_())
