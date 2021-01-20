try:
    from TranslationWindow.TranslationWindowUI import Ui_Dialog
except ModuleNotFoundError:
    from TranslationWindowUI import Ui_Dialog
from PyQt5 import QtWidgets, QtCore, QtGui

try:
    import TranslationWindow.Translate as Translate
except ModuleNotFoundError:
    import Translate


class TranslationWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, settings: dict, parent=None, image=None, title=''):
        super(TranslationWindow, self).__init__(parent)
        self.setWindowTitle(title)
        self.setupUi(self)
        self.setupCombos(settings)
        self.imsource = settings['imsource']
        self.inputTextEdit.returnPressed.connect(self.startTextTranslation)
        self.emptyProgressBar()
        self.reverseLanguages.pressed.connect(self.reverseLang)
        if image is not None:
            self.startImageTranslation(image)

    def reverseLang(self):
        src = self.sourceLanguageCombo.currentIndex()
        dest = self.destinationLanguageCombo.currentIndex()
        self.sourceLanguageCombo.setCurrentIndex(dest)
        self.destinationLanguageCombo.setCurrentIndex(src)
        src = self.inputTextEdit.toPlainText()
        dest = self.outputBrowser.toPlainText()
        self.inputTextEdit.setText(dest)
        self.outputBrowser.setText(src)

    def startTextTranslation(self, text):
        self.infiniteProgressBar()
        thread = TranslateThread(text, self.sourceLanguageCombo.currentData(),
                                 self.destinationLanguageCombo.currentData(), self)
        thread.translatingReady.connect(self.showTranslation)
        thread.translatingFailed.connect(self.translationFailed)
        thread.start()

    def startImageTranslation(self, image):
        self.infiniteProgressBar()
        thread = TranslateThread.byImage(image, self.imsource, self.sourceLanguageCombo.currentData(),
                                         self.destinationLanguageCombo.currentData(), self)
        thread.translatingReady.connect(self.showTranslation)
        thread.detectionReady.connect(self.inputTextEdit.setText)
        thread.translatingFailed.connect(self.translationFailed)
        thread.start()

    def showTranslation(self, source, translation, source_language, destination_language):
        self.inputTextEdit.setText(source)
        cursor = self.inputTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.inputTextEdit.setTextCursor(cursor)
        self.outputBrowser.setText(translation)
        cursor = self.outputBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.outputBrowser.setTextCursor(cursor)

        self.sourceLanguageCombo.setCurrentIndex(
            self.sourceLanguageCombo.findData(source_language)
        )
        self.destinationLanguageCombo.setCurrentIndex(
            self.destinationLanguageCombo.findData(destination_language)
        )
        self.emptyProgressBar()

    def translationFailed(self):
        cursor = self.inputTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.inputTextEdit.setTextCursor(cursor)

        self.outputBrowser.setHtml('<p style="color:red">Translation Failed.</p>')
        cursor = self.outputBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.outputBrowser.setTextCursor(cursor)

        self.emptyProgressBar()

    def setupCombos(self, settings):
        for i, (code, lang) in enumerate(Translate.languages.items()):
            self.sourceLanguageCombo.addItem(f'{lang.capitalize()} ({code})')
            self.sourceLanguageCombo.setItemData(i, code)
            self.destinationLanguageCombo.addItem(f'{lang.capitalize()} ({code})')
            self.destinationLanguageCombo.setItemData(i, code)
        self.sourceLanguageCombo.setView(QtWidgets.QListView())
        self.sourceLanguageCombo.setStyleSheet(self.sourceLanguageCombo.styleSheet() + '\n' +
                                               "QListView::item {height:22px;}")
        self.destinationLanguageCombo.setView(QtWidgets.QListView())
        self.destinationLanguageCombo.setStyleSheet(self.destinationLanguageCombo.styleSheet() + '\n' +
                                                    "QListView::item {height:22px;}")
        self.sourceLanguageCombo.setCurrentIndex(
            self.sourceLanguageCombo.findData(settings['source']))
        self.destinationLanguageCombo.setCurrentIndex(
            self.destinationLanguageCombo.findData(settings['dest']))
        self.sourceLanguageCombo.returnPressed.connect(self.inputTextEdit.setFocus)
        self.destinationLanguageCombo.returnPressed.connect(self.inputTextEdit.setFocus)

    def infiniteProgressBar(self):
        self.progressBar.setMaximum(0)
        self.progressBar.setMinimum(0)

    def emptyProgressBar(self):
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)

    def saveSettings(self):
        self.settings.settings = self.editedSettings.settings.copy()
        self.settings.save()


class TranslateThread(QtCore.QThread):
    translatingReady = QtCore.pyqtSignal(str, str, str, str)  # source_text, translation, source_language,
    #   destination_language
    translatingFailed = QtCore.pyqtSignal(Exception)
    detectionReady = QtCore.pyqtSignal(str)  # detected_text

    def __init__(self, text, source, dest, parent=None, image=None, imsource=None):
        super(TranslateThread, self).__init__(parent)
        self.source = source
        self.imsource = imsource
        self.dest = dest
        self.text = text
        self.image = image

    @classmethod
    def byImage(cls, image, imsource, source, dest, parent=None):
        return cls('', source, dest, parent, image, imsource)

    def run(self, p=None) -> None:
        if self.image is None:
            try:
                translation = Translate.TranslateFromText(self.text, self.dest, self.source)
                self.translatingReady.emit(*translation)
            except Exception as e:
                raise e
                self.translatingFailed.emit(e)
        else:
            translation_iter = Translate.TranslateFromImage(self.image, self.dest, self.source, self.imsource)
            source_text = next(translation_iter)
            self.detectionReady.emit(source_text)
            try:
                translation, source_language, destination_language = next(translation_iter)
                self.translatingReady.emit(source_text, translation, source_language, destination_language)
            except Exception as e:
                raise e
                self.translatingFailed.emit(e)


class progressWindow(QtWidgets.QProgressBar):
    """small progress widget"""

    def __init__(self, parent=None):
        super(progressWindow, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(0)
        # self.progression.setMaximumHeight(10)
        self.setStyleSheet("QProgressBar {\n"
                           "    border: 2px solid grey;\n"
                           "    border-radius: 5px;\n"
                           "}\n"
                           "\n"
                           "QProgressBar::chunk {\n"
                           "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(165, "
                           "120, 255, 255), stop:1 rgba(0, 0, 255, 255));\n "
                           "    /*width: 20px;*/\n"
                           "\n"
                           "}\n"
                           "")
        self.setFixedSize(100, 10)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setGeometry(QtGui.QCursor.pos().x(), QtGui.QCursor.pos().y(), self.width(), self.height())
        self.show()


class Line(QtWidgets.QWidget):
    def __init__(self, width, color, parent=None):
        super(Line, self).__init__(parent)
        self.setFixedHeight(width)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Fixed)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        if isinstance(color, str):
            self.setStyleSheet("background-color: " + color)
        else:
            if len(color) == 3:
                self.setStyleSheet("background-color: rgb" + str(tuple(color)))
            elif len(color) == 4:
                self.setStyleSheet("background-color: rgba" + str(tuple(color)))


class draggableFrameLessWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(draggableFrameLessWindow, self).__init__(*args, **kwargs)
        self.oldPos = self.pos()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


class smallTranslationWindow(draggableFrameLessWindow):
    def __init__(self, text, source, dest, parent=None, failed=False):
        super(smallTranslationWindow, self).__init__(parent)
        self.text = text
        # QtWidgets.QMessageBox.warning(self, 'Translation', text)
        p = QtGui.QCursor.pos()
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.mainWidget = QtWidgets.QWidget()
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.mainWidget.setLayout(self.verticalLayout)
        self.xButton = QtWidgets.QPushButton(' X ', self)
        self.xButton.clicked.connect(self.close)
        if not failed:
            self.languageLabel = QtWidgets.QLabel(f'{Translate.languages.get(source.split("-")[0], source).capitalize()} to'
                                                  f' {Translate.languages.get(dest.split("-")[0], dest).capitalize()}',
                                                  self)
        else:
            self.languageLabel = QtWidgets.QLabel(text, self)

        self.xButton.setStyleSheet(
            '''	
            QPushButton {	
                background-color: transparent;	
                border: none;	
                }	
            
            QPushButton:hover{	
                background-color: rgba(150, 150, 150, 230)	
                }	
            
            QPushButton:pressed{	
                background-color: rgba(130, 130, 130, 230)	
                }	
            ''')
        self.horizontalLayout.addWidget(self.xButton)
        self.horizontalLayout.addWidget(self.languageLabel)
        self.horizontalLayout.addStretch()
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.translationLabel = QtWidgets.QLabel(text, self)
        if failed:
            red = 'QLabel {background-color: transparent; color: red;}'
            self.languageLabel.setStyleSheet(red)
            self.translationLabel.setStyleSheet(red)
        else:
            self.languageLabel.setStyleSheet('background-color: transparent')
            self.translationLabel.setStyleSheet('background-color: transparent')

        self.verticalLayout.setAlignment(QtCore.Qt.AlignTop)
        self.l = Line(2, "black", self)
        self.verticalLayout.addWidget(self.l)
        self.verticalLayout.addWidget(self.translationLabel)
        self.setCentralWidget(self.mainWidget)
        self.setStyleSheet('background-color: rgba(210, 210, 210, 230)')
        self.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.setGeometry(QtGui.QCursor.pos().x(), QtGui.QCursor.pos().y(), self.width(), self.height())
        self.show()


class SmallTranslation:
    def __init__(self, settings: dict, image, parent=None):
        """add small progressbar attacked to the mouse"""
        self.image = image
        self.parent = parent
        self.imsource = settings['imsource']
        self.source = settings['source']
        self.dest = settings['dest']
        self.startImageTranslation()

    def startImageTranslation(self):
        self.showProgressBar()
        self.thread = TranslateThread.byImage(self.image, self.imsource, self.source, self.dest, self.parent)
        self.thread.translatingReady.connect(lambda x, y, z: self.showTranslation(x, y, z))
        self.thread.translatingFailed.connect(self.translatingFailed)
        self.thread.start()

    def translatingFailed(self):
        self.hideProgressBar()
        smallTranslationWindow('Translation Failed', '', '', self.parent, True)

    def showTranslation(self, source, translation, source_language):
        self.hideProgressBar()
        smallTranslationWindow(translation, source_language, self.dest, self.parent)

    def showProgressBar(self):
        self.pBar = progressWindow(self.parent)

    def hideProgressBar(self):
        self.pBar.hide()


def small():
    return smallTranslationWindow('translation', 'en', 'he')


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = small()
    sys.exit(app.exec_())