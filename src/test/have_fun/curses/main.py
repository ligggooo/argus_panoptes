import curses
from curses.textpad import rectangle,Textbox
import traceback

def main(stdscr):
    stdscr.addstr(0, 0, "Enter IM message: (hit Ctrl-G to send)")

    editwin = curses.newwin(5,30, 2,1)
    rectangle(stdscr, 1,0, 1+5+1, 1+30+1)
    stdscr.refresh()

    box = Textbox(editwin)

    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    message = box.gather()
    return message

stdscr=curses.initscr()
  
  # Turn off echoing of keys, and enter cbreak mode,
   # where no buffering is performed on keyboard input
curses.noecho()
curses.cbreak()
  
  # In keypad mode, escape sequences for special keys
   # (like the cursor keys) will be interpreted and
   # a special value like curses.KEY_LEFT will be returned
stdscr.keypad(1)
try:
    print(main(stdscr))
    stdscr.keypad(0)
    input()
except Exception as e:
    traceback.print_exec() 
  # Enter the main loop
   # Set everything back to normal

curses.echo()
curses.nocbreak()
curses.endwin() 
  # Terminate curses
   