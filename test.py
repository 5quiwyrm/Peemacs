
import curses as c
from common import *

def main(w):
    w.clear()
    w.refresh()
    ch = None
    while True:
        ch = w.getch()
        if ch == ord('q'):
            break
        elif ch == 27: # ALT
            w.nodelay(True)
            ch2 = w.getch()
            if ch2 == -1:
                break # Something bad?
            else:
                w.clear()
                w.addstr(0, 0, "A-" + chr(ch2))
                w.refresh()
            w.nodelay(False)
        else:
            w.clear()
            w.addstr(0, 0, c.keyname(ch))
            w.refresh()

c.wrapper(main)