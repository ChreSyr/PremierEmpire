
class Memory:

    def __init__(self):

        with open('library\memory.txt', 'r') as reader:
            lines = reader.readlines()

        self.lang_id = None
        self.music_is_on = None
        self.volume_master = None
        self.volume_music = None
        self.volume_sfx = None
        self.volume_ui = None

        self._types = {
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

        with open('library\memory.txt', 'r') as reader:
            memory_lines = reader.readlines()
        memory_lines[self._keys.index(key)] = f"{key}:{value}\n"
        with open('library\memory.txt', 'w') as writer:
            for line in memory_lines:
                writer.write(line)
