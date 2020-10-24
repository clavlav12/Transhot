from PyQt5 import QtCore, QtGui, QtWidgets
import webbrowser

try:
    from ImageUploader.uploaderUI import Ui_Dialog
    from ImageUploader.ImageUploaderInterface import UploaderInterface
except ImportError:
    from uploaderUI import Ui_Dialog
    from ImageUploaderInterface import UploaderInterface


class showUploadedImage(QtWidgets.QDialog, Ui_Dialog):
    closed = QtCore.pyqtSignal()
    DX = 20
    DY = 80

    def __init__(self, interface: UploaderInterface, pixmap: QtGui.QPixmap,
                 parent=None, to_google=False):
        super(showUploadedImage, self).__init__(parent)
        self.setupUi(self)
        self.cancelButton.clicked.connect(self.abort)
        self.copyButton.clicked.connect(self.copyUrl)
        self.openButton.clicked.connect(self.openUrl)
        self.closeButton.clicked.connect(self.abort)

        self.interface = interface
        if to_google:
            self.interface.on_image_upload(self.openUrl)
            self.interface.on_fail(self.uploadFailed)
        else:
            self.interface.on_image_upload(self.uploadSuccess)
            self.interface.on_fail(self.uploadFailed)

        array = QtCore.QByteArray()
        buff = QtCore.QBuffer(array)
        buff.open(QtCore.QIODevice.WriteOnly)
        pixmap.save(buff, "PNG")
        pixmap_bytes = array.data()
        if to_google:
            self.interface.upload_image_to_google_search(pixmap_bytes)
        else:
            self.interface.upload_image(pixmap_bytes)

        self.stackedWidget.setCurrentIndex(0)
        self.setFixedSize(self.size())

        mouseScreen = QtWidgets.QApplication.desktop().primaryScreen()
        SCREEN_RESOLUTION = QtWidgets.QDesktopWidget().screenGeometry(mouseScreen)
        SCREEN_RESOLUTION = (SCREEN_RESOLUTION.width(), SCREEN_RESOLUTION.height())

        self.move(SCREEN_RESOLUTION[0] - int(self.DX * (SCREEN_RESOLUTION[0] / 1920)) - self.width(),
                  SCREEN_RESOLUTION[1] - int(self.DY * (SCREEN_RESOLUTION[1] / 1080)) - self.height()
                  )  # The DX and DY values where chosen on a 1920x1080 screen.

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.MSWindowsFixedSizeDialogHint)

    def copyUrl(self):
        QtWidgets.QApplication.clipboard().setText(self.lineEdit.text())
        self.abort()

    def openUrl(self, url=None):
        if not url:
            url = self.lineEdit.text()
        webbrowser.open(url)
        self.abort()

    def uploadSuccess(self, url):
        self.stackedWidget.setCurrentIndex(1)
        self.lineEdit.setText(url)
        self.lineEdit.selectAll()

    def uploadFailed(self):
        self.stackedWidget.setCurrentIndex(2)

    def abort(self):
        self.closed.emit()
        self.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
