# script to display all the LCFToR float BREFB values for tuning mechanisms
# 20221030 CJH

import curses
import datetime
import pandas as pd
import time
import os
import signal
import brEFB_CJH as brefb

console_df = None  # just in case we somehow miss a definition
dummy_df = None

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
    # if None in brefb.ipdict.values():  # not sure what else to do
    #     # should I call the brefb.set_banks(verbose=True) again?
    #     # brefb.set_banks(verbose=False)
    #     return dummy_df

    if list(brefb.ipdict.values())[0] == None:
        temp_a = dummy_df.iloc[0:4]
    else:
        confa = brefb.get_conf_df('a')
        state_a = brefb.current_state_df('a')
        temp_a = pd.concat([state_a, confa], axis=1)
        temp_a['axis'] = 'A' + temp_a['axis'].astype(str)
    if list(brefb.ipdict.values())[1] == None:
        temp_b = dummy_df.iloc[4:]
    else:
        confb = brefb.get_conf_df('b')
        state_b = brefb.current_state_df('b')
        temp_b = pd.concat([state_b, confb], axis=1)
        temp_b['axis'] = 'B' + temp_b['axis'].astype(str)

    console_df = pd.concat([temp_a, temp_b])
    console_df.columns = ['axis', 'td dec', 'td 256', 'sp dec', 'sp 256', 'P gain', 'I gain', 'D gain', 'rev', 'td min',
                          'td max']
    return console_df

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)
signal.signal(signal.SIGINT, handler)

if __name__ == '__main__':

    try:
        print('- Program to monitor the transducers, SPs and PIDs of the BrEFBs - ')
        print('Connecting to brefbs...')
        brefb.set_banks(verbose=True)
        if None in brefb.ipdict.values():
            print(f'Unable to communicate with BREFB a and b!' +
                  f'\n1) Are we connected to animation network?' +
                  f'\n2) Are the BREFBs powered up?\n' +
                  f'exiting!')
            # exit(1)
    except Exception as e:
        print(f'Unable to communicate with BREFB!' +
              f'\nAre we connected to animation network?')

    while True:
        console_df = get_updates()
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        msg = f'*** BREFB POLLING DATA FOR {now} ***  (press Ctrl-c to exit)'
        offset = (80 - len(msg)) // 2
        os.system('clear')
        print(f'{" " * offset}{msg}')
        print(f'\nIP dict: {brefb.ipdict}\n')
        print(console_df, flush=True)
        time.sleep(1)