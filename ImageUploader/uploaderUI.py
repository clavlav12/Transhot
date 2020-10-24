# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uploaderUI.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.setEnabled(True)
        Dialog.resize(370, 41)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setAcceptDrops(False)
        Dialog.setWindowOpacity(1.0)
        Dialog.setLayoutDirection(QtCore.Qt.LeftToRight)
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(False)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.stackedWidget = QtWidgets.QStackedWidget(Dialog)
        self.stackedWidget.setObjectName("stackedWidget")
        self.loadingPage = QtWidgets.QWidget()
        self.loadingPage.setObjectName("loadingPage")
        self.gridLayout = QtWidgets.QGridLayout(self.loadingPage)
        self.gridLayout.setObjectName("gridLayout")
        self.cancelButton = QtWidgets.QPushButton(self.loadingPage)
        self.cancelButton.setObjectName("cancelButton")
        self.gridLayout.addWidget(self.cancelButton, 0, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.loadingPage)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 0, 1, 1, 1)
        self.stackedWidget.addWidget(self.loadingPage)
        self.successPage = QtWidgets.QWidget()
        self.successPage.setObjectName("successPage")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.successPage)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.openButton = QtWidgets.QPushButton(self.successPage)
        self.openButton.setObjectName("openButton")
        self.horizontalLayout.addWidget(self.openButton)
        self.copyButton = QtWidgets.QPushButton(self.successPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.copyButton.sizePolicy().hasHeightForWidth())
        self.copyButton.setSizePolicy(sizePolicy)
        self.copyButton.setObjectName("copyButton")
        self.horizontalLayout.addWidget(self.copyButton)
        self.lineEdit = QtWidgets.QLineEdit(self.successPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.stackedWidget.addWidget(self.successPage)
        self.failedPage = QtWidgets.QWidget()
        self.failedPage.setObjectName("failedPage")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.failedPage)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.closeButton = QtWidgets.QPushButton(self.failedPage)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout_2.addWidget(self.closeButton)
        self.failLabel = QtWidgets.QLabel(self.failedPage)
        self.failLabel.setTextFormat(QtCore.Qt.RichText)
        self.failLabel.setObjectName("failLabel")
        self.horizontalLayout_2.addWidget(self.failLabel)
        self.stackedWidget.addWidget(self.failedPage)
        self.gridLayout_2.addWidget(self.stackedWidget, 0, 1, 1, 1)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Image Uploader"))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))
        self.openButton.setText(_translate("Dialog", "Open"))
        self.copyButton.setText(_translate("Dialog", "Copy"))
        self.lineEdit.setText(_translate("Dialog", "https://i.imgur.com/dfbJrRp.png"))
        self.closeButton.setText(_translate("Dialog", "Close"))
        self.failLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600; color:#ff0000;\">Image Upload Failed. Please Try Again Later</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
