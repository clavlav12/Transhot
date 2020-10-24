from PyQt5.QtCore import QThread, pyqtSignal
import keyboard
from enum import IntFlag


def find(iterable, key):
    for i in iterable:
        if key(i):
            return i
    raise KeyError(f"Could't Find Match")


class TwoWayDict(dict):
    def reverse(self, item):
        return find(self.keys(), lambda i: self[i] == item)


class LongOperation(QThread):
    def __init__(self, function, parent=None, *args, **kwargs):
        super(LongOperation, self).__init__(parent)
        self.start()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.function(*self.args, **self.kwargs)


class Modifiers(IntFlag):
    ctrl = 1
    alt = 2
    shift = 4


class QListener(QThread):
    keyPressed = pyqtSignal(str)
    keyReleased = pyqtSignal(str)
    foo = lambda value: None

    keyboard_to_qt = {  # there is difference in the name of some keys
        'page down': 'PgDown',
        'page up': 'PgUp',
        'print screen': 'Print',
        'scroll lock': 'ScrollLock',
        'num lock': 'numLock',
        'caps lock': 'capsLock',
        'delete': 'Del',
        'insert': 'Ins',
    }

    qt_to_keyboard = {
        value: key for key, value in keyboard_to_qt.items()
    }

    def __init__(self, parent=None, onPress=foo, onRelease=foo):
        """
        :param parent: parent QWidget
        :param onPress: function to call when a key is pressed. sends the key
        :param onRelease: function to call when a key is released. sends the key
        """
        super(QListener, self).__init__(parent)
        self.onPress = onPress
        self.onRelease = onRelease
        self.keyPressed.connect(onPress)
        self.keyReleased.connect(onRelease)
        self.printKeyShortcuts = [
            # (bitwise or operation, function)
        ]
        self.mulKeyShortcuts = [
            # (bitwise or operation, function)
        ]

    @classmethod
    def activeModifiers(cls):
        return cls.sumByKey(filter(keyboard.is_pressed, ('alt', 'shift', 'ctrl')),
                            lambda x: Modifiers[x.lower()])

    @staticmethod
    def activeListModifiers():
        return list(filter(keyboard.is_pressed, ('alt', 'shift', 'ctrl')))
                            
    def run(self):
        keyboard.on_press(lambda x: self.on_press(x.name))
        keyboard.on_release(lambda x: self.on_release(x.name))
        keyboard.wait()

    def on_press(self, key):
        if key in ('print screen', '*'):
            lst = self.mulKeyShortcuts if key == '*' else self.printKeyShortcuts
            modifiers = self.activeModifiers()
            for _, func in filter(lambda sum_: (modifiers & sum_[0]) == sum_[0], lst):
                func()
        if key in keyboard.all_modifiers or self.onPress is self.foo:
            return

        mods = self.activeListModifiers()
        for mod in mods:
            self.keyPressed.emit(mod + '+' + self.keyboard_to_qt.get(key, key))
        if len(mods) > 1:
            self.keyPressed.emit('+'.join(mods) + '+' + self.keyboard_to_qt.get(key, key))
        self.keyPressed.emit(self.keyboard_to_qt.get(key, key))

    def on_release(self, key):
        if self.onRelease is self.foo:
            return
        self.keyReleased.emit(self.keyboard_to_qt.get(key, key))

    def add_hotkey(self, keys, callback):
        keys = keys.toString()
        if 'Print' in keys or '*' in keys:
            lst = self.printKeyShortcuts if 'Print' in keys else self.mulKeyShortcuts
            lst.append(
                (self.sumByKey(filter(lambda x: x.lower() in ('alt', 'shift', 'ctrl'), keys.split('+')),
                               lambda x: Modifiers[x.lower()]),
                 callback)
            )
        else:
            keys = '+'.join(map(lambda x: self.qt_to_keyboard.get(x, x), keys.split('+')))
            keyboard.add_hotkey(keys, callback)

    def remove_hotkey(self, keys):
        keys = keys.toString()
        if 'Print' in keys or '*' in keys:
            lst = self.printKeyShortcuts if 'Print' in keys else self.mulKeyShortcuts
            lst.remove(sum(filter(lambda x: x.lower() in ('alt', 'shift', 'ctrl'),
                                  keys.split('+')), lambda x: Modifiers[x.lower()]))
        else:
            keys = '+'.join(map(lambda x: self.qt_to_keyboard.get(x, x), keys.split('+')))
            keyboard.remove_hotkey(keys)

    def reset_hotkeys(self):
        try:
            self.printKeyShortcuts.clear()
            self.mulKeyShortcuts.clear()
            keyboard.remove_all_hotkeys()
        except AttributeError:
            pass

    @staticmethod
    def sumByKey(iterable: iter, key: callable):
        return sum(map(key, iterable))


class EmptyStackException(Exception):
    pass


class Stack:
    def __init__(self, *args, max_size=float('inf')):
        self.__items = []
        self.__max_size = max_size
        for arg in args:
            self.push(arg)

    def push(self, value):
        self.__items.append(value)
        if len(self) > self.__max_size:
            self.__items.pop(0)

    def pop(self, default=None):
        if len(self.__items) > 0:
            return self.__items.pop()
        if default is None:
            raise EmptyStackException("Can't pop from an empty stack")
        return default

    def get_items(self):
        return self.__items

    def top(self, default=None):
        if len(self.__items) > 0:
            return self.__items[-1]
        if default is None:
            raise EmptyStackException("Can't read from an empty stack")
        return default

    def is_empty(self):
        return not bool(self)

    def clear(self):
        self.__items.clear()

    def __len__(self):
        return len(self.__items)

    def __str__(self):
        return str(self.__items)

    def __bool__(self):
        return bool(self.__items)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QKeySequence
    import sys

    app = QApplication(sys.argv)

    listener = QListener()
    listener.add_hotkey(QKeySequence('ctrl+shift+s'), lambda: print("ctrl+shift+print"))
    listener.add_hotkey(QKeySequence('*'), lambda: print("*"))
    listener.add_hotkey(QKeySequence('a'), lambda: print("a"))
    listener.start()

    sys.exit(app.exec_())


