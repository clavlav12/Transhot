import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from structures import Stack, EmptyStackException
from shortcutDialog.newShortcutDialog import shortcutEditor


def create_shortcut(window, method, tooltip, *keys):
    action = QtWidgets.QAction(window)
    action.setShortcuts(keys)
    action.triggered.connect(method)
    action.setToolTip(tooltip)
    window.addAction(action)
    return action


class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(self.size())
        self.show()
        self.points = QtGui.QPolygon()
        self.undoStack = Stack()
        self.redoStack = Stack()
        create_shortcut(self, self.openShortcutEditor, 'Open Shortcut Editor', 'ctrl+f')
        create_shortcut(self, self.undo, 'Undo', 'ctrl+z')
        create_shortcut(self, self.redo, 'Redo', 'ctrl+y')
        self.defaultShortcuts = shortcutEditor.windowActionsToDict(self)
        shortcutEditor.loadSavedActions(self)

    def openShortcutEditor(self):
        self.editor = shortcutEditor(self, self.defaultShortcuts)
        self.editor.show()

    def undo(self):
        try:
            self.redoStack.push(self.undoStack.top())
            self.points.remove(self.points.indexOf(self.undoStack.pop()))
            self.repaint()
        except EmptyStackException:
            pass

    def redo(self):
        try:
            self.undoStack.push(self.redoStack.top())
            self.points.append(self.redoStack.pop())
            self.repaint()
        except EmptyStackException:
            pass

    def mousePressEvent(self, e):
        if e.button() == 1:  # left click
            self.points.append(e.pos())
            self.undoStack.push(e.pos())
            self.redoStack.clear()
            self.update()
        elif e.button() == 2:
            self.openShortcutEditor()

    def paintEvent(self, ev):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtCore.Qt.red, 5)
        brush = QtGui.QBrush(QtCore.Qt.red)
        qp.setPen(pen)
        qp.setBrush(brush)
        for i in range(self.points.count()):
            qp.drawEllipse(self.points.point(i), 5, 5)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec_())
