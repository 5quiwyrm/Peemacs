from common import *

def handles_range(func):
    def inner(win, other, **kwargs):
        try:
            if len(win.vars["mark_range"]) == 2:
                win.vars["mark_range"] += [win.cursor.line, win.cursor.col]
            lb_line, lb_col, ub_line, ub_col = win.vars["mark_range"]
            if lb_line > ub_line:
                win.vars["mark_range"] = [ub_line, ub_col, lb_line, lb_col]
            elif lb_line == ub_line and lb_col > ub_col:
                win.vars["mark_range"] = [lb_line, ub_col, ub_line, lb_col]
        except:
            win.vars["mark_range"] = []
        return func(win, other, **kwargs)
    return inner

def backspace(win, _):
    try:
        backspace_mark(win, 0)
    except:
        backspace_no_mark(win, 0)
    win.vars["mark_range"] = []

@handles_range
def backspace_mark(win, _):
    lb_line, lb_col, ub_line, ub_col = win.vars["mark_range"]
    if lb_line == ub_line:
        win.lines[lb_line] = kill_range(
            win.lines[lb_line],
            lb_col,
            ub_col + 1)
    else:
        win.lines[lb_line] = win.lines[lb_line][:lb_col] + win.lines[ub_line][ub_col + 1:]
        win.lines = win.lines[:lb_line + 1] + win.lines[ub_line + 1:]
    win.cursor.line = lb_line
    win.cursor.col = lb_col

def backspace_no_mark(win, _):
    # TODO: [2] Implement regions and kill region (in progress)
    # This will be a significant change to the location code (not really no)
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
            up_padding = 10            
            win.cursor.col = len(win.lines[win.cursor.line])
            win.lines[win.cursor.line] += l
        else:
            c.beep()