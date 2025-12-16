def ctrlise(key):
    return "^" + key.upper()

def altise(key):
    return "a-" + key

def kill_range(original, start_idx, end_idx):
    return original[:start_idx] + original[end_idx:]

def insert(original, string, index):
    return original[:index] + string + original[index:]

class State:
    def __init__(self, lines, filename):
        self.windows = []
        self.windows_head = 0
        self.windows.append(Window(lines, filename))
        self.display = None     # State -> None
        self.process_key = None # State -> ch -> None

    def win(self):
        return self.windows[self.windows_head]

    def new_win(self, lines, filename):
        self.windows.append(Window(lines, filename))
        self.windows_head = len(self.windows) - 1

class Window:
    def __init__(self, lines, filename):
        self.lines = lines
        self.filename = filename
        self._col = 0
        self._line = 0
        self.cursor = Cursor()
        self.key_bindings = {}
        self.vars = {}

class Cursor:
    def __init__(self):
        self.col = 0
        self.line = 0