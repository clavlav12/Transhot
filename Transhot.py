from PyQt5 import QtWidgets, QtCore, QtGui, QtPrintSupport
from PyQt5.QtGui import QPainter
from collections import namedtuple
from TranslationWindow.Translate import openImage
from structures import QListener, TwoWayDict, Stack, EmptyStackException
from TranslationWindow.TranslationWindow import TranslationWindow, SmallTranslation
from SettingsDialog.SettingsDialog import PreferenceDialog
from ImageUploader.ImageUploaderInterface import UploaderInterface
from ImageUploader.uploader import showUploadedImage
from ButtonsDialog.horizontal import horizontalDialog as horizontalButtonsDialog
from ButtonsDialog.vertical import verticalDialog as verticalButtonsDialog
from ButtonsDialog.vertical import paintButton
try:
    from ISO_converter import ISO_3_TO_2
except ModuleNotFoundError:
    from SettingsDialog.ISO_converter import ISO_3_TO_2
import reasource_rc
import subprocess
import time
import sys
import os

Rect = namedtuple('Rectangle', ['x', 'y', 'w', 'h'])
Point = namedtuple('Point', ['x', 'y'])

appName = 'Transhot'


class Cursors:
    default = 0
    cross = 1
    dragVertically = 2
    dragHorizontally = 3
    dragSlash = 4  # /
    dragBackslash = 5  # \
    move = 6
    paint = 7
    draw = 7


def screen_resolutions():
    screens = []
    for displayNr in range(QtWidgets.QDesktopWidget().screenCount()):
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(displayNr)
        screens.append((sizeObject.width(), sizeObject.height()))
    return screens


def getTopLeft(p1, p2):
    return Point(*(min(p1[i], p2[i]) for i in range(2)))


def getBottomRight(p1, p2):
    return Point(*(max(p1[i], p2[i]) for i in range(2)))


class DisabledShortcutAction(QtWidgets.QAction):
    """Qt Has problem listening to shortcuts when the keyboard layout is not
    Roman characters or print key is pressed. therefore shortcuts are called using
    a third party modules"""

    def trigIfEnabled(self):
        if self.isEnabled():
            self.trigger()

    def event(self, e: QtCore.QEvent) -> bool:
        if e.type() == QtCore.QEvent.Shortcut:
            return True
        else:
            return super(DisabledShortcutAction, self).event(e)


def create_shortcut(window, method, tooltip, *keys):
    action = DisabledShortcutAction(window)
    action.setShortcuts(keys)
    action.triggered.connect(method)
    action.setToolTip(tooltip)
    window.addAction(action)
    return action


class LongOperation(QtCore.QThread):
    def __init__(self, function, parent=None, *args, finished=lambda: None, **kwargs):
        super(LongOperation, self).__init__(parent)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = finished
        self.start()

    def run(self):
        self.function(*self.args, **self.kwargs)
        self.finished()


class Timer:
    def __init__(self, delay, reverse=False):
        self.startingTime = time.time()
        self.delay = delay
        self.reverse = reverse
        self.finished = False

    def calcFinished(self):
        self.finished = time.time() - self.startingTime > self.delay

    def __bool__(self):
        if not self.finished:
            self.calcFinished()
        return self.finished ^ self.reverse


class Main(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(appName)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.doNothing = lambda: None

        screenGeometry = QtWidgets.QApplication.primaryScreen().virtualGeometry()
        self.SCREEN_RESOLUTION = Point(screenGeometry.width(), screenGeometry.height())

        self.setGeometry(0, 0, 0, 0)
        self.setMouseTracking(True)
        screen = QtWidgets.QApplication.primaryScreen()
        self.screenshot = screen.grabWindow(0, 0, 0, *self.SCREEN_RESOLUTION)
        self.resetAction = create_shortcut(self, self.reset, 'Take A Screenshot', QtCore.Qt.Key_Print)
        self.hideAction = create_shortcut(self, self.hide, 'Hide', 'esc')
        self.copyAction = create_shortcut(self, self.copyImage, 'Copy To Clipboard', 'ctrl+c')
        self.translateAction = create_shortcut(self, self.translate, 'Translate', 'ctrl+t')
        self.softTranslation = create_shortcut(self, self.softTranslation, 'Quick Translation', 'ctrl+n')
        self.saveAction = create_shortcut(self, self.saveImage, 'Save', 'ctrl+s')
        self.quickSaveAction = create_shortcut(self, lambda: LongOperation(self.quickSave, self), 'quick save', 'ctrl+shift+s')
        self.saveOpenAction = create_shortcut(self, self.saveAndOpen, 'Save & Open', 'ctrl+r')
        self.printAction = create_shortcut(self, self.printImage, 'print', 'ctrl+p')
        self.uploadImageShortcut = create_shortcut(self, self.uploadImage, 'Upload Screenshot', 'ctrl+U')
        self.uploadImageToGoogleShortcut = create_shortcut(self, lambda: self.uploadImage(True), 'Search Screenshot '
                                                                                                 'in google', 'ctrl+G')
        self.openSettings = create_shortcut(self, lambda: self.openPreferenceDialog() if not self.isHidden()
        else None, 'Open Settings Page', 'ctrl+j')
        self.undo = create_shortcut(self, lambda: self.label.drawer.undo(), 'Undo Drawing', 'ctrl+z')
        self.redo = create_shortcut(self, lambda: self.label.drawer.redo(), 'Redo Drawing', 'ctrl+Y')

        self.busy = False  # another window is already active
        self.listener = QListener(self)
        self.listener.start()
        self.trans = QtCore.QTranslator(self)

        self.defaultSettings = {
            'dest': 'he',
            'source': 'auto',
            'imsource': [],
            'saves': 'saves\\'
        }
        self.settingsDatabase = PreferenceDialog.initiateSettingsDatabase(self.defaultSettings)

        # the settings are read from file and may be corrupted
        if self.settingsDatabase.get_setting('dest') not in ISO_3_TO_2:
            self.settingsDatabase.update_setting('dest', self.defaultSettings['dest'])
        if self.settingsDatabase.get_setting('source') not in ISO_3_TO_2:
            self.settingsDatabase.update_setting('source', self.defaultSettings['dest'])
        if not os.path.isdir(self.settingsDatabase.get_setting('saves')):
            self.settingsDatabase.update_setting('saves', self.defaultSettings['saves'])
        self.settingsDatabase.save_changes()

        self.defaultShortcuts = PreferenceDialog.windowActionsToDict(self)

        PreferenceDialog.loadSavedActions(self)

        self.preferenceDialog = None
        self.reloadActions()

        self.icon = SystemTrayIcon(self, app)
        self.setUpIcon()

        self.readyToUpload = False
        self.interface = UploaderInterface(lambda: print("fail"), lambda: None, self.setReady, None)
        self.interface.connect()

        self.horizontalButtons = horizontalButtonsDialog.horizontalButtonsDialog(
            self.copyAction.trigger,
            self.saveAction.trigger,
            self.printAction.trigger,
            self.softTranslation.trigger,
            self
        )
        self.verticalButtons = verticalButtonsDialog.verticalButtonsDialog(
            self.openSettings.trigger,
            self.uploadImageShortcut.trigger,
            self.uploadImageToGoogleShortcut.trigger,
            lambda: self.label.toggleDrawing(),
            lambda: None,
            self
        )

        self.verticalButtons.show()
        self.horizontalButtons.show()
        self.verticalButtons.hide()
        self.horizontalButtons.hide()

        self.label = CaptureLabel(self.SCREEN_RESOLUTION, self.verticalButtons.paintButton,
                                  self.screenshot, self)
        self.setCentralWidget(self.label)

        self.saveDelay = .5  # delay between fast save

    def reloadActions(self):
        self.listener.reset_hotkeys()
        for action in self.actions():
            try:
                self.listener.add_hotkey(action.shortcut(), action.trigIfEnabled)
            except ValueError:
                pass

    def uploadImage(self, to_google=False):
        if self.isHidden():
            return
        if (not self.readyToUpload) and not to_google:
            print("beep")
            QtWidgets.QApplication.beep()
        else:
            self.uploader = showUploadedImage(self.interface, self.getCroppedScreenShot(),
                                              self.SCREEN_RESOLUTION, self, to_google)
            self.uploader.show()
            self.hide()

    def setReady(self):
        self.readyToUpload = True

    def debug(self):
        pass

    def setUpIcon(self):
        self.icon.show()
        self.icon.showMessage(appName, appName + ' is listening', self.icon.icon())

    def hide(self):
        self.verticalButtons.hide()
        self.horizontalButtons.hide()
        self.unsetCursor()
        return super(Main, self).hide()

    def openPreferenceDialog(self):
        if self.busy:
            return
        self.busy = True
        self.unsetCursor()
        self.preferenceDialog = PreferenceDialog(self, self.defaultShortcuts,
                                                 self.defaultSettings,
                                                 settingsDBPath=self.settingsDatabase.path,
                                                 listener=self.listener,
                                                 icon=self.icon.icon())
        self.preferenceDialog.actionsChanged.connect(self.reloadActions)
        self.preferenceDialog.show()
        self.preferenceDialog.finished.connect(lambda: self.setBusy(False))

    def setBusy(self, value):
        self.busy = value

    def change_language(self, file):  # '' for english, eng-lang for another language
        self.trans.load(file)
        QtWidgets.QApplication.instance().installTranslator(self.trans)

    def reset(self):
        if self.busy or self.isVisible() or not self.icon.currentlyActive:  # and self.actionEditor.isHidden()):
            return
        self.crossCursor = QtGui.QCursor(QtGui.QPixmap(r':icon/images/blackbg-cross-corsur.png'))
        screen = QtWidgets.QApplication.primaryScreen()
        self.screenshot = screen.grabWindow(0, 0, 0, *self.SCREEN_RESOLUTION)
        self.label.deleteLater()
        self.label = CaptureLabel(self.SCREEN_RESOLUTION, self.verticalButtons.paintButton,
                                  self.screenshot, self)
        self.label.AOISelected.connect(self.showButtons)
        self.label.AOIRemoved.connect(self.hideButtons)

        self.moving = None  # moving the AOI if it is already selected
        self.selecting = False  # choosing AOI
        self.draggingUp = False
        self.draggingDown = False
        self.draggingRight = False
        self.draggingLeft = False
        self.show()
        self.update()

    def showButtons(self):

        self.updateButtonsPosition()
        self.verticalButtons.show()
        self.horizontalButtons.show()

    def hideButtons(self):
        self.verticalButtons.hide()
        self.horizontalButtons.hide()

    def updateButtonsPosition(self):
        bottomright = getBottomRight(self.label.pos1, self.label.pos2)
        self.ButtonsDistance = 15
        self.verticalButtons.setGeometry(bottomright[0] + self.ButtonsDistance,
                                         bottomright[1] - self.verticalButtons.height(),
                                         self.verticalButtons.width(),
                                         self.verticalButtons.height())

        self.horizontalButtons.setGeometry(bottomright[0] - self.horizontalButtons.width(),
                                           bottomright[1] + self.ButtonsDistance,
                                           self.horizontalButtons.width(),
                                           self.horizontalButtons.height())

        self.boundOnScreen(self.verticalButtons, self.SCREEN_RESOLUTION)
        self.boundOnScreen(self.horizontalButtons, self.SCREEN_RESOLUTION)

    @classmethod
    def boundOnScreen(cls, widget: QtWidgets.QWidget, screenResolution: Point):
        """
        x less than 0: move right to 0
        x greater than resolution - width: move left to resolution - width

        y less than 0: move down to zero
        y greater than resolution - height: move up to resolution - height

        :param widget:  widget to bound in screen
        :param screenResolution:  resolution of the used screen
        """

        x = cls.ceil(widget.x(), 0, screenResolution[0] - widget.width())
        y = cls.ceil(widget.y(), 0, screenResolution[1] - widget.height())
        widget.setGeometry(x, y, widget.width(), widget.height())

    @staticmethod
    def ceil(num, val1, val2):
        min_, max_ = sorted([val1, val2])
        if num > max_:
            return max_
        elif num < min_:
            return min_
        return num

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def copyImage(self):
        if self.isHidden():
            return
        self.icon.showMessage(appName, 'Screenshot was copied to clipboard', self.icon.icon())
        QtWidgets.QApplication.clipboard().setPixmap(self.getCroppedScreenShot())
        self.hide()

    def quickSave(self):
        if self.busy:
            return

        self.busy = True

        settings_dir = self.settingsDatabase.get_setting('saves')
        if not os.path.isdir(settings_dir):
            settings_dir = 'saves'

        self.lastPath = self.getSavedFilePath(settings_dir)

        screen = QtWidgets.QApplication.primaryScreen()
        get_screenshot = {
            True: self.getCroppedScreenShot,
            False: lambda: screen.grabWindow(0, 0, 0, *self.SCREEN_RESOLUTION)

        }

        shot = get_screenshot[self.isVisible()]()

        saved = shot.save(self.lastPath)
        if not saved:  # no permissions to save there
            self.lastPath = self.getSavedFilePath(self.defaultSettings['saves'])
            shot.save(self.lastPath)

        self.hide()
        self.icon.showMessage(appName, f'Screenshot was saved to {os.path.basename(self.lastPath)}. '
                                       f'Click here to open directory', self.icon.icon())
        self.icon.messageClicked.connect(self.openSavedFile)

        self.busy = Timer(self.saveDelay, reverse=True)
        return self.lastPath

    @staticmethod
    def getSavedFilePath(folder):
        n = 0
        path = folder + f'\\screenshot_{n}.png'
        while os.path.isfile(path):
            n += 1
            path = folder + f'\\screenshot_{n}.png'
        return os.path.normpath(path)

    def openSavedFile(self):
        if sys.platform == 'win32':
            print("opening ", self.lastPath, os.path.exists(self.lastPath))
            subprocess.Popen([r'explorer', '/select,', self.lastPath], shell=True)

        elif sys.platform == 'darwin':
            subprocess.Popen(['open', "--", self.lastPath])

        else:
            try:
                subprocess.Popen(['xdg-open', "--", self.lastPath])
            except OSError:
                print("weird os. pass")
        self.icon.messageClicked.disconnect(self.openSavedFile)

    def saveImage(self):
        if self.isHidden() or self.busy:
            return
        self.busy = True

        path = QtWidgets.QFileDialog.getSaveFileName(self, r"Save File",
                                                     r"untitled.png",
                                                     r"Images (*.png *.jpg *.bpm)")[0]
        if path:
            self.hide()
            self.getCroppedScreenShot().save(path)
            self.lastPath = os.path.normpath(path)
            self.icon.showMessage(appName, f'Screenshot was saved to {os.path.basename(self.lastPath)}. '
                                           f'Click here to open directory', self.icon.icon())
            self.getCroppedScreenShot().save(self.lastPath)
            self.icon.messageClicked.connect(self.openSavedFile)

        self.busy = False
        return path

    def saveAndOpen(self):
        if self.isHidden() or self.busy:
            return
        self.busy = True
        path = self.saveImage()
        if path:
            openImage(path)
            self.hide()
            self.icon.showMessage(appName, 'Screenshot was saved', self.icon.icon())
        self.busy = False

    def printImage(self):
        """Prints the current diagram"""
        if self.isHidden() or self.busy:
            return
        self.busy = True
        # Create the printer
        printerobject = QtPrintSupport.QPrinter(0)
        # Set the settings
        printdialog = QtPrintSupport.QPrintDialog(printerobject)
        if printdialog.exec_() == QtWidgets.QDialog.Accepted:
            # Print
            pixmapImage = self.getCroppedScreenShot()
            painter = QtGui.QPainter(printerobject)
            painter.drawPixmap(0, 0, pixmapImage)
            del painter
            self.icon.showMessage(appName, 'Screenshot was printed', self.icon.icon())
        self.busy = False
        self.hide()

    def getCroppedScreenShot(self):
        return self.label.getCroppedScreenShot()

    def translate(self):
        if self.isHidden() or self.busy:
            return
        self.busy = True
        self.unsetCursor()
        t = TranslationWindow(self.settingsDatabase.get_settings(), self, self.getCroppedScreenShot(), title=appName)
        self.hide()
        t.exec_()
        self.busy = False

    def softTranslation(self):
        """Open a small window with the translated text in it.
        open progress widget
        get text with thread
        open small translation window
        """
        if self.isHidden() or self.busy:
            return
        SmallTranslation(self.settingsDatabase.get_settings(), self.getCroppedScreenShot(), self)
        self.hide()

    def closeEvent(self, event):
        self.unsetCursor()

    def unsetCursor(self):
        self.label.unsetCursor()
        return super(Main, self).unsetCursor()


class Drawer:
    def __init__(self, getColor, screenshot, parent, offset):
        self.getColor = getColor
        self.parent = parent
        self.offset = offset
        self.resetDrawing(screenshot, offset)

    def resetDrawing(self, screenshot: QtGui.QPixmap, offset: QtCore.QPoint):
        """Called every time the user creates a new AOI."""
        self.image = screenshot.toImage()
        self.offset = offset
        self.drawing = False  # drawing right now
        self.ableToDraw = False  # can drow (is the draw button pressed?)
        self.previousImages = Stack(self.image.copy())
        self.nextImages = Stack()
        self.brushSize = 2
        self.startingPoint = None
        self.lastPoint = QtCore.QPoint()

    def undo(self):
        try:
            self.nextImages.push(self.image.copy())
            self.image = self.previousImages.pop()
            self.parent.repaint()
        except EmptyStackException:
            pass

    def redo(self):
        try:
            old = self.image.copy()
            self.image = self.nextImages.pop().copy()
            self.previousImages.push(old)
            self.parent.repaint()
        except EmptyStackException:
            pass

    def setDrawing(self, value: bool):
        self.drawing = value

    def setAbleToDraw(self, value: bool):
        self.ableToDraw = value

    def startDrawing(self, position):
        if self.ableToDraw:
            self.startingPoint = position
            self.previousImages.push(self.image.copy())
            self.nextImages.clear()
            self.drawing = True
            self.lastPoint = position - self.offset

    def keepDrawing(self, position):
        if self.drawing and self.ableToDraw:
            painter = QPainter(self.image)
            painter.setPen(QtGui.QPen(self.getColor(), self.brushSize, QtCore.Qt.SolidLine,
                                      QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            if self.startingPoint == position:
                painter.setBrush(self.getColor())
                painter.drawEllipse(position - self.offset, self.brushSize, self.brushSize)
            else:
                painter.drawLine(self.lastPoint, position - self.offset)
            self.lastPoint = position - self.offset
            self.parent.update()

    def stopDrawing(self, position):
        if self.startingPoint == position:
            self.keepDrawing(position)  # draw a circle
        self.drawing = False
        self.startingPoint = None

    def drawingNow(self):
        return self.drawing and self.ableToDraw


class myMouseEvent(QtGui.QMouseEvent):

    def __init__(self, *args, **kwargs):
        super(myMouseEvent, self).__init__(*args, **kwargs)
        self.overriddenPosition = None

    def setPosition(self, pos):
        self.overriddenPosition = pos

    def pos(self):
        if self.overriddenPosition is not None:
            return self.overriddenPosition
        return super(myMouseEvent, self).pos()


class mouseToolTip(QtWidgets.QMainWindow):
    def __init__(self, toolTip, parent):
        super(mouseToolTip, self).__init__(parent=parent)
        self.offset = (0, 20)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(QtCore.Qt.WindowTransparentForInput)

        self.mainWidget = QtWidgets.QLabel(self)
        self.mainWidget.setObjectName("mainWidget")
        self.setStyleSheet("QWidget#TimeVolumeDisplay{background: transparent}")
        self.mainWidget.setStyleSheet("""
            QWidget#mainWidget{
                    background-color: rgba(255, 255, 255, 255);
                    border: 1px solid rgba(118, 118, 118, 255);
                }

            QLabel{
                    background-color: transparent;
                    color: rgba(0a, 0, 0, 255);
                }
                """
                                      )

        self.mainWidget.setText(toolTip)

        font = QtGui.QFont()
        fontMetrics = QtGui.QFontMetrics(font)
        self.mainWidget.setFont(font)
        pixelsWide = fontMetrics.width(self.mainWidget.text()) + 6
        pixelsHigh = fontMetrics.height() + 6

        self.mainWidget.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.mainWidget.setAlignment(QtCore.Qt.AlignCenter)

        self.mainWidget.setFixedWidth(pixelsWide)
        self.mainWidget.setFixedHeight(pixelsHigh)

    def moveToCursor(self):
        self.setGeometry(QtGui.QCursor.pos().x() + self.offset[0],
                         QtGui.QCursor.pos().y() + self.offset[1],
                         self.width(), self.height())


class CaptureLabel(QtWidgets.QLabel):
    DRAG_MARGIN = 5
    AOIRemoved = QtCore.pyqtSignal()
    AOISelected = QtCore.pyqtSignal()

    def __init__(self, screenResolution: Point, colorWidget: paintButton, screenshot, parent=None):
        super(CaptureLabel, self).__init__(parent)
        self.pos1 = [0, 0]
        self.pos2 = [0, 0]

        self.screenshot = screenshot
        self.setGeometry(0, 0, screenResolution[0], screenResolution[1])
        self.setPixmap(self.screenshot)

        self.moving = None  # moving the AOI if it is already selected
        self.selecting = False  # choosing AOI
        self.draggingUp = False
        self.draggingDown = False
        self.draggingRight = False
        self.draggingLeft = False
        self.choseAOI = False
        self.crossCursor = QtGui.QCursor(QtGui.QPixmap(r':icon/images/blackbg-cross-corsur.png'))

        self.SCREEN_RESOLUTION = screenResolution
        self.firstChosen = False
        self.setMouseTracking(True)
        self.mouseToolTip = mouseToolTip('Choose An Area', self)

        # hand-drawing:
        self.colorWidget = colorWidget
        self.colorWidget.colorChanged.connect(self.drawColorChanged)
        self.colorWidget.colorChanged.connect(self.startDrawing)
        self.drawer = Drawer(self.brushColor, self.screenshot, self, QtCore.QPoint(0, 0))

        self.AOIRemoved.connect(self.onAOIRemove)
        self.AOISelected.connect(self.onAOISelect)

        self.drawMat = self.colorWidget.convertQPixmapToMat(
            QtGui.QPixmap(r':icon/images/paint cursor white.png')
        )

        self.currentCursor = Cursors.default
        self.cursorSet = {
            Cursors.cross: self.crossCursor,
            Cursors.dragVertically: QtCore.Qt.SizeVerCursor,
            Cursors.dragHorizontally: QtCore.Qt.SizeHorCursor,
            Cursors.dragSlash: QtCore.Qt.SizeBDiagCursor,
            Cursors.dragBackslash: QtCore.Qt.SizeFDiagCursor,
            Cursors.move: QtCore.Qt.SizeAllCursor,
            Cursors.draw: self.getDrawCursor
        }

        self.mouseToolTip.moveToCursor()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        if not self.firstChosen:
            self.mouseToolTip.moveToCursor()
            self.effSetCursor(Cursors.cross)
            self.mouseToolTip.show()
        super(CaptureLabel, self).showEvent(a0)

    def hideEvent(self, a0: QtGui.QHideEvent):
        if self.mouseToolTip.isVisible():
            self.mouseToolTip.hide()
        if self.drawer.ableToDraw:
            self.colorWidget.click()
        super(CaptureLabel, self).hideEvent(a0)

    def getDrawCursor(self):
        color = self.brushColor().getRgb()
        if len(color) == 4:  # remove alpha channel
            color = color[:-1]
        return QtGui.QCursor(self.colorWidget.tintImage(self.drawMat, color))

    def drawColorChanged(self):
        if self.drawer.ableToDraw:
            self.effSetCursor(Cursors.draw, True)

    def effSetCursor(self, cursor, changeAnyway=False):
        if (not cursor == self.currentCursor) or changeAnyway:
            new = self.cursorSet[cursor]
            if callable(new):
                new = new()
            self.setCursor(new)
            self.currentCursor = cursor

    def unsetCursor(self) -> None:
        self.currentCursor = Cursors.default
        return super(CaptureLabel, self).unsetCursor()

    def toggleDrawing(self):
        self.drawer.ableToDraw = not self.drawer.ableToDraw

    def startDrawing(self):
        self.drawer.ableToDraw = True

    def stopDrawing(self):
        self.drawer.ableToDraw = False

    def onAOIRemove(self):
        self.choseAOI = False

    def onAOISelect(self):
        self.choseAOI = True

        empty = QtGui.QPixmap(*self.getCroppedSize())
        empty.fill(QtCore.Qt.transparent)
        self.drawer.resetDrawing(empty, QtCore.QPoint(
            *getTopLeft(self.pos1, self.pos2)))

    def brushColor(self):
        return self.colorWidget.currentColor()

    def getCroppedScreenShot(self):
        width = abs(self.pos2[0] - self.pos1[0])
        height = abs(self.pos2[1] - self.pos1[1])
        topleft = getTopLeft(self.pos1, self.pos2)

        copy = self.screenshot.copy(*topleft, width, height)
        canvasPainter = QPainter(copy)
        canvasPainter.drawImage(QtCore.QPoint(0, 0), self.drawer.image)
        canvasPainter.end()

        return copy

    def getCroppedSize(self):
        width = abs(self.pos2[0] - self.pos1[0])
        height = abs(self.pos2[1] - self.pos1[1])
        return width, height

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.drawer.drawing:
            self.drawer.stopDrawing(event.pos())
        elif not self.drawer.ableToDraw:
            self.selecting = False
            if self.moving:
                self.moving = None
            elif self.isDragging():
                self.draggingDown = self.draggingUp = self.draggingRight = self.draggingLeft = False
            else:
                self.pos2[0], self.pos2[1] = event.pos().x(), event.pos().y()
                self.update()
            self.AOISelected.emit()
        return super(CaptureLabel, self).mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        x, y = event.pos().x(), event.pos().y()
        topleft = getTopLeft(self.pos1, self.pos2)
        bottomright = getBottomRight(self.pos1, self.pos2)

        if self.drawer.ableToDraw:
            if event.button() == QtCore.Qt.RightButton:
                position = QtCore.QPoint(0, 0)
                pressEvent = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,
                                               position,
                                               QtCore.Qt.RightButton,
                                               QtCore.Qt.RightButton,
                                               QtCore.Qt.NoModifier
                                               )
                releaseEvent = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
                                                 position,
                                                 QtCore.Qt.RightButton,
                                                 QtCore.Qt.RightButton,
                                                 QtCore.Qt.NoModifier
                                                 )
                self.colorWidget.mousePressEvent(pressEvent)
                self.colorWidget.mouseReleaseEvent(releaseEvent)
            else:
                self.drawer.startDrawing(event.pos())
                self.effSetCursor(Cursors.draw)
        else:
            if not self.firstChosen:
                self.mouseToolTip.hide()
            self.selecting = True
            self.firstChosen = True

            self.updateDraggingStatus(x, y)

            if not self.isDragging():
                if (topleft[0] < x < bottomright[0]) and (
                        topleft[1] < y < bottomright[1]):  # mouse inside rect, drag it
                    self.moving = x, y  # initial position
                else:  # new rect
                    self.pos1[0], self.pos1[1] = x, y

            self.AOIRemoved.emit()
        return super(CaptureLabel, self).mousePressEvent(event)

    def updateDraggingStatus(self, x, y):
        self.draggingDown, self.draggingUp, self.draggingLeft, self.draggingRight = self.getDraggingStatus(x, y)

    def getDraggingStatus(self, x, y):
        topleft = getTopLeft(self.pos1, self.pos2)
        bottomright = getBottomRight(self.pos1, self.pos2)

        draggingDown = (topleft[0] - self.DRAG_MARGIN < x < bottomright[0] + self.DRAG_MARGIN) and \
                       (bottomright[1] - self.DRAG_MARGIN < y < bottomright[1] + self.DRAG_MARGIN)
        draggingUp = (topleft[0] - self.DRAG_MARGIN < x < bottomright[0] + self.DRAG_MARGIN) and \
                     (topleft[1] - self.DRAG_MARGIN < y < topleft[1] + self.DRAG_MARGIN)
        draggingLeft = (topleft[0] - self.DRAG_MARGIN < x < topleft[0] + self.DRAG_MARGIN) and \
                       (topleft[1] - self.DRAG_MARGIN < y < bottomright[1] + self.DRAG_MARGIN)
        draggingRight = (bottomright[0] - self.DRAG_MARGIN < x < bottomright[0] + self.DRAG_MARGIN) and \
                        (topleft[1] - self.DRAG_MARGIN < y < bottomright[1] + self.DRAG_MARGIN)

        return draggingDown, draggingUp, draggingLeft, draggingRight

    def setDraggingIcon(self, x, y):
        draggingDown, draggingUp, draggingLeft, draggingRight = self.getDraggingStatus(x, y)
        if (draggingRight and draggingUp) or (draggingLeft and draggingDown):
            self.effSetCursor(Cursors.dragSlash)
        elif (draggingRight and draggingDown) or (draggingLeft and draggingUp):
            self.effSetCursor(Cursors.dragBackslash)
        elif draggingLeft or draggingRight:
            self.effSetCursor(Cursors.dragHorizontally)
        elif draggingUp or draggingDown:
            self.effSetCursor(Cursors.dragVertically)

    def updateRectSize(self, x, y):
        topleft = getTopLeft(self.pos1, self.pos2)
        bottomright = getBottomRight(self.pos1, self.pos2)
        if self.drawer.ableToDraw:
            self.effSetCursor(Cursors.draw)
        else:
            if not self.isDragging():  # has own mouse icons
                if (topleft[0] < x < bottomright[0]) and (topleft[1] < y < bottomright[1]):  # mouse inside rect
                    self.effSetCursor(Cursors.move)
                else:
                    self.effSetCursor(Cursors.cross)
            self.setDraggingIcon(x, y)

        if self.draggingUp:
            highestPoint = min(self.pos1, self.pos2, key=lambda pos: pos[1])
            lowestPoint = max(self.pos1, self.pos2, key=lambda pos: pos[1])
            if lowestPoint[1] > y:
                highestPoint[1] = y
            else:  # cursor is under the lowest point
                self.draggingDown = True
                self.draggingUp = False

        elif self.draggingDown:
            lowestPoint = max(self.pos1, self.pos2, key=lambda pos: pos[1])
            highestPoint = min(self.pos1, self.pos2, key=lambda pos: pos[1])
            if highestPoint[1] < y:
                lowestPoint[1] = y
            else:  # switch
                self.draggingDown = False
                self.draggingUp = True

        if self.draggingRight:
            rightestPoint = max(self.pos1, self.pos2, key=lambda pos: pos[0])
            leftestPoint = min(self.pos1, self.pos2, key=lambda pos: pos[0])
            if x > leftestPoint[0]:
                rightestPoint[0] = x
            else:
                self.draggingLeft = True
                self.draggingRight = False

        elif self.draggingLeft:
            leftestPoint = min(self.pos1, self.pos2, key=lambda pos: pos[0])
            rightestPoint = max(self.pos1, self.pos2, key=lambda pos: pos[0])
            if x < rightestPoint[0]:
                leftestPoint[0] = x
            else:
                self.draggingRight = True
                self.draggingLeft = False

    def mouseMoveEvent(self, event):
        if self.drawer.drawing:
            self.drawer.keepDrawing(event.pos())
        else:
            x, y = event.pos().x(), event.pos().y()

            if not self.firstChosen:  # no area has been selected yet, show tool tip
                self.mouseToolTip.moveToCursor()

            self.updateRectSize(x, y)  # dragging

            if not self.isDragging():
                if self.moving:  # moving the already made AOI
                    if (0 < self.pos1[0] + x - self.moving[0] < self.SCREEN_RESOLUTION.x and
                            0 < self.pos2[0] + x - self.moving[0] < self.SCREEN_RESOLUTION.x):
                        self.pos1[0] += x - self.moving[0]
                        self.pos2[0] += x - self.moving[0]
                    if (0 < self.pos1[1] + y - self.moving[1] < self.SCREEN_RESOLUTION.y and
                            0 < self.pos2[1] + y - self.moving[1] < self.SCREEN_RESOLUTION.y):
                        self.pos1[1] += y - self.moving[1]
                        self.pos2[1] += y - self.moving[1]
                    self.moving = x, y

                elif self.selecting:  # selecting AOI
                    self.pos2[0], self.pos2[1] = x, y

        val = super(CaptureLabel, self).mouseMoveEvent(event)
        self.update()
        return val

    def regulatePosition(self):
        self.pos1[0] = min(max(0, self.pos1[0]), self.SCREEN_RESOLUTION[0])
        self.pos2[0] = min(max(0, self.pos2[0]), self.SCREEN_RESOLUTION[0])
        self.pos1[1] = min(max(0, self.pos1[1]), self.SCREEN_RESOLUTION[1])
        self.pos2[1] = min(max(0, self.pos2[1]), self.SCREEN_RESOLUTION[1])

    def setDrawing(self, value: bool):
        self.drawing = value

    def updatePos1(self, pos):
        self.pos1 = pos

    def updatePos2(self, pos):
        self.pos2 = pos

    def paintEvent(self, event):
        super(CaptureLabel, self).paintEvent(event)

        if self.choseAOI:
            canvasPainter = QPainter(self)
            canvasPainter.drawImage(QtCore.QRect(
                QtCore.QPoint(*getTopLeft(self.pos1, self.pos2)),
                QtCore.QPoint(*getBottomRight(self.pos1, self.pos2))
            ),
                self.drawer.image, self.drawer.image.rect())
            canvasPainter.end()
        self.darkSurrounding()

    def darkSurrounding(self):
        width = self.pos2[0] - self.pos1[0]
        height = self.pos2[1] - self.pos1[1]

        qp = QPainter()
        qp.begin(self)
        pen = QtGui.QPen(QtCore.Qt.DashLine)
        pen.setColor(QtCore.Qt.white)
        qp.setPen(pen)
        qp.drawRect(self.pos1[0], self.pos1[1], width, height)

        pen.setColor(QtCore.Qt.black)
        pen.setDashOffset(2)
        qp.setPen(pen)
        qp.drawRect(self.pos1[0], self.pos1[1], width, height)

        qp.end()

        # dark background
        qp = QPainter()
        qp.begin(self)

        topleft = getTopLeft(self.pos1, self.pos2)
        height = abs(height)
        width = abs(width)
        darken_rects = (
            Rect(0, 0, self.SCREEN_RESOLUTION.x, topleft.y),
            Rect(0, topleft.y, topleft.x, height),
            Rect(topleft.x + width, topleft.y, self.SCREEN_RESOLUTION.x - (topleft.x + width), height),
            Rect(0, topleft.y + height, self.SCREEN_RESOLUTION.x, self.SCREEN_RESOLUTION.y - (topleft.y + height))
        )

        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(brush)
        for rect in darken_rects:
            qp.drawRect(*rect)

    def isDragging(self):
        return self.draggingDown or self.draggingLeft or self.draggingRight or self.draggingUp


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, mainWindow: Main, parent=None):

        self.currentlyActive = True
        self.activeIcon = QtGui.QIcon(r":icon\images\Tray Icon\gray active.png")
        self.inactiveIcon = QtGui.QIcon(r":icon\images\Tray Icon\gray inactive.png")

        super(SystemTrayIcon, self).__init__(self.activeIcon, parent)

        menu = QtWidgets.QMenu()

        screenshotAction = menu.addAction("Take A Screenshot")
        screenshotAction.triggered.connect(mainWindow.resetAction.trigger)

        optionAction = menu.addAction("Options")
        optionAction.triggered.connect(mainWindow.openPreferenceDialog)

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(QtCore.QCoreApplication.quit)

        self.setContextMenu(menu)

        self.mainWindow = mainWindow
        self.activated.connect(self.active)

    def active(self, reason):
        if reason == 3:  # left click
            self.currentlyActive = not self.currentlyActive
            if self.currentlyActive:
                self.setIcon(self.activeIcon)
            else:
                self.setIcon(self.inactiveIcon)


if __name__ == '__main__':
    from PyQt5 import QtCore, QtWidgets

    lockfile = QtCore.QLockFile(QtCore.QDir.tempPath() + f'/{appName}.lock')

    if lockfile.tryLock(100):  # run only once!
        app = QtWidgets.QApplication(sys.argv)
        main = Main()
        app.setQuitOnLastWindowClosed(False)
        sys.exit(app.exec_())
    else:
        print('app is already running')

