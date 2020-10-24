try:
    from ISO_converter import ENGLISH_3, TESSERACT_CODES, ISO_639_3
    from LanguageInsertionWidgetUI import Ui_LanguagesInsertionWidget
except ModuleNotFoundError:
    from SettingsDialog.ISO_converter import ENGLISH_3, TESSERACT_CODES, ISO_639_3
    from SettingsDialog.LanguageInsertionWidgetUI import Ui_LanguagesInsertionWidget
from PyQt5 import QtWidgets, QtCore


class LanguageInsertion(QtWidgets.QWidget, Ui_LanguagesInsertionWidget):
    cleared = QtCore.pyqtSignal()
    languageInserted = QtCore.pyqtSignal(str)

    def __init__(self, languages, parent=None):
        super(LanguageInsertion, self).__init__(parent)
        self.setupUi(self)
        self.textBrowser.setReadOnly(True)
        self.setupButtons()
        self.setupCombobox()
        if self.parent() is not None:
            self.parent().destroyed.connect(self.reset)

        self.currentLanguages = []

        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.getCurrentLanguages)
        self.current_timer.setSingleShot(True)
        self.current_timer.start(5000)

        self.blockSignals(True)
        for lang in languages:
            self.tryInsert(ISO_639_3.get(lang, ''))
        self.blockSignals(False)

    def setupButtons(self):
        self.xButton.clicked.connect(self.clear)
        self.insertButton.clicked.connect(self.tryInsert)

    def setupCombobox(self):
        self.languagesCombo.comboStyleSheet = (
            """
            QLineEdit {
                border: 2px solid gray;
                border-radius: 15px;
                padding: 6px;
                selection-background-color: darkgray;
                min-width: 10em;
                font: 20px;
                outline: 0px;
            }
            """ +
            "QAbstractItemView {"
            "    min-width: 150px;"
            "}\n"
            "QAbstractItemView::item {"
            "    min-height: 30px;"
            "}\n"
            "QScrollBar:vertical {\n"
            "  width: 5px;\n"
            "  background: #f1f1f1;\n"
            "}\n"
            "\n"
            "QScrollBar::handle:vertical {\n"
            "  background: #888;\n"
            "  border-radius: 2px;\n"
            "}\n"
            "QScrollBar::add-line:vertical {\n"
            "  border: 2px solid gray;\n"
            "  background: #f1f1f1;\n"
            "}\n"
            "\n"
            "QScrollBar::handle:hover:vertical {\n"
            "  background: #555;\n"
            "}\n"
            )
        self.languagesCombo.setDropDownStylesheet()

        for i, code in enumerate(TESSERACT_CODES):  # insert items to combobox
            try:
                lang = ISO_639_3[code]
            except KeyError:
                if code in ('equ',  'osd'):  # math, ord osd, no need
                    continue
                else:
                    lang = ISO_639_3[code.split('_')[0]]
            self.languagesCombo.addItem(lang)
            self.languagesCombo.setItemData(i, code)

        self.languagesCombo.setView(QtWidgets.QListView())
        self.languagesCombo.setStyleSheet(self.languagesCombo.styleSheet() + '\n' +
                                          "QListView::item {height:22px;}")

        # default index
        self.languagesCombo.setCurrentIndex(-1)

        self.languagesCombo.returnPressed.connect(self.tryInsert)

    def tryInsert(self, lang=None):
        lang = self.languagesCombo.currentText() if not lang else lang
        if lang in ENGLISH_3 and not lang in self.currentLanguages:
            self.insert(lang)

    def insert(self, language):
        print(language)
        if not self.textBrowser.toPlainText():
            self.textBrowser.insertPlainText(language)
        else:
            self.textBrowser.insertPlainText(', ' + language)
        self.currentLanguages.append(language)
        self.languageInserted.emit(ENGLISH_3[language])

    def reset(self):
        self.languagesCombo.setCurrentIndex(-1)
        self.clear()

    def clear(self):
        self.currentLanguages.clear()
        self.textBrowser.clear()
        self.cleared.emit()

    def getCurrentLanguages(self):
        return (ENGLISH_3[i] for i in self.currentLanguages)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main = LanguageInsertion()
    main.show()
    sys.exit(app.exec_())
