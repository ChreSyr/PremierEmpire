
class Memory:

    def __init__(self):

        with open('library\memory.txt', 'r') as reader:
            lines = reader.readlines()

        self.lang_id = lines[0][5:-1]

    def set_lang(self, lang_id):

        if lang_id == self.lang_id:
            return

        self.lang_id = lang_id

        with open('library\memory.txt', 'r') as reader:
            memory_lines = reader.readlines()
        memory_lines[0] = "lang:" + lang_id + "\n"
        with open('library\memory.txt', 'w') as writer:
            for line in memory_lines:
                writer.write(line)
