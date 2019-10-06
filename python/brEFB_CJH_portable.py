# CJH trying to talk to the GilderFluke br-EFB
import urllib.request, json 
import requests
import pandas as pd
import time
from datetime import datetime
from IPython.display import clear_output
import matplotlib.pyplot as plt

ip_a='200'
ip_b='201'
ip='201'
# -------- WEB SECTION -----------
# Set up the urls that the br-EFB responds to
current_url = 'http://192.168.1.'+ip+'/current.php'
settings_url = 'http://192.168.1.'+ip+'/settings.php'
shows_url = 'http://192.168.1.'+ip+'/shows.php'
post_url = 'http://192.168.1.'+ip+'/command.php'

def set_urls(bank='a'):
    global current_url, settings_url, shows_url, post_url
    if bank.lower() == 'a':
        ip = ip_a
    else:
        ip = ip_b
    current_url = 'http://192.168.1.'+ip+'/current.php'
    settings_url = 'http://192.168.1.'+ip+'/settings.php'
    shows_url = 'http://192.168.1.'+ip+'/shows.php'
    post_url = 'http://192.168.1.'+ip+'/command.php'

def get_brefb(brefb_url):
    '''generic function for returning one of the three json structures the br-EFB listens for'''
    with urllib.request.urlopen(brefb_url) as url:
        data = json.loads(url.read().decode())
    return data

def get_shows_df():
    '''define a pandas data frame with the current shows, axis config, etc'''
    show_data = get_brefb(shows_url)
    df = pd.DataFrame(show_data, columns =['name','length', 'frame_rate', 'steppable','end_action']) 
    return df

def get_conf_df():
    '''pandas df of the current br-EFB config'''
    conf = get_brefb(settings_url)
    df = pd.DataFrame(conf['axis'], columns = ['proportional_gain','integral_gain', 'derivative_gain','reversed','scaled_min','scaled_max'])
    return df
    
def show_length(shows,show):
    '''return the length of a show in seconds'''
    return shows.values[show][1] / shows.values[show][2]

def current_state_df():
    ''' function to print the current state of the br-EFB'''
    brdata=[]
    axes_states = get_brefb(current_url)
    #print('Current state of axes:')
    for ix, axis in enumerate(axes_states['axis']):
        #print(f"Axis: {ix}  Transducer: {0.5*(axis['input']/2.0**15 +1) :3.3f}  or {int(128*(axis['input']/2.0**15+1)):3}/256" +
        #      f" __ Setpoint: {0.5*(axis['setpoint']/2.0**15 +1):3.3f}  or {int(128*(axis['setpoint']/2.0**15+1)):3}/256")
        brdata.append([ix,0.5*(axis['input']/2.0**15 +1),
                       int(128*(axis['input']/2.0**15+1)),
                      0.5*(axis['setpoint']/2.0**15 +1),
                      int(128*(axis['setpoint']/2.0**15+1))])
    df = pd.DataFrame(brdata, columns =['axis','transducer 01', 'transducer 256', 'setpoint 01', 'setpoint sp256']).round(3)
    return df

def get_axes_values():
    ''' function to retrieve the current state of the br-EFB transducers and setpoints''' 
    data = get_brefb(current_url)
    points = []
    for ix, axis in enumerate(data['axis']):
        points.append([data['axis'][ix]['input'], data['axis'][ix]['setpoint']])
    points = [item/2.0**15 for sublist in points for item in sublist]
    return points
    
def acquire_telemetry(end_time=30, dt=0.1, bank='a'):
    '''return a list of axis data over time in the form time, trans 0, sp 0 ... trans 3, sp 3'''
    #initialization
    set_urls(bank)
    brdata = []
    start = time.time()

    while time.time()-start < end_time:
        points = get_axes_values()     
        points.insert(0,time.time()-start)
        brdata.append(points)
        time.sleep(dt)
        update_progress((time.time()-start)/end_time)
    update_progress(1)
    return brdata

def prepare_all_telemetry(end_time=30, dt=0.1,axes=4,bank='a'):
    '''Plot data from all axes (or only a selected axis) for a given time and step'''
    set_urls(bank)
    shows = get_shows_df()
    time_stamp = datetime.now()
    dt_string = time_stamp.strftime("%Y-%m-%d %H:%M:%S")
    #label = shows.values[get_brefb(current_url)['current_show']][0] + f" (Bank {bank.upper()} at {dt_string} )"
    label = shows.values[get_brefb(current_url)['current_show']][0] + " (Bank {0} at {1} )".format(bank.upper(),dt_string)
    brdata = acquire_telemetry(end_time, dt, bank)
    df = pd.DataFrame(brdata, columns =['t', 'td 0', 'sp 0', 'td 1', 'sp 1', 'td 2', 'sp 2', 'td 3', 'sp 3']) 
    return df, label

def create_matplot(df,label,axes=4, save=False, fname='test.png'):
    # multiple line plot
    markersize = 3
    linewidth = 1.2
    colors=['blue', 'orange', 'green', 'red']
    plt.figure(num=None, figsize=(10,6),dpi=100)
    for i in range(4):
        plt.plot( 't', 'td '+str(i), data=df, marker='o', markerfacecolor=colors[i], markersize=markersize, color=colors[i], linewidth=0)
    for i in range(4):
        plt.plot( 't', 'sp '+str(i), data=df, marker='', color=colors[i], linewidth=linewidth, linestyle='dashed')
    #plt.legend()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.ylim(-1.1,1.1)
    plt.title(label)
    plt.xlabel('time (s)')
    plt.ylabel('scaled br-EFB units')
    if save:
        plt.savefig(fname)
    #return plt.show()
    return

def update_progress(progress):
    '''progress bar to look at while waiting for data'''
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >=1:
        progress = 1
        
    block = int(round(bar_length * progress))
    clear_output(wait = True)
    #text = f'Progress: [{"#"*block + "="*(bar_length-block)}] {100*progress:.1f}%'
    text =  'Progress: [{}] {:.1f}%'.format("#"*block + "="*(bar_length-block),100*progress)
    print(text,end='\r', flush=True)


