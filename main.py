#! /usr/bin/python3

import curses as c
import copy
from common import *
import sys

debug = False

def main(w):
    global debug
    w.clear()
    w.refresh()
    filename = sys.argv[1]
    with open(filename, "r") as f:
        win = Window(f.read().splitlines(), filename)
    import init
    init.init(win)

    ch = None
    while True:
        # TODO: support A-<key> combos: https://stackoverflow.com/questions/22362076/how-to-detect-curses-alt-key-combinations-in-python
        w.clear()
        if debug:
            w.addstr(c.LINES - 1, 0, f"key: {repr(str(ch))}, type: {type(ch)}")
        win.display(w)
        ch = None
        try:
            ch = w.getkey()
        except:
            pass
        win.process_key(ch)
        w.refresh()

c.wrapper(main)
c.resetty()