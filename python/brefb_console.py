# script to display all the LCFToR float BREFB values for tuning mechanisms
# 20221030 CJH

import pickle
import datetime
import pandas as pd
import time
import os
import signal
import brEFB_CJH as brefb

console_df = None  # just in case we somehow miss a definition
dummy_df = None

# debug - pull the dummy df from the disk - really not necessary after I dubugged it
with open('console.pkl', 'rb') as f:
    dummy_df = pickle.load(f)
for col in ['td dec', 'td 256', 'sp dec', 'sp 256', 'P gain', 'I gain', 'D gain', 'rev', 'td min', 'td max']:
    dummy_df[col]='NA'


def get_updates():
    if None in brefb.ipdict.values():  # not sure what else to do
        # should I call the brefb.set_banks(verbose=True) again?
        # brefb.set_banks(verbose=False)
        return dummy_df

    confa = brefb.get_conf_df('a')
    state_a = brefb.current_state_df('a')
    confb = brefb.get_conf_df('b')
    state_b = brefb.current_state_df('b')

    temp_a = pd.concat([state_a, confa], axis=1)
    temp_b = pd.concat([state_b, confb], axis=1)
    temp_a['axis'] = 'A' + temp_a['axis'].astype(str)
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
            exit(1)
    except Exception as e:
        print(f'Unable to communicate with BREFB!' +
              f'\nAre we connected to animation network?')

    while True:
        os.system('cls')
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        msg = f'*** BREFB POLLING DATA FOR {now} ***  (press Ctrl-c to exit)'
        offset = (80 - len(msg)) // 2
        print(f'{" " * offset}{msg}')
        print(f'\nIP dict: {brefb.ipdict}\n')
        console_df = get_updates()
        print(console_df)
        time.sleep(1)