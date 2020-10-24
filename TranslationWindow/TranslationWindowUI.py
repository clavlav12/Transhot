# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TranslationWindowUI.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setStyleSheet("QDialog{\n"
"    background-color: rgb(228, 255, 250);\n"
"}")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.progressBar.setFont(font)
        self.progressBar.setStyleSheet("QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(165, 120, 255, 255), stop:1 rgba(0, 0, 255, 255));\n"
"    /*width: 20px;*/\n"
"\n"
"}\n"
"")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", -1)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.sourceLanguageCombo = ExtendedComboBox(Dialog)
        self.sourceLanguageCombo.setObjectName("sourceLanguageCombo")
        self.horizontalLayout_2.addWidget(self.sourceLanguageCombo)
        self.reverseLanguages = QtWidgets.QPushButton(Dialog, default=False, autoDefault=False)
        self.reverseLanguages.setMinimumSize(QtCore.QSize(25, 25))
        self.reverseLanguages.setMaximumSize(QtCore.QSize(25, 25))
        self.reverseLanguages.setStatusTip("")
        self.reverseLanguages.setStyleSheet("QPushButton {\n"
"    border: 2px solid #555;\n"
"    /*border-radius: 12px;*/\n"
"    border-style: outset;\n"
"    }\n"
"\n"
"QPushButton:hover {  /* light */\n"
"    background-color: rgb(240, 255, 255);\n"
"    }\n"
"\n"
"QPushButton:pressed { /* lighter */\n"
"    border-style: inset;\n"
"    }\n"
"")
        self.reverseLanguages.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/images/reverse.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reverseLanguages.setIcon(icon)
        self.reverseLanguages.setIconSize(QtCore.QSize(16, 16))
        self.reverseLanguages.setObjectName("reverseLanguages")
        self.horizontalLayout_2.addWidget(self.reverseLanguages)
        self.destinationLanguageCombo = ExtendedComboBox(Dialog)
        self.destinationLanguageCombo.setObjectName("destinationLanguageCombo")
        self.horizontalLayout_2.addWidget(self.destinationLanguageCombo)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.inputTextEdit = MessageEntry(Dialog)
        self.inputTextEdit.setTabChangesFocus(False)
        self.inputTextEdit.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.inputTextEdit.setLineWrapColumnOrWidth(0)
        self.inputTextEdit.setReadOnly(False)
        self.inputTextEdit.setOverwriteMode(False)
        self.inputTextEdit.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.inputTextEdit.setPlaceholderText("")
        self.inputTextEdit.setObjectName("inputTextEdit")
        self.horizontalLayout.addWidget(self.inputTextEdit)
        self.outputBrowser = QtWidgets.QTextBrowser(Dialog)
        self.outputBrowser.setObjectName("outputBrowser")
        self.horizontalLayout.addWidget(self.outputBrowser)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.reverseLanguages.setToolTip(_translate("Dialog", "Reverse Languages"))


try:
    from extendedcombobox import ExtendedComboBox
except ModuleNotFoundError:
    from SettingsDialog.extendedcombobox import ExtendedComboBox
try:
    from TranslationWindow.MessageEntry import MessageEntry
except ModuleNotFoundError:
    from MessageEntry import MessageEntry

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
