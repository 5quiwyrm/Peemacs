from common import *
import curses as c

def init(win):
    win.key_bindings["KEY_UP"] = move_up
    win.key_bindings["KEY_DOWN"] = move_down
    win.key_bindings["KEY_LEFT"] = move_left
    win.key_bindings["KEY_RIGHT"] = move_right
    win.key_bindings["KEY_BACKSPACE"] = backspace
    win.key_bindings["KEY_RESIZE"] = noop
    win.key_bindings["\n"] = type_enter
    win.key_bindings[ctrlise('w')] = save_file
    win.key_bindings["\t"] = tab
    win.key_bindings[ctrlise('e')] = end
    win.key_bindings[ctrlise('a')] = home
    win.key_bindings[ctrlise('r')] = reload_editor
    win.key_bindings[ctrlise('d')] = page_down
    win.key_bindings[ctrlise('u')] = page_up
    win.key_bindings[ctrlise('x')] = ctrlx
    win.key_bindings[ctrlise('k')] = del_line
    win.key_bindings[ctrlise('g')] = repeat_cmd
    win.key_bindings[ctrlise('f')] = next_word
    win.key_bindings[ctrlise('b')] = prev_word
    win.process_key = lambda s: process_key(win, s)
    win.display = lambda w: display(win, w)
    win.vars["message"] = ""
    win.vars["ctrlx"] = False
    win.vars["ctrlx_answer"] = ""

def noop(win, _):
    pass

def display(win, w):
    x = 0
    bottom_lines = 0
    if win.vars["message"] != "" or win.vars["ctrlx"]:
        bottom_lines += 1
    while x < c.LINES - bottom_lines and x + win._line < len(win.lines):
        w.addnstr(x, 0, win.lines[x + win._line][win._col:], c.COLS)
        x += 1
        if x >= len(win.lines):
            break 
    if not win.vars["ctrlx"]:
        w.addnstr(c.LINES - 1, 0, win.vars["message"], c.COLS)
        w.move(win.cursor.line - win._line, win.cursor.col - win._col)
        win.vars["message"] = ""
    else:
        w.addnstr(c.LINES - 1, 0, ("^X: " + win.vars["ctrlx_answer"]), c.COLS)
        w.move(c.LINES - 1, 4 + len(win.vars["ctrlx_answer"]))

def process_key(win, key):
    if win.vars["ctrlx"]:
        sk = str(key)
        if sk == "\n":
            exec_command(win, win.vars["ctrlx_answer"])
        elif sk == "\t":
            win.vars["ctrlx_answer"] += "    "
        elif sk == "KEY_BACKSPACE":
            if win.vars["ctrlx_answer"] != "":
                win.vars["ctrlx_answer"] = win.vars["ctrlx_answer"][:-1]
        elif sk == ctrlise('k'):
            win.vars["ctrlx_answer"] = ""
        elif sk == "~" or (key != None and ord(key[0]) >= 32) and len(sk) == 1:
            win.vars["ctrlx_answer"] += sk
        else:
            c.beep()
    else:
        try:
            f = win.key_bindings[str(key)]
            try:
                f(win, key)
            except Exception as e:
                win.vars["message"] = str(e)
        except:
            win.vars["message"] = str(key)
            if key == "~" or (key != None and ord(key[0]) >= 32):
                type_key(win, key)
            else:
                c.beep()

def type_key(win, key):
    win.lines[win.cursor.line] = insert(
        win.lines[win.cursor.line],
        str(key),
        win.cursor.col
    )
    win.cursor.col += len(str(key))

up_padding = 10
def move_up(win, _):
    if win.cursor.line != 0:
        win.cursor.line -= 1
        if win.cursor.col > len(win.lines[win.cursor.line]):
            win.cursor.col = len(win.lines[win.cursor.line])
        if win.cursor.line - up_padding < win._line:
            win._line = max(0, win.cursor.line - up_padding)
    else:
        c.beep()

down_padding = 10
def move_down(win, _):
    if win.cursor.line < len(win.lines) - 1:
        win.cursor.line += 1
        if win.cursor.col > len(win.lines[win.cursor.line]):
            win.cursor.col = len(win.lines[win.cursor.line])
        if win.cursor.line + down_padding > win._line + c.LINES:
            win._line = min(len(win.lines), win.cursor.line + down_padding - c.LINES)
    else:
        c.beep()

def move_left(win, _):
    if win.cursor.col != 0:
        win.cursor.col -= 1
        return True
    else:
        if win.cursor.line != 0:
            win.cursor.line -= 1 # No race condition here
            win.cursor.col = len(win.lines[win.cursor.line])
            return True
        else:
            c.beep()
            return False

def move_right(win, _):
    if win.cursor.col != len(win.lines[win.cursor.line]):
        win.cursor.col += 1
        return True
    else:
        if win.cursor.line != len(win.lines) - 1:
            win.cursor.line += 1
            win.cursor.col = 0
            return True
        else:
            c.beep()
            return False

def backspace(win, _):
    # TODO: Implement regions and kill region
    if win.cursor.col != 0:
        win.lines[win.cursor.line] = kill_range(
            win.lines[win.cursor.line],
            win.cursor.col - 1,
            win.cursor.col
        )
        win.cursor.col -= 1
    else:
        if win.cursor.line != 0:
            l = win.lines.pop(win.cursor.line)
            win.cursor.line -= 1
            win.cursor.col = len(win.lines[win.cursor.line])
            win.lines[win.cursor.line] += l
        else:
            c.beep()

def type_enter(win, _):
    l = win.lines[win.cursor.line]
    win.lines[win.cursor.line] = l[:win.cursor.col]
    win.lines.insert(win.cursor.line + 1, l[win.cursor.col:])
    win.cursor.line += 1
    win.cursor.col = 0

def save_file(win, _):
    with open(win.filename, "w") as f:
        written = f.write("\n".join(win.lines))
    win.vars["message"] = f"saved {len(win.lines)} lines, {written} bytes"

def tab(win, _):
    type_key(win, "    ")

def end(win, _):
    win.cursor.col = len(win.lines[win.cursor.line])

def home(win, _):
    win.cursor.col = 0

def reload_editor(win, _):
    win = Window(win.lines, win.filename)
    init(win)

def page_down(win, _):
    og = win.cursor.line
    win.cursor.line = min(max(0, len(win.lines) - 1), win.cursor.line + c.LINES)
    win.cursor.col = min(len(win.lines[win.cursor.line]), win.cursor.col)
    win._line += win.cursor.line - og

def page_up(win, _):
    og = win.cursor.line
    win.cursor.line = max(0, win.cursor.line - c.LINES)
    win.cursor.col = min(len(win.lines[win.cursor.line]), win.cursor.col)
    win._line -= og - win.cursor.line
    if win._line < 0:
        win._line = 0

def del_line(win, _):
    win.lines.pop(win.cursor.line)
    win.cursor.col = 0
    if win.cursor.line != 0:
        win.cursor.line -= 1

def next_word(win, _):
    while True:
        try:
            ch = win.lines[win.cursor.line][win.cursor.col]
        except:
            ch = " "
        if not ch.isspace():
            break
        success = move_right(win, 0)
        if not success:
            return
    try:
        while not win.lines[win.cursor.line][win.cursor.col].isspace():
            success = move_right(win, 0)
            if not success:
                return
    except:
        pass

def prev_word(win, _):
    while True:
        try:
            ch = win.lines[win.cursor.line][win.cursor.col]
        except:
            ch = " "
        if not ch.isspace():
            break
        success = move_left(win, 0)
        if not success:
            return
    try:
        while not win.lines[win.cursor.line][win.cursor.col].isspace():
            if ch.isspace():
                break
            success = move_left(win, 0)
            if not success:
                return
    except:
        pass

def ctrlx(win, _):
    win.vars["ctrlx"] = True

def repeat_cmd(win, _):
    exec_command(win, win.vars["ctrlx_answer"])

def exec_command(win, cmd):
    win.vars["ctrlx"] = False
    
    def open_file(filename):
        with open(filename, "r") as f:
            win.lines = f.read().splitlines()
            win._line = 0
            win._col = 0
            win.cursor.line = 0
            win.cursor.col = 0
            win.filename = filename

    def find(pattern):
        if win.cursor.col != len(win.lines[win.cursor.line]):
            f = win.lines[win.cursor.line][win.cursor.col + 1:].find(pattern)
            if f != -1:
                win.cursor.col += 1 + f
                return f"found on current line, col {f}"
        if win.cursor.line + 1 >= len(win.lines):
            return "exhausted search, try bfind(pattern)"
        for (i, l) in enumerate(win.lines[win.cursor.line + 1:]):
            f = l.find(pattern)
            if f != -1:
                win.cursor.line += 1 + i
                win._line = min(max(0, len(win.lines) - down_padding), win.cursor.line - down_padding)
                win.cursor.col = f
                return f"found on line {win.cursor.line + i + 1}, col {f}"
        return "exhausted search, try bfind(pattern)"

    def bfind(pattern):
        if win.cursor.col != 0:
            f = win.lines[win.cursor.line][:win.cursor.col].find(pattern)
            if f != -1:
                win.cursor.col = f
                return f"found on current line, col {f}"
        if win.cursor.line == 0:
            return "exhausted search, try find(pattern)"
        for (i, l) in enumerate(win.lines[:win.cursor.line]):
            f = l.find(pattern)
            if f != -1:
                win.cursor.line = l
                win.cursor.col = f
                win._line = max(0, l - up_padding)
                return f"found on line {win.cursor.line}, col {f}"
        return "exhausted search, try find(pattern)"

    try:
        result = eval(cmd)
        win.vars["message"] = str(result)
    except Exception as e:
        win.vars["message"] = str(e)