#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp, pyqtSignal, QStringListModel
from PyQt5.QtWidgets import QCompleter, QComboBox, QStyledItemDelegate


class CustomQCompleter(QCompleter):

    def __init__(self, *args):
        super(CustomQCompleter, self).__init__(*args)
        self.local_completion_prefix = ""
        self.source_model = None
        self.filterProxyModel = QSortFilterProxyModel(self)
        self.usingOriginalModel = False

    def setModel(self, model):
        self.source_model = model
        self.filterProxyModel = QSortFilterProxyModel(self)
        self.filterProxyModel.setSourceModel(self.source_model)
        super(CustomQCompleter, self).setModel(self.filterProxyModel)
        self.usingOriginalModel = True

    def updateModel(self):
        if not self.usingOriginalModel:
            self.filterProxyModel.setSourceModel(self.source_model)

        pattern = QRegExp(self.local_completion_prefix,
                          Qt.CaseInsensitive,
                          QRegExp.FixedString)

        self.filterProxyModel.setFilterRegExp(pattern)

    def splitPath(self, path):
        self.local_completion_prefix = path
        self.updateModel()
        if self.filterProxyModel.rowCount() == 0:
            self.usingOriginalModel = False
            self.filterProxyModel.setSourceModel(QStringListModel([path]))
            return [path]

        return []


class ExtendedComboBox(QComboBox):
    returnPressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = CustomQCompleter(self.pFilterModel, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.mCompleterItemDelegate = QStyledItemDelegate(self)

        self.completer.popup().setItemDelegate(self.mCompleterItemDelegate)

        self.comboStyleSheet = (
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
            "    min-width: 200px;"
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

        self.setDropDownStylesheet()

        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.lineEdit().returnPressed.connect(self.returnPress)
        self.completer.activated.connect(self.on_completer_activated)

    def setDropDownStylesheet(self):
        self.completer.popup().setStyleSheet(self.comboStyleSheet)
        self.setStyleSheet(self.comboStyleSheet)

    def returnPress(self):
        self.clearFocus()
        self.returnPressed.emit(self.currentText())

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)
        self.completer.popup().setItemDelegate(self.mCompleterItemDelegate)

    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QStringListModel

    app = QApplication(sys.argv)

    string_list = ['hola muchachos', 'adios amigos', 'hello world', 'good bye']

    combo = ExtendedComboBox()

    # either fill the standard model of the combobox
    combo.addItems(string_list)

    # or use another model
    # combo.setModel(QStringListModel(string_list))

    combo.resize(300, 40)
    combo.show()

    sys.exit(app.exec_())
