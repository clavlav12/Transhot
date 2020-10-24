from PyQt5 import QtGui, QtCore, QtWidgets
from structures import QListener
try:
    from shortcutDialog.shortcutDataBaseHandler import ShortcutDataBase
except ModuleNotFoundError:
    from SettingsDialog.shortcutDialog.shortcutDataBaseHandler import ShortcutDataBase
try:
    import SettingsDialog.shortcutDialog.shortcut_dialog as shortcut_dialog
except ModuleNotFoundError:
    import shortcutDialog.shortcut_dialog as shortcut_dialog
from typing import List
import warnings
debug = True
if debug:
    import traceback


def getActionName(action):
    if action.toolTip():
        return action.toolTip()
    elif action.statusTip():
        return action.statusTip()
    elif action.objectName():
        return action.objectName()


class KeySequenceRecorder(QtWidgets.QLineEdit):
    updated = QtCore.pyqtSignal(QtGui.QKeySequence)

    modToString = {QtCore.Qt.Key_Control: "Ctrl", QtCore.Qt.Key_Shift: "Shift",
                   QtCore.Qt.Key_Alt: "Alt", QtCore.Qt.Key_Meta: "Meta"}

    def __init__(self, keySequence, *args):
        super(KeySequenceRecorder, self).__init__(*args)
        self.keySequence = keySequence
        self.setKeySequence(keySequence)
        self.home(False)
        self.setReadOnly(True)

    def setKeySequence(self, keySequence):
        self.keySequence = keySequence
        self.setText(self.keySequence.toString(QtGui.QKeySequence.NativeText))

    def clearText(self):
        self.keySequence = QtGui.QKeySequence('')
        self.setText('')

    def keyPressEvent(self, e):
        if e.type() == QtCore.QEvent.KeyPress:
            key = e.key()
            if key == QtCore.Qt.Key_unknown:
                warnings.warn("Unknown key from a macro probably")
                return

            # the user have clicked just and only the special keys Ctrl, Shift, Alt, Meta.
            if (key == QtCore.Qt.Key_Control or
                    key == QtCore.Qt.Key_Shift or
                    key == QtCore.Qt.Key_Alt or
                    key == QtCore.Qt.Key_Meta):
                return

            # check for a combination of user clicks
            modifiers = e.modifiers()
            # if the keyText is empty than it's a special key like F1, F5, ...

            if modifiers & QtCore.Qt.ShiftModifier:
                key += QtCore.Qt.SHIFT
            if modifiers & QtCore.Qt.ControlModifier:
                key += QtCore.Qt.CTRL
            if modifiers & QtCore.Qt.AltModifier:
                key += QtCore.Qt.ALT
            if modifiers & QtCore.Qt.MetaModifier:
                key += QtCore.Qt.META

            self.setKeySequence(QtGui.QKeySequence(key))
            self.clearFocus()
            self.updated.emit(self.keySequence)


class Action:
    """Represents an individual action."""
    actions_list = []
    actions_dict = {
        # tooltip: action
    }
    regularLineEditStyleSheet = '''
                                QLineEdit
                                {
                                    background-color:transparent;
                                }
                                QLineEdit:hover
                                 {
                                    background-color: rgb(224, 232, 246);
                                }
                                QLineEdit:focus
                                {
                                    background-color: rgba(193, 210, 238, 200);
                                    border: 1px solid rgb(60, 127, 177)
                                }
                                '''

    errorLineEditStyleSheet = '''
                                QLineEdit
                                {
                                    background-color:transparent;
                                }
                                QLineEdit:hover
                                 {
                                    background-color: rgb(224, 232, 246);
                                }
                                QLineEdit:focus
                                {
                                    background-color: rgba(255, 8, 8, 50);
                                    border: 1px solid rgba(255, 8, 8, 200);
                                }
                            '''

    def __init__(self, action, rowNumber, tableWidget, parent, dataBase: ShortcutDataBase):
        self.dataBase = dataBase
        self.action = action
        self.text = getActionName(action)
        self.shortcut = action.shortcut()

        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setChecked(action.isEnabled())
        self.checkBox.stateChanged.connect(self.checkBoxChanged)

        widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout(widget)
        self.layout.addWidget(self.checkBox)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)

        rowPosition = tableWidget.rowCount()
        if rowNumber == rowPosition:
            tableWidget.insertRow(rowPosition)
        tableWidget.setCellWidget(rowNumber, 0, widget)

        self.lineEdit = KeySequenceRecorder(action.shortcut(), parent)
        self.lineEdit.setStyleSheet(self.regularLineEditStyleSheet)
        tableWidget.setCellWidget(rowNumber, 1, self.lineEdit)
        self.lineEdit.updated.connect(self.setShortcut)

        item = QtWidgets.QTableWidgetItem()
        tableWidget.setVerticalHeaderItem(rowNumber, item)
        item.setText(self.text)

        self.parent = parent
        self.tableWidget = tableWidget
        self.actions_list.append(self)
        self.actions_dict[self.text] = self

    def checkBoxChanged(self, value: bool):
        self.dataBase.update_shortcut(self.text, enabled=value)

    def setShortcut(self, shortcut: QtGui.QKeySequence):
        action = None
        try:
            for action in self.actions_list:
                if (action.shortcut == shortcut) and (self is not action) and not (shortcut == QtGui.QKeySequence('')):
                    raise ValueError('Shortcut is already in use by "{}"\n'.format(action.text))
            else:  # the shortcut is free
                self.lineEdit.setStyleSheet(self.regularLineEditStyleSheet)
                self.lineEdit.setKeySequence(shortcut)
                self.dataBase.update_shortcut(self.text, shortcut.toString())
                self.shortcut = shortcut
        except ValueError as e:
            self.lineEdit.clearText()
            reply = QtWidgets.QMessageBox.question(self.parent, "Shortcut in use", str(e) + "What would you like to do?"
                                                   , QtWidgets.QMessageBox.Retry |
                                                   QtWidgets.QMessageBox.Ignore |
                                                   QtWidgets.QMessageBox.Cancel
                                                   )

            if reply == QtWidgets.QMessageBox.Retry:
                self.tableWidget.parent().activateWindow()
                self.lineEdit.setFocus()
                self.lineEdit.setStyleSheet(self.errorLineEditStyleSheet)
            elif reply == QtWidgets.QMessageBox.Cancel:
                self.lineEdit.clearFocus()
            else:  # Ignore - solve the collision
                action.setShortcut(QtGui.QKeySequence(''))
                self.setShortcut(shortcut)

    def updateWidgets(self, shortcut: dict):
        """Update widgets states according by shortcut"""
        self.shortcut = QtGui.QKeySequence(shortcut['shortcut'])
        self.checkBox.setChecked(shortcut['enabled'])
        self.lineEdit.setKeySequence(self.shortcut)

    @classmethod
    def loadActions(cls, windowActions: List[QtWidgets.QAction],
                    tableWidget: QtWidgets.QTableWidget,
                    windowParent: QtWidgets.QWidget,
                    db: ShortcutDataBase):
        for idx, action in enumerate(sorted(windowActions,
                                            key=lambda ac: getActionName(ac).lower())):
            cls(action, idx, tableWidget, windowParent, db)

    @classmethod
    def updateAll(cls, dataBase: ShortcutDataBase):
        shortcuts = dataBase.getAllShortcuts()
        for shortcutDict in shortcuts:
            action = cls.actions_dict[shortcutDict['tooltip']]
            action.updateWidgets(shortcutDict)

    def __str__(self):
        return self.text


class shortcutEditor(QtWidgets.QDialog, shortcut_dialog.Ui_Dialog):
    defaultDatabasePath = 'shortcuts.db'

    def __init__(self, window: QtWidgets.QWidget,
                 defaultShortcuts: List[dict],
                 dbPath: str = defaultDatabasePath,
                 countMenu: bool = False,
                 *,
                 listener: QListener = None,
                 ):
        """
        this window assumes that every QAction of window has a unique tool tip, status tip or object name!!
        it will not work otherwise!
        before creating this window, load saved actions by calling shortcutEditor.loadSavedActions
        :parameter window: the window this dialog edits the shortcuts to

        :parameter defaultShortcuts: a list of dictionaries of this template:
            {
                tooltip: '<tool tip of the action (str)>',
                shortcut: '<shortcut of the action (str)>',
                enabled: '<whether or not the action is enabled (bool)>'
            }
            To obtain such a dictionary from a window's current shortcuts, call static
            function shortcutEditor.windowActionsToDict().

        :parameter dbPath (optional): a database made by sqlite path.
            If not provided creates a new one.

        :parameter countMenu (optional): whether or not edit menu actions
        """
        Action.actions_list.clear()
        super(shortcutEditor, self).__init__(window)
        self.countMenu = countMenu
        self.defaultShortcuts = [dict_.copy() for dict_ in defaultShortcuts]
        self.setupUi(self)
        self.setWindowTitle('Shortcut Editor')
        self.resize(400, 400)

        self.shortcutDB = ShortcutDataBase(dbPath)
        self.beforeChanges = self.windowActionsToDict(window, countMenu)
        self.shortcutDB.insert_shortcuts(self.beforeChanges)

        self.tableWidget.setContentsMargins(0, 0, 0, 0)
        self.parentActions = self.getFilteredWindowActions(window)
        Action.loadActions(self.parentActions, self.tableWidget, window, self.shortcutDB)

        self.btn = QtWidgets.QPushButton("Restore To default", self)
        self.btn.clicked.connect(self.restoreToDefault)
        self.btn.setAutoDefault(False)
        self.layout().addWidget(self.btn)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        header = self.tableWidget.verticalHeader()
        header.setDefaultSectionSize(32)

        if listener is not None:
            listener.keyPressed.connect(self.printScreenPressed)
        self.listener = listener

    @staticmethod
    def printScreenPressed(key):
        if 'Print' in key:  # Qt can't catch this key
            widget = QtWidgets.QApplication.focusWidget()
            if isinstance(widget, KeySequenceRecorder):
                if '+' in key:
                    modifier = key.split('+')[0].lower()
                    if modifier == 'alt':
                        widget.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                             QtCore.Qt.Key_Print, QtCore.Qt.AltModifier))
                    elif modifier == 'shift':
                        widget.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                             QtCore.Qt.Key_Print, QtCore.Qt.ShiftModifier))
                    elif modifier == 'ctrl':
                        widget.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                             QtCore.Qt.Key_Print, QtCore.Qt.ControlModifier))
                else:
                    widget.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                                         QtCore.Qt.Key_Print, QtCore.Qt.NoModifier))

    def closeEvent(self, QCloseEvent):
        self.safeClose()
        super(shortcutEditor, self).closeEvent(QCloseEvent)

    def safeClose(self):
        self.listener.keyPressed.disconnect(self.printScreenPressed)
        if self.notChanged():
            self.closeDatabaseConnection()
            return
        reply = QtWidgets.QMessageBox.question(self, "Save Changes?", "Would you like to save your changes?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.saveSettings()
        else:
            self.unSaveSettings()

    def closeDatabaseConnection(self):
        self.shortcutDB.close()

    def notChanged(self) -> True:
        """Checks if changes were made to the database"""
        return sorted(self.beforeChanges, key=lambda x: x['tooltip']) ==\
               sorted(self.shortcutDB.getAllShortcuts(), key=lambda x: x['tooltip'])

    def saveSettings(self):
        self.applyChangesToWindow()

    def unSaveSettings(self):
        self.shortcutDB.rollback()
        self.closeDatabaseConnection()

    def restoreToDefault(self):
        """Callback and Restore database to it's default state according to self.defaultShortcuts"""
        self.shortcutDB.rollback()
        self.shortcutDB.insert_shortcuts(self.defaultShortcuts)
        Action.updateAll(self.shortcutDB)

    def applyChangesToWindow(self):
        """Called after save. Apply changes to self.window (use setWindowShortcut)"""
        self.setWindowShortcut(self.parent(), self.shortcutDB.getAllShortcuts(), self.countMenu)
        # self.long_save_changes()
        LongOperation(self.long_save_changes, self.parent())

    def long_save_changes(self):
        self.shortcutDB.save_changes()
        self.shortcutDB.close()

    @classmethod
    def setWindowShortcut(cls, window: QtWidgets.QWidget, shortcutDict: List[dict], countMenu=False) -> None:
        """
        sets the window's action's shortcuts according to shortcutDict

        :parameter shortcutDict: a list of dictionaries of this template:
            {
                tooltip: '<tool tip of the action (str)>',
                shortcut: '<shortcut of the action (str)>',
                enabled: '<whether or not the action is enabled (bool)>'
            }
            To build such a dictionary from a window's current shortcuts, call static
            function shortcutEditor.windowActionsToDict().

        :parameter window: the window to apply changes to
        :parameter countMenu: (optional) whether or not edit menu actions
        """
        shortcutDict = {
            shortcut['tooltip']: shortcut for shortcut in shortcutDict
        }  # tooltip: {tooltip: , shortcut:, enabled:}

        windowActions = cls.getFilteredWindowActions(window, countMenu)
        for action in windowActions:
            name = getActionName(action)
            try:
                newShortcut = shortcutDict[name]['shortcut']
                newEnabled = shortcutDict[name]['enabled']
                action.setShortcut(newShortcut)
                action.setEnabled(newEnabled)
            except Exception as e:
                if debug:
                    print("Exception at setWindowShortcut", e)  # just in case of something unexpected
                    traceback.print_exc()

    @classmethod
    def loadSavedActions(cls, window, path=defaultDatabasePath, countMenu=False) -> None:
        dataBase = ShortcutDataBase(path)
        try:
            shortcutsDictList = dataBase.getAllShortcuts(True)  # trying to load
        except Exception as e:
            shortcutsDictList = {}
            if debug:
                print("Exception at loadSavedActions", e)  # making sure it wasn't something unexpected
                traceback.print_exc()

        # shortcutsDictList is a dict of form {tooltip: {tooltip: , shortcut:, enabled: }}
        windowActions = {
            getActionName(action): action
            for action in cls.getFilteredWindowActions(window, countMenu)
        }

        #             if shortcutsDictList[actionName]['shortcut']:  # has a shortcut. idk why is was here
        # in case of a problem check it
        for actionName in shortcutsDictList:
            try:
                windowActions[actionName].setShortcut(shortcutsDictList[actionName]['shortcut'])
                windowActions[actionName].setDisabled(not shortcutsDictList[actionName]['enabled'])
            except KeyError:
                pass
        dataBase.close()

    @staticmethod
    def getFilteredWindowActions(window, countMenu=False) -> List[QtWidgets.QAction]:
        return list(filter(lambda action: action.toolTip() or action.statusTip() or action.objectName(),
                           set(window.findChildren(QtWidgets.QAction)) - (set(window.menuBar().actions() if countMenu
                                                                              else set()))))

    @classmethod
    def windowActionsToDict(cls, window: QtWidgets.QWidget, countMenu=False) -> List[dict]:
        """Loads an window actions into list of dicts of this template:
            {
                tooltip: '<tool tip of the action (str)>',
                shortcut: '<shortcut of the action (str)>',
                enabled: '<whether or not the action is enabled (bool)>'
            }
        """
        actions = cls.getFilteredWindowActions(window, countMenu)
        return [
            {'tooltip': getActionName(action),
             'shortcut': action.shortcut().toString(),
             'enabled': action.isEnabled()
             }
            for action in actions
        ]


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


if __name__ == '__main__':
    def create_shortcut(window, method, tooltip, *keys):
        action = QtWidgets.QAction(window)
        action.setShortcuts(keys)
        action.triggered.connect(method)
        action.setToolTip(tooltip)
        window.addAction(action)
        return action


    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    create_shortcut(win, lambda: None, 'Copy', 'ctrl+c')
    create_shortcut(win, lambda: None, 'Undo', 'ctrl+z')
    create_shortcut(win, lambda: None, 'Redo', 'ctrl+y')
    main = shortcutEditor(win, [
        {'shortcuts': 'ctrl+c', 'tooltip': 'Copy', 'enable': True},
        {'shortcuts': 'ctrl+z', 'tooltip': 'Undo', 'enable': True},
        {'shortcuts': 'ctrl+y', 'tooltip': 'Redo', 'enable': True},
    ])
    main.show()
    # main = KeySequenceRecorder(QtGui.QKeySequence(''))
    sys.exit(app.exec_())
