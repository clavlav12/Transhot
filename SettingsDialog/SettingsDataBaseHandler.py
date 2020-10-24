try:
    from SettingsDialog.shortcutDialog import DataBaseTemplate
except ImportError:
    try:
        import shortcutDialog.DataBaseTemplate
    except ImportError:
        import DataBaseTemplate

from copy import deepcopy


class SettingsDataBase(DataBaseTemplate.DataBaseHandlerTemplate):
    connectedBases = {
        # {path: [SettingsDataBase]}
    }

    pythonObjectToJson = {
        set: list,
    }

    jsonToPythonObject = {
        value: key for key, value in pythonObjectToJson.items()
    }

    def convertToJsonDataTypes(self, dct: dict):
        """
        :parameter dct:
        {
            SettingsName: SettingsValue
        }
        """
        return {
            setting: (self.pythonObjectToJson[self.settings[setting]](dct[setting])
                      if self.settings[setting] in self.pythonObjectToJson
                      else dct[setting])
            for setting in dct
        }

    def convertToPythonDataTypes(self, dct: dict):
        """
        :parameter dct:
        {
            SettingsName: SettingsValue
        }
        """
        return {
            setting: (self.jsonToPythonObject[self.settings[setting]](dct[setting])
                      if self.settings[setting] in self.jsonToPythonObject
                      else dct[setting])
            for setting in dct
        }

    def __init__(self, path):
        super(SettingsDataBase, self).__init__(path, {})

        self.settings = {'dest': str,
                         'imsource': set,
                         'saves': str,
                         'source': str
                         }  # supports all and only
        # json data types or converted types by pythonObjectToJson
        self.path = path

    def insert_settings(self, input_settings: dict):
        """
        :param input_settings: dict of this form
        {
            SettingsName: SettingsValue,
            ...
        }
        """
        self.data.update(deepcopy(self.convertToJsonDataTypes(input_settings)))

    def update_setting(self, setting: str, value) -> None:
        if self.settings[setting] in self.pythonObjectToJson:
            value = self.pythonObjectToJson[self.settings[setting]](value)
        self.data[setting] = deepcopy(value)

    def is_settings(self) -> bool:
        return bool(self.data)

    def get_setting(self, setting):
        value = deepcopy(self.data[setting])
        if self.settings[setting] in self.jsonToPythonObject:
            value = self.jsonToPythonObject[self.settings[setting]](value)
        return value

    def get_settings(self) -> dict:
        assert self.data, 'no settings found'
        return self.convertToPythonDataTypes(self.data)

    def save_changes(self):
        self.commitChanges()

    def rollback(self):
        self.rollbackChanges()

    def copyData(self):
        return deepcopy(self.data)


if __name__ == '__main__':
    db = SettingsDataBase(':memory:')
    db.insert_settings({
        'dest': 'Dest',
        'imsource': ['source1', 'source2'],
        'saves': 'Saves',
        'source': 'Source'
    }
    )
    db.insert_settings({
        'dest': 'Dest2',
        'imsource': ['source3', 'source4'],
        'saves': 'Saves2',
        'source': 'Source2'
    }
    )
    print(db.get_settings())
