# script to display all the LCFToR float BREFB values for tuning mechanisms
# NOTE: for curses to work on windows you have to call with winpty python script.py
# 20221030 CJH

import curses
import datetime
import pandas as pd
import brEFB_CJH as brefb

console_df = None  # just in case we somehow miss a definition

# empty df in case we don't have connectivity
dummy_data = {'axis': {0: 'A0',  1: 'A1',  2: 'A2',  3: 'A3',  4: 'B0',  5: 'B1',  6: 'B2',  7: 'B3'},
'td dec': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'td 256': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'sp dec': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'sp 256': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'P gain': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'I gain': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'D gain': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'rev': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'td min': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'},
'td max': {0: '----',  1: '----',  2: '----',  3: '----',  4: '----',  5: '----',  6: '----',  7: '----'}}
dummy_df = pd.DataFrame(dummy_data)



def get_updates():

    if list(brefb.ipdict.values())[0] == None:
        temp_a = dummy_df.iloc[0:4]  # just show blanks
    else:
        confa = brefb.get_conf_df('a')
        state_a = brefb.current_state_df('a')
        temp_a = pd.concat([state_a, confa], axis=1)
        temp_a['axis'] = 'A' + temp_a['axis'].astype(str)
    if list(brefb.ipdict.values())[1] == None:
        temp_b = dummy_df.iloc[4:]  # just show blanks
    else:
        confb = brefb.get_conf_df('b')
        state_b = brefb.current_state_df('b')
        temp_b = pd.concat([state_b, confb], axis=1)
        temp_b['axis'] = 'B' + temp_b['axis'].astype(str)

    console_df = pd.concat([temp_a, temp_b])
    console_df.columns = ['axis', 'td dec', 'td 256', 'sp dec', 'sp 256', 'P gain', 'I gain', 'D gain', 'rev', 'td min',
                          'td max']
    return console_df

if __name__ == '__main__':
    screen = curses.initscr()
    warning_line = 20
    screen.clear()
    curses.cbreak()
    screen.nodelay(True) # take character input

    try:
        screen.addstr(0, 0, '- Program to monitor the transducers, SPs and PIDs of the BrEFBs - ')
        screen.addstr(1, 0, 'Connecting to brefbs...')
        screen.refresh()
        brefb.set_banks(verbose=True)
        if None in list(brefb.ipdict.values()):
            screen.addstr(warning_line, 0, f'Unable to communicate with both BREFB a and b!' +
                  f'\n1) Are we connected to animation network?' +
                  f'\n2) Are the BREFBs powered up?\n' +
                  f'Consider exiting!')
            screen.refresh()
            curses.napms(2000)
            screen.clear()
            # exit(1)
    except Exception as e:
        screen.addstr(warning_line, 0, f'Unable to communicate with BREFB!' +
              f'\nAre we connected to animation network?')

    # add a few colors to make life easier
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    while True:
        console_df = get_updates()
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        msg = f'*** BREFB POLLING DATA FOR {now} ***'
        offset = (80 - len(msg)) // 2

        # Update the buffer, adding text at different locations
        screen.addstr(0, 0, f'{" " * offset}{msg}', curses.A_BOLD)
        screen.addstr(2, 0, f'IP dict: {brefb.ipdict}\n')  # Python 3 required for unicode
        s = console_df.to_string().split('\n')
        screen.addstr(4, 0, s[0], curses.A_BOLD)
        screen.addstr(5, 0, '\n'.join(s[1:5]), curses.color_pair(2) | curses.A_BOLD)
        screen.addstr(9, 0, '\n'.join(s[5:]), curses.color_pair(3) | curses.A_BOLD)

        quit_msg = f'press q to quit: '
        screen.addstr(warning_line, len(quit_msg), ' ')  # clear non-quittng characters
        screen.addstr(warning_line, 0, quit_msg, curses.color_pair(1) | curses.A_BOLD)

        curses.curs_set(True) # lose the blinking cursor

        c = screen.getch()  # break if we hit the q key, note nodelay() is on
        if c == ord('q'):
            screen.addstr(warning_line, 0, f'Exit key pressed ... Goodbye!')
            screen.refresh()
            curses.napms(2500)
            break
        # Changes go in to the screen buffer and only get displayed after calling `refresh()` to update
        screen.refresh()
        curses.napms(1000)

    # put the console back to normal
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()
