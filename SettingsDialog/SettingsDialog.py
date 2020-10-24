try:
    from SettingsDialog.shortcutDialog.newShortcutDialog import shortcutEditor, Action, LongOperation
    from SettingsDialog.SettingsDataBaseHandler import SettingsDataBase
    from SettingsDialog.extendedcombobox import ExtendedComboBox
    from SettingsDialog.LanguagesInsertionWidget import LanguageInsertion
except ModuleNotFoundError:
    from shortcutDialog.newShortcutDialog import shortcutEditor, Action, LongOperation
    from extendedcombobox import ExtendedComboBox
    from LanguagesInsertionWidget import LanguageInsertiona
from PyQt5 import QtWidgets, QtCore, QtGui
from TranslationWindow.Translate import languages
import os.path


class ButtonLineEdit(QtWidgets.QLineEdit):
    buttonClicked = QtCore.pyqtSignal(bool)

    def __init__(self, icon_file, parent=None):
        super(ButtonLineEdit, self).__init__(parent)

        self.button = QtWidgets.QToolButton(self)
        self.button.setIcon(QtGui.QIcon(icon_file))
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        self.button.clicked.connect(self.buttonClicked.emit)

        frameWidth = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth * 2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth * 2 + 2))

    def resizeEvent(self, event):
        buttonSize = self.button.sizeHint()
        frameWidth = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frameWidth - buttonSize.width(),
                         (self.rect().bottom() - buttonSize.height() + 1) / 2)
        super(ButtonLineEdit, self).resizeEvent(event)


class pathLineEdit(ButtonLineEdit):
    def __init__(self, settingsDB: SettingsDataBase, parent=None):
        super(pathLineEdit, self).__init__(':icon/images/browse.png', parent)
        self.buttonClicked.connect(self.browse)
        self.settingsDB = settingsDB
        self.setText(self.settingsDB.get_setting('saves'))

    def focusOutEvent(self, a0: QtGui.QFocusEvent) -> None:
        self.tryToSetPath(self.text())
        return super(pathLineEdit, self).focusOutEvent(a0)

    def tryToSetPath(self, path):
        if not os.path.isdir(path):
            self.setText('')
        else:
            self.settingsDB.update_setting('saves', os.path.normpath(path))

    def browse(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, r"Save File", self.settingsDB.get_setting('saves'))
        if path:
            self.setText(path)
            self.settingsDB.update_setting('saves', os.path.normpath(path))

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == QtCore.Qt.Key_Return:
            self.clearFocus()
        else:
            super(pathLineEdit, self).keyPressEvent(a0)


class PreferenceDialog(shortcutEditor):
    shortcutsDatabasePath = 'data\\shortcuts.db'
    settingsDatabasePath = 'data\\settings.db'
    actionsChanged = QtCore.pyqtSignal()
    # between initiateSettingsDatabase and __init__(). Generates a new connection.

    @classmethod
    def initiateSettingsDatabase(cls, defaultSettings,
                                 pathToDatabase=settingsDatabasePath) -> SettingsDataBase:
        database = SettingsDataBase(pathToDatabase)
        if not database.is_settings():
            database.insert_settings(defaultSettings)
        # now it must have settings
        database.save_changes()
        return database

    @classmethod
    def loadSavedActions(cls, window, path=shortcutsDatabasePath, countMenu=False) -> None:
        super(PreferenceDialog, cls).loadSavedActions(window, path, countMenu)

    def __init__(self,
                 parent: QtWidgets.QWidget,
                 defaultShortcuts: list,
                 defaultSettings: dict,
                 shortcutsDBPath: str = shortcutsDatabasePath,
                 settingsDBPath: str = settingsDatabasePath,
                 countMenu=False,
                 *,
                 listener=None,
                 icon=None):
        """
        :parameter parent: the window this dialog edits the shortcuts to
        :parameter defaultSettings: a dict of this form:
        {
            'dest': <dest (str)> ,
            'imsource': <imsource (list)>,
            'saves': <saves (str)>,
            'source': <source (str)>
        }
        """
        super(PreferenceDialog, self).__init__(parent, defaultShortcuts, shortcutsDBPath, countMenu, listener=listener)

        if icon is not None:
            self.setWindowIcon(icon)
        self.settingsDB = SettingsDataBase(settingsDBPath)
        self.defaultSettings = defaultSettings
        currentSettings = self.settingsDB.get_settings()
        self.settingsBeforeChanges = currentSettings.copy()
        self.settingsBeforeChanges['imsource'] = set(self.settingsBeforeChanges['imsource'].copy())

        self.gridLayout = QtWidgets.QGridLayout()
        QtWidgets.QApplication.restoreOverrideCursor()
        QtWidgets.QApplication.processEvents()

        self.setWindowTitle('Settings')
        self.sourceLanguageCombo = ExtendedComboBox(self)
        self.destinationLanguageCombo = ExtendedComboBox(self)
        for i, (code, lang) in enumerate(languages.items()):
            self.sourceLanguageCombo.addItem(f'{lang.capitalize()} ({code})')
            self.sourceLanguageCombo.setItemData(i, code)
            self.destinationLanguageCombo.addItem(f'{lang.capitalize()} ({code})')
            self.destinationLanguageCombo.setItemData(i, code)

        self.sourceLanguageCombo.currentIndexChanged.connect(self.sourceChanged)
        self.destinationLanguageCombo.currentIndexChanged.connect(self.destinationChanged)

        self.sourceLabel = QtWidgets.QLabel('First Language', self)
        self.destinationLabel = QtWidgets.QLabel('Second Language', self)

        self.sourceLabel.setMaximumSize(120, 1000000)
        self.destinationLabel.setMaximumSize(120, 1000000)

        self.sourceLanguageCombo.setView(QtWidgets.QListView())
        self.sourceLanguageCombo.setStyleSheet(self.sourceLanguageCombo.styleSheet() + '\n' +
                                               "QListView::item {height:22px;}")
        self.destinationLanguageCombo.setView(QtWidgets.QListView())
        self.destinationLanguageCombo.setStyleSheet(self.destinationLanguageCombo.styleSheet() + '\n' +
                                                    "QListView::item {height:22px;}")

        self.insertionDialog = LanguageInsertion(currentSettings['imsource'], self)
        margin = self.insertionDialog.horizontalLayout.getContentsMargins()
        self.insertionDialog.horizontalLayout.setContentsMargins(
            0, margin[1], 0, margin[3]
        )
        self.insertionDialog.languagesCombo.setMaximumWidth(75)
        self.insertionDialog.insertButton.setMaximumWidth(75)

        self.verticalLayout.removeWidget(self.btn)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 2))
        self.verticalLayout.addWidget(self.insertionDialog)
        self.verticalLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 2))
        self.verticalLayout.addWidget(self.btn)

        self.insertionDialog.cleared.connect(self.insertionDialogCleared)
        self.insertionDialog.languageInserted.connect(self.insertionDialogInserted)

        self.sourceLanguageCombo.setCurrentIndex(
            self.sourceLanguageCombo.findData(currentSettings['source']))
        self.destinationLanguageCombo.setCurrentIndex(
            self.destinationLanguageCombo.findData(currentSettings['dest']))

        self.pathLabel = QtWidgets.QLabel('Saves Folder')
        self.pathLineEdit = pathLineEdit(self.settingsDB)

        self.gridLayout.addWidget(self.sourceLabel, 0, 0)
        self.gridLayout.addWidget(self.sourceLanguageCombo, 0, 1)
        self.gridLayout.addWidget(self.destinationLabel, 1, 0)
        self.gridLayout.addWidget(self.destinationLanguageCombo, 1, 1)
        self.gridLayout.addWidget(QtWidgets.QWidget(), 2, 0)
        self.gridLayout.addWidget(self.pathLabel, 3, 0)
        self.gridLayout.addWidget(self.pathLineEdit, 3, 1)

        self.move(self.pos() + (QtGui.QGuiApplication.primaryScreen().geometry().center() - self.geometry().center()))

    def restoreToDefault(self):
        super(PreferenceDialog, self).restoreToDefault()
        self.settingsDB.rollback()
        self.settingsDB.insert_settings(self.defaultSettings)
        self.updateWidgets()

    def updateWidgets(self):
        self.sourceLanguageCombo.setCurrentIndex(
            self.sourceLanguageCombo.findData(self.settingsDB.get_setting('source')))
        self.destinationLanguageCombo.setCurrentIndex(
            self.destinationLanguageCombo.findData(self.settingsDB.get_setting('dest')))
        # empty languages insertion dialog and add new languages
        self.insertionDialog.reset()
        print(self.settingsDB.get_setting('imsource'))
        for source in self.settingsDB.get_setting('imsource'):
            self.insertionDialog.tryInsert(source)
        self.pathLineEdit.tryToSetPath(self.settingsDB.get_setting('saves'))

    def insertionDialogCleared(self):
        self.settingsDB.update_setting('imsource', [])

    def insertionDialogInserted(self, lang):
        self.settingsDB.update_setting('imsource',
                                       self.settingsDB.get_setting('imsource') + [lang])

    def clearLayout(self):
        if self.layout() is not None:
            old_layout = self.verticalLayout
            for i in reversed(range(old_layout.count())):
                old_layout.itemAt(i).widget().setParent(None)

    def notChanged(self):
        currentSettings = self.settingsDB.get_settings()
        currentSettings['imsource'] = set(currentSettings['imsource'].copy())
        return super(PreferenceDialog, self).notChanged() and currentSettings == self.settingsBeforeChanges

    def sourceChanged(self, index):
        self.settingsDB.update_setting('source', self.sourceLanguageCombo.itemData(index))

    def destinationChanged(self, index):
        self.settingsDB.update_setting('dest', self.destinationLanguageCombo.itemData(index))

    def unSaveSettings(self):
        self.settingsDB.rollback()
        super(PreferenceDialog, self).unSaveSettings()

    def long_save_changes(self):
        super(PreferenceDialog, self).long_save_changes()
        self.settingsDB.save_changes()
        self.settingsDB.close()
        self.actionsChanged.emit()

    def closeDatabaseConnection(self):
        super(PreferenceDialog, self).closeDatabaseConnection()
        self.settingsDB.close()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    sys.exit(app.exec_())
