from common import *

def backspace(win, _):
    # TODO: [2] Implement regions and kill region
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