# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LanguageInsertionWidgetUI.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LanguagesInsertionWidget(object):
    def setupUi(self, LanguagesInsertionWidget):
        LanguagesInsertionWidget.setObjectName("LanguagesInsertionWidget")
        LanguagesInsertionWidget.resize(360, 69)
        LanguagesInsertionWidget.setMaximumSize(QtCore.QSize(16777215, 69))
        self.horizontalLayout = QtWidgets.QHBoxLayout(LanguagesInsertionWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.languagesCombo = ExtendedComboBox(LanguagesInsertionWidget)
        self.languagesCombo.setObjectName("languagesCombo")
        self.verticalLayout.addWidget(self.languagesCombo)
        self.insertButton = QtWidgets.QPushButton(LanguagesInsertionWidget)
        self.insertButton.setObjectName("insertButton")
        self.verticalLayout.addWidget(self.insertButton)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.textBrowser = QtWidgets.QTextBrowser(LanguagesInsertionWidget)
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 50))
        self.textBrowser.setUndoRedoEnabled(False)
        self.textBrowser.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textBrowser.setLineWrapColumnOrWidth(5000)
        self.textBrowser.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout_2.addWidget(self.textBrowser)
        self.xButton = QtWidgets.QPushButton(LanguagesInsertionWidget)
        self.xButton.setMinimumSize(QtCore.QSize(20, 20))
        self.xButton.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setFamily("Arial Rounded MT Bold")
        font.setPointSize(27)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.xButton.setFont(font)
        self.xButton.setStyleSheet("QPushButton{\n"
"    border:none;\n"
"    /*font: bold;*/\n"
"    /*font-size: 36px;*/\n"
"    margin-top: 1px;\n"
"    padding-top: 1px;\n"
"    color: rgb(220, 0, 0);\n"
"}\n"
"QPushButton:hover:!pressed{\n"
"    color:rgb(255, 0, 0);\n"
"}")
        self.xButton.setObjectName("xButton")
        self.horizontalLayout_2.addWidget(self.xButton, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.horizontalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(LanguagesInsertionWidget)
        QtCore.QMetaObject.connectSlotsByName(LanguagesInsertionWidget)

    def retranslateUi(self, LanguagesInsertionWidget):
        _translate = QtCore.QCoreApplication.translate
        LanguagesInsertionWidget.setWindowTitle(_translate("LanguagesInsertionWidget", "Form"))
        self.insertButton.setText(_translate("LanguagesInsertionWidget", "Insert"))
        self.textBrowser.setPlaceholderText(_translate("LanguagesInsertionWidget",
                                                       "Insert the desired Languages to to be recognized by the scanner"
                                                       ". The more the longer the recognition lasts."
                                                       " Leave empty to use above languages"))
        self.xButton.setText(_translate("LanguagesInsertionWidget", "X"))


try:
    from extendedcombobox import ExtendedComboBox
except ModuleNotFoundError:
    from SettingsDialog.extendedcombobox import ExtendedComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LanguagesInsertionWidget = QtWidgets.QWidget()
    ui = Ui_LanguagesInsertionWidget()
    ui.setupUi(LanguagesInsertionWidget)
    LanguagesInsertionWidget.show()
    sys.exit(app.exec_())
