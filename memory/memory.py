
class Memory:

    def __init__(self):

        with open('memory\memory.txt', 'r') as reader:
            lines = reader.readlines()

        self.lang_id = lines[0][5:7]

    def set_lang(self, lang_id):

        if lang_id == self.lang_id:
            return

        self.lang_id = lang_id

        with open('memory\memory.txt', 'r') as reader:
            memory_lines = reader.readlines()
        memory_lines[0] = "lang:" + lang_id + "\n"
        with open('memory\memory.txt', 'w') as writer:
            for line in memory_lines:
                writer.write(line)
