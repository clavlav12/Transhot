from PyQt5 import QtWidgets, QtCore, QtGui
import sys


class MessageEntry(QtWidgets.QTextEdit):
    returnPressed = QtCore.pyqtSignal(str)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if (e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return) and \
                not e.modifiers() & QtCore.Qt.ShiftModifier:
            self.returnPressed.emit(self.toPlainText())
            return
        return super(MessageEntry, self).keyPressEvent(e)


if __name__ == '__main__':

        app = QtWidgets.QApplication(sys.argv)
        entry = MessageEntry()
        entry.show()
        sys.exit(app.exec_())
