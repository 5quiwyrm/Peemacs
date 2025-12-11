def ctrlise(key):
    return chr(ord(key) - ord('a') + 1)

def kill_range(original, start_idx, end_idx):
    return original[:start_idx] + original[end_idx:]

def insert(original, string, index):
    return original[:index] + string + original[index:]

class Window:
    def __init__(self, lines, filename):
        self.lines = lines
        self.filename = filename
        self._col = 0
        self._line = 0
        self.cursor = Cursor()
        self.key_bindings = {}
        self.vars = {}
        self.process_key = None
        self.display = None

class Cursor:
    def __init__(self):
        self.col = 0
        self.line = 0

