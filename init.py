from common import *
import curses as c
from templates import *
import copy
import glob

def init(state):
    # TODO: by popular demand (one person), a vim mode should be implemented as an alterative, init_vim.py
    win = state.win()
    win.key_bindings["KEY_UP"] = move_up
    win.key_bindings["KEY_DOWN"] = move_down
    win.key_bindings["KEY_LEFT"] = move_left
    win.key_bindings["KEY_RIGHT"] = move_right
    win.key_bindings["KEY_BACKSPACE"] = backspace
    win.key_bindings["KEY_RESIZE"] = noop
    win.key_bindings["^J"] = type_enter
    win.key_bindings[ctrlise('w')] = save_file
    win.key_bindings["^I"] = tab
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
    state.process_key = lambda s: process_key(state, s)
    state.display = lambda w: display(state, w)
    win.vars["message"] = ""
    win.vars["ctrlx"] = False
    win.vars["ctrlx_answer"] = ""

def noop(a, _):
    pass

def display(state, w):
    win = state.win()
    x = 0
    bottom_lines = 2
    if "message" not in win.vars:
        win.vars["message"] = ""
    if "ctrlx" not in win.vars:
        win.vars["ctrlx"] = False
    if "ctrlx_answer" not in win.vars:
        win.vars["ctrlx_answer"] = ""
    longest_number = len(str(len(win.lines) - 1))
    while x < c.LINES - bottom_lines and x + win._line < len(win.lines):
        w.addnstr(x, 0, win.lines[x + win._line][win._col:], c.COLS)
        x += 1
        if x >= len(win.lines):
            break
    w.addnstr(c.LINES - 2, 0, statusline(state), c.COLS)
    if not win.vars["ctrlx"]:
        w.addnstr(c.LINES - 1, 0, win.vars["message"], c.COLS)
        w.move(min(c.LINES - 1, win.cursor.line - win._line), min(c.COLS - 1, win.cursor.col - win._col))
        win.vars["message"] = ""
    else:
        w.addnstr(c.LINES - 1, 0, ("^X: " + win.vars["ctrlx_answer"]), c.COLS)
        w.move(c.LINES - 1, 4 + len(win.vars["ctrlx_answer"]))

def statusline(state):
    win = state.win()
    return f"[{state.windows_head}]: {win.filename}:{win.cursor.line}:{win.cursor.col}"

def process_key(state, key):
    win = state.win()
    if win.vars["ctrlx"]:
        sk = str(key)
        if sk == "^J":
            exec_command(state, win.vars["ctrlx_answer"])
        elif sk == "^I":
            win.vars["ctrlx_answer"] += "    "
        elif sk == "KEY_BACKSPACE":
            if win.vars["ctrlx_answer"] != "":
                win.vars["ctrlx_answer"] = win.vars["ctrlx_answer"][:-1]
        elif sk == ctrlise('x'):
            win.vars["ctrlx_answer"] = ""
        elif sk.startswith("a-"):
            pass
        elif sk == "~" or (key != None and ord(key[0]) >= 32) and len(sk) == 1:
            win.vars["ctrlx_answer"] += sk
        else:
            c.beep()
    else:
        try:
            f = win.key_bindings[str(key)]
            try:
                try:
                    f(win, key)
                except:
                    f(state, key)
            except Exception as e:
                win.vars["message"] = str(e)
        except:
            win.vars["message"] = str(key) + " : " + str(type(key))
            if key.startswith("a-"):
                pass 
            elif key == "~" or (key != None and ord(key[0]) >= 32):
                if not ("block_typing" in win.vars):
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
    if isinstance(win, Window):
        exec_command(win, win.vars["ctrlx_answer"])
    else:
        return "not a window"

def exec_command(state, cmd):
    win = state.win()
    win.vars["ctrlx"] = False

    def open_file(filename, create = False):
        open_mode = "r"
        if create:
            open_mode = "a+"
        with open(filename, open_mode) as f:
            if create:
                f.write("\n")
            state.new_win(f.read().splitlines(), filename)
            init(state)

    def goto_line(line):
        if line >= len(win.lines) or line < 0:
            c.beep()
            return "line out of range!"
        win.cursor.line = line
        win._line = max(0, line - up_padding)

    def create_file(filename):
        with open(file, "a+") as f:
            f.write("\n")
            state.new_win([""], filename)
            init(state)

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

    def ls(path = ".", pattern = "/**/*"):
        import os
        paths = glob.glob(path + pattern, recursive = True)
        state.new_win(paths, f"ls(path = {repr(path)}, pattern = {repr(pattern)})")
        win = state.win()
        win.key_bindings["KEY_UP"] = move_up
        win.key_bindings["KEY_DOWN"] = move_down
        win.key_bindings["KEY_LEFT"] = move_left
        win.key_bindings["KEY_RIGHT"] = move_right
        win.key_bindings["KEY_BACKSPACE"] = noop
        win.key_bindings["KEY_RESIZE"] = noop
        win.key_bindings[ctrlise('x')] = ctrlx

        def open_file_at_line(x, _):
            win = state.win()
            open_file(win.lines[win.cursor.line])
        
        win.key_bindings["^J"] = open_file_at_line

        win.vars["message"] = ""
        win.vars["ctrlx"] = False
        win.vars["ctrlx_answer"] = ""
        win.vars["block_typing"] = True

    def ls_buf():
        state.new_win(list(a.filename for a in state.windows) + ["*ls_buf"], "*ls_buf")
        win = state.win()
        win.key_bindings["KEY_UP"] = move_up
        win.key_bindings["KEY_DOWN"] = move_down
        win.key_bindings["KEY_LEFT"] = move_left
        win.key_bindings["KEY_RIGHT"] = move_right
        win.key_bindings["KEY_BACKSPACE"] = noop
        win.key_bindings["KEY_RESIZE"] = noop
        win.key_bindings[ctrlise('x')] = ctrlx

        def open_buf_at_line(state, _):
            prev_head = state.windows_head
            state.windows_head = state.win().cursor.line
            state.windows.pop(prev_head)        
        win.key_bindings["^J"] = open_buf_at_line

        def kill_buf_at_line(state, _):
            win = state.win()
            if win.cursor.line == len(state.windows) - 1:
                c.beep()
                return
            else:
                if state.windows[win.cursor.line].filename[0] == '*':
                    c.beep()
                    return
                state.windows.pop(win.cursor.line)
            win.cursor.line -= 1
            if win.cursor.line < 0:
                win.cursor.line = 0
            state.windows_head = len(state.windows) - 1
            state.windows[state.windows_head].lines = list(a.filename for a in state.windows)
        win.key_bindings[ctrlise('k')] = kill_buf_at_line

        win.vars["message"] = ""
        win.vars["ctrlx"] = False
        win.vars["ctrlx_answer"] = ""
        win.vars["block_typing"] = True
    lb = ls_buf

    def ls_todo(path = "."):
        todos = []
        paths = glob.glob(path + "/**/*", recursive = True)
        for p in paths:
            with open(p, "r") as f:
                lines = f.read().splitlines()
                for (idx, l) in enumerate(lines):
                    cl = copy.deepcopy(l)
                    cl = cl.strip()
                    if cl.startswith("# TODO: "):
                        todos.append(f"{p}:{idx} | {l.strip()}")
        def todo_urgency(todo):
            _, message = todo.split("# TODO: ", 1)
            if message.startswith("["):
                try:
                    return int(message[1:].split("]", 1)[0]) # this gets the number in a string like this: [<num>]...
                except:
                    return -1
            else:
                return 0
        todos.sort(key = todo_urgency, reverse = True)
        state.new_win(todos, f"ls_todo(path = {repr(path)})")
        win = state.win()
        win.key_bindings["KEY_UP"] = move_up
        win.key_bindings["KEY_DOWN"] = move_down
        win.key_bindings["KEY_LEFT"] = move_left
        win.key_bindings["KEY_RIGHT"] = move_right
        win.key_bindings["KEY_BACKSPACE"] = noop
        win.key_bindings["KEY_RESIZE"] = noop
        win.key_bindings[ctrlise('x')] = ctrlx

        def reload_todos(state, _):
            todos = []
            paths = glob.glob(path + "/**/*", recursive = True)
            for p in paths:
                with open(p, "r") as f:
                    lines = f.read().splitlines()
                    for (idx, l) in enumerate(lines):
                        cl = copy.deepcopy(l)
                        cl = cl.strip()
                        if cl.startswith("# TODO: "):
                            todos.append(f"{p}:{idx} | {l.strip()}")
            todos.sort(key = todo_urgency, reverse = True)
            state.win().lines = todos

        win.key_bindings[ctrlise('r')] = reload_todos

        win.vars["message"] = ""
        win.vars["ctrlx"] = False
        win.vars["ctrlx_answer"] = ""
        win.vars["block_typing"] = True

        def open_todo_at_line(state, _):
            win = state.win()
            line = win.lines[win.cursor.line]
            path, rest = line.split(":", 1)
            line_num, rest = rest.split(" | ", 1)
            open_file(path.strip())
            init(state)
            try:
                state.win().cursor.line = int(line_num)
                state.win()._line = max(0, int(line_num) - up_padding)
            except:
                return "unreachable: bad line number"
        win.key_bindings['^J'] = open_todo_at_line

        def open_todo_at_line_new_win(state, _):
            win = state.win()
            line = win.lines[win.cursor.line]
            path, rest = line.split(":", 1)
            line_num, rest = rest.split(" | ", 1)
            state.new_win([""], "")
            open_todo_at_line(path.strip())
            init(state)
            try:
                state.win().cursor.line = int(line_num)
                state.win()._line = max(0, int(line_num) - up_padding)
            except:
                return "unreachable: bad line number"
        win.key_bindings['^I'] = open_todo_at_line_new_win
    
    def next_buf():
        state.windows_head += 1
        if state.windows_head >= len(state.windows):
            state.windows_head = 0
    nb = next_buf

    def prev_buf():
        state.windows_head -= 1
        if state.windows_head < 0:
            state.windows_head = len(state.windows) - 1
    pb = prev_buf

    def kill_buf():
        state.windows.pop(state.windows_head)
        prev_buf()
    kb = kill_buf

    try:
        result = eval(cmd)
        try:
            result()
        except:
            pass
        win.vars["message"] = str(result)
    except Exception as e:
        win.vars["message"] = str(e)