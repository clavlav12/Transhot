from abc import ABC, abstractmethod
import os.path
from pathlib import Path
import json


class DataBaseHandlerTemplate(ABC):
    def __init__(self, path, defaultData):
        self.path = os.path.normpath(path)
        existed = self.load()
        if not existed:
            self.initiateData(defaultData)
        self.beforeChanges = self.copyData()
        if self.path in self.connectedBases:
            self.connectedBases[self.path].append(self)
        else:
            self.connectedBases[self.path] = [self]

    @property
    @abstractmethod
    def connectedBases(self) -> dict:
        # {path: [DataBaseHandlerTemplate]}
        ...

    def commitChanges(self):
        for base in self.connectedBases[self.path]:
            base.data = self.copyData()
        self.beforeChanges = self.copyData()
        self.save()

    def rollbackChanges(self):
        self.data = self.beforeChanges
        self.beforeChanges = self.copyData()

    def initiateData(self, data):
        self.data = data
        self.beforeChanges = self.copyData()

    def save(self):
        with open(self.path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def load(self) -> bool:
        try:
            p = Path(os.path.dirname(self.path))
            existed = p.exists()
            p.mkdir(exist_ok=True, parents=True)
            # create the file itself
            try:
                with open(self.path, 'a'):
                    pass
            except PermissionError:
                os.rmdir(self.path)
                with open(self.path, 'a'):
                    pass
            assert existed  # if not existed, return false
            with open(self.path, 'r') as file:
                self.data = json.load(file)
        except Exception as e:
            print(e)
            return False
        return True

    @abstractmethod
    def copyData(self):
        pass

    def close(self):
        self.connectedBases[self.path].remove(self)


if __name__ == '__main__':
    class testHandler(DataBaseHandlerTemplate):
        connectedBases = {
            # {path: [DataBaseHandlerTemplate]}
        }

        def __init__(self, path):
            data = {}
            super(testHandler, self).__init__(path, data)

        def setName(self, name):
            self.data['name'] = name

        def copyData(self):
            return self.data.copy()

    def printData():
        print(first.data)
        print(second.data)

    first = testHandler(r'db\data.db')
    second = testHandler(r'db\data.db')
    first.setName('avi')
    first.data['name'] = 'bobi'
    first.commitChanges()
    printData()
