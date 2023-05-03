
import sys
import os
import pygame


class ScreenSize:

    def __init__(self, val):

        self.width = self.height = 0
        self.fullscreen = False

        if val == 'fullscreen':
            self.fullscreen = True

        elif type(val) == str:
            values = val.split(",")
            self.width = int(values[0])
            self.height = int(values[1])

        else:
            self.width = val[0]
            self.height = val[1]

    def __getitem__(self, item):

        if item == 0:
            return self.width
        if item == 1:
            return self.height
        return KeyError(f"A screen size only has 2 values")

    def __str__(self):

        if self.fullscreen:
            return "fullscreen"
        else:
            return f"{self.width},{self.height}"

    def get(self):

        if self.fullscreen:
            return pygame.display.list_modes()[0]
        else:
            return self.width, self.height


class Memory:

    def __init__(self):

        self.storage_path = resource_path("library\memory.txt")

        with open(self.storage_path, 'r') as reader:
            lines = reader.readlines()

        self.screen_size = None
        self.lang_id = None
        self.music_is_on = None
        self.volume_master = None
        self.volume_music = None
        self.volume_sfx = None
        self.volume_ui = None

        self._types = {
            'screen_size': ScreenSize,
            'lang_id': str,
            'music_is_on': int,
            'volume_master': float,
            'volume_music': float,
            'volume_sfx': float,
            'volume_ui': float,
        }
        self._keys = tuple(self._types.keys())

        for line in lines:
            if line.endswith('\n'):
                line = line[:-1]
            key, value = line.split(':')
            setattr(self, key, self._types[key](value))

    def set(self, key, value):

        if key not in self._keys:
            raise KeyError(f"{key} is not a memory attribute")

        try:
            value = self._types[key](value)
        except ValueError:
            raise ValueError(f"{value} is not convertible to {self._types[key]}")

        setattr(self, key, value)

        with open(self.storage_path, 'r') as reader:
            memory_lines = reader.readlines()
        memory_lines[self._keys.index(key)] = f"{key}:{value}\n"
        with open(self.storage_path, 'w') as writer:
            for line in memory_lines:
                writer.write(line)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)