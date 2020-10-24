try:
    from SettingsDialog.shortcutDialog import DataBaseTemplate
except ImportError:
    import DataBaseTemplate


class ShortcutDataBase(DataBaseTemplate.DataBaseHandlerTemplate):
    connectedBases = {
        # {path: [ShortcutDataBase]}
    }

    def __init__(self, path):
        super(ShortcutDataBase, self).__init__(path, {})

    @staticmethod
    def listToDict(lst):
        return {shortcut['tooltip']: shortcut for shortcut in lst}

    @staticmethod
    def dictToList(dct):
        return [dct[tooltip] for tooltip in dct]

    def insert_shortcuts(self, shortcuts: list):
        """
        Firstly inserts shortcuts into table (if exists, updates them)
        :parameter shortcuts: a list of dictionaries of this template:
            {
                tooltip: '<tool tip of the action (str)>',
                shortcut: '<shortcut of the action (str)>',
                enabled: '<whether or not the action is enabled (bool)>'
            }
        """
        try:
            self.data.update(self.listToDict(map(lambda x: x.copy(), shortcuts)))
        except KeyError as e:
            raise KeyError(f"can't find {e.args[0]} in shortcuts")

    def update_shortcut(self, tooltip: str, shortcut: str = None, enabled: bool = None):
        value = self.data[tooltip]
        if shortcut is not None:
            value['shortcut'] = shortcut
        if enabled is not None:
            value['enabled'] = enabled

    def is_shortcut(self, tooltip: str) -> bool:
        return tooltip in self.data

    def get_shortcut(self, tooltip):
        try:
            return self.data[tooltip]
        except KeyError:
            raise KeyError('shortcut "' + tooltip + '" does not exists')

    def getAllShortcuts(self, asDict=False):
        if asDict:
            return self.data
        return self.dictToList(self.data)

    def save_changes(self):
        self.commitChanges()

    def rollback(self):
        self.rollbackChanges()

    def copyData(self):
        return {key: self.data[key].copy() for key in self.data}
