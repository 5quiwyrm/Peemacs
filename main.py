#! /usr/bin/python3

import curses as c
import copy
from common import *
import sys

def main(w):
    w.clear()
    w.refresh()
    filename = sys.argv[1]
    with open(filename, "r") as f:
        state = State(f.read().splitlines(), filename)
    import init
    init.init(state)

    ch = None
    while True:
        w.clear()
        state.display(w)
        key = None
        try:
            ch = w.getch()
            if ch == 27: # ALT
                w.nodelay(True)
                chh = ""
                try:
                    chh = w.getkey()
                except:
                    break # something has gone very wrong
                w.nodelay(False)
                key = "a-" + chh
            else:
                key = (c.keyname(ch)).decode("utf-8")
        except:
            pass
        state.process_key(key)
        w.refresh()

c.wrapper(main)
c.resetty()