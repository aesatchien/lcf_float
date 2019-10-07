# CJH trying to talk to the GilderFluke br-EFB
import urllib.request, json 
import urllib.error as ue
import requests
import pandas as pd
import time
from datetime import datetime
from IPython.display import clear_output
import matplotlib.pyplot as plt
import numpy as np


# -------- WEB SECTION -----------
# Set up the urls that the br-EFB responds to - this is deprecated, call set_banks to get them right
#ip='201'
#current_url = 'http://192.168.2.'+ip+'/current.php'
#settings_url = 'http://192.168.2.'+ip+'/settings.php'
#shows_url = 'http://192.168.2.'+ip+'/shows.php'
#post_url = 'http://192.168.2.'+ip+'/command.php'

# if there are no banks connected and somehow we call the plot functions use this for a dummy plot
dummy_data = [[0.055, -0.936, -1.0, -0.92, -0.99, -0.015, -0.98, -1.0, -0.97], [0.21, -0.93, -1.0, -0.92, -0.99, -0.014, -0.98, -1.0, -0.97], [0.39, -0.93, -1.0, -0.92, -0.99, -0.01, -0.98, -1.0, -0.97], [0.55, -0.93, -1.0, -0.92, -0.99, -0.014, -0.98, -1.0, -0.97]]
# initialize sparklines
sparks = {'a':np.zeros(8).tolist(),'b':np.zeros(8).tolist()}
ipdict = {'a':None,'b':None}
def set_banks():
    ips=['200','201','202','203']
    for ip in ips:
        try:
            with urllib.request.urlopen('http://192.168.2.'+ip+'/settings.php',data=None, timeout=0.75) as url:
                data = json.loads(url.read().decode())
                dmx = data['first_channel']
                if int(dmx)==6:
                        ipdict['a']=ip
                elif int(dmx)==10:
                        ipdict['b']=ip
                print(f'found dmx {dmx} at ip {ip}')
        except ue.URLError:
            pass
            #print(f'No answer at {ip}')
    print(f"Set bank a to {ipdict['a']} and bank b to {ipdict['b']}")

def set_urls(bank='a'):
    '''probably a much cleaner way of doing this - one set for each, or a lambda for each'''
    if ipdict[bank.lower()] is None:
          print(f"Bank {bank} not connected")
          return -1
    global current_url, settings_url, shows_url, post_url
    ip = ipdict[bank.lower()]
    current_url = 'http://192.168.2.'+ip+'/current.php'
    settings_url = 'http://192.168.2.'+ip+'/settings.php'
    shows_url = 'http://192.168.2.'+ip+'/shows.php'
    post_url = 'http://192.168.2.'+ip+'/command.php'
    return 0


def get_url(bank, target):
    '''single function to return a valid url... probably need to recheck validity every few minutes'''
    #ipdict = {'a': '999', 'b': '888'}
    http_base = 'http://192.168.2.'
    http_dict = {'current': '/current.php', 'settings': '/settings.php', 'shows': '/shows.php',
                 'command': '/command.php'}
    if target not in http_dict:
          print("Invalid target url")
          return -1 , ""
    if ipdict[bank.lower()] is None:
          print(f"Bank {bank} not connected")
          return -1 , ""
    url = http_base + ipdict[bank.lower()] + http_dict[target]
    return 0, url

def get_brefb(brefb_url):
    '''generic function for returning one of the three json structures the br-EFB listens for'''
    with urllib.request.urlopen(brefb_url) as url:
        data = json.loads(url.read().decode())
    return data

def get_shows_df(bank='a'):
    '''define a pandas data frame with the current shows, axis config, etc'''
    response, shows_url = get_url(bank,'shows')
    if response == -1:
          return
    show_data = get_brefb(shows_url)
    df = pd.DataFrame(show_data, columns =['name','length', 'frame_rate', 'steppable','end_action']) 
    return df

def get_conf_df(bank='a'):
    '''pandas df of the current br-EFB config'''
    response, settings_url = get_url(bank,'settings')
    if response == -1:
          return
    conf = get_brefb(settings_url)
    df = pd.DataFrame(conf['axis'], columns = ['proportional_gain','integral_gain', 'derivative_gain','reversed','scaled_min','scaled_max'])
    return df
    
def show_length(shows,show):
    '''return the length of a show in seconds'''
    return shows.values[show][1] / shows.values[show][2]

def current_state_df(bank='a'):
    ''' function to print the current state of the br-EFB'''
    response, current_url = get_url(bank,'current')
    if response == -1:
          return
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

def get_axes_values(bank='a'):
    ''' function to retrieve the current state of the br-EFB transducers and setpoints'''
    response, current_url = get_url(bank, 'current')
    if response == -1:
        return
    data = get_brefb(current_url)
    points = []
    for ix, axis in enumerate(data['axis']):
        points.append([data['axis'][ix]['input'], data['axis'][ix]['setpoint']])
    points = [item/2.0**15 for sublist in points for item in sublist]
    return points

def update_sparks(banks=['a','b']):
    global sparks
    for bank in [bank for bank in banks if ipdict[bank] is not None]:
        points = get_axes_values(bank)
        sparks[bank]= points

def acquire_telemetry(end_time=30, dt=0.1, bank='a', print_spark=True):
    '''return a list of axis data over time in the form time, trans 0, sp 0 ... trans 3, sp 3'''
    #initialization
    response, current_url = get_url(bank, 'current')
    if response == -1:
        return
    sparkdata=[]
    for i in range(4):
        sparkdata.append(list(np.zeros(8)))
    brdata = []
    start = time.time()

    while time.time()-start < end_time:
        points = get_axes_values(bank)
        points.insert(0,time.time()-start)
        brdata.append(points)
        time.sleep(dt)
        #update_progress((time.time()-start)/end_time)

        for i in range(4):
            sparkdata[i].insert(0,points[2*(i+1)])
            sparkdata[i].pop()
        update_progress_sparkline((time.time()-start)/end_time, sparkdata, print_spark)
    update_progress_sparkline(1,sparkdata,print_spark)
    
    return brdata

def prepare_all_telemetry(end_time=30, dt=0.1,axes=4,bank='a',print_spark=True):
    '''Plot data from all axes (or only a selected axis) for a given time and step'''
    response, current_url = get_url(bank, 'current')
    if response == -1:
        dummy_df = pd.DataFrame(dummy_data, columns =['t', 'td 0', 'sp 0', 'td 1', 'sp 1', 'td 2', 'sp 2', 'td 3', 'sp 3']) 
        return dummy_df, "Bank Not Connected, Dummy Data Shown"
    shows = get_shows_df(bank)
    time_stamp = datetime.now()
    dt_string = time_stamp.strftime("%Y-%m-%d %H:%M:%S")
    label = shows.values[get_brefb(current_url)['current_show']][0] + f" (Bank {bank.upper()} at {dt_string} )"
    brdata = acquire_telemetry(end_time, dt, bank, print_spark)
    df = pd.DataFrame(brdata, columns =['t', 'td 0', 'sp 0', 'td 1', 'sp 1', 'td 2', 'sp 2', 'td 3', 'sp 3']) 
    return df, label

# -------- PLOTTING OPTIONS -----------
def create_hvplot(df,label,axes=4):
    ''' use hvplot to display the data from brEFB'''
    #import hvplot
    import hvplot.pandas
    import holoviews as hv
    color=['blue','orange','green','red']
    if axes>3:
        ycols = {'trans':['td 0', 'td 1', 'td 2', 'td 3'],'setpoints':['sp 0', 'sp 1', 'sp 2', 'sp 3']}
    elif axes in {0,1,2,3}:
        td = 'td ' + str(axes)
        sp = 'sp ' + str(axes)
        # have to put them twice to trick bokeh into showing the legend - it won't for a single y value
        ycols = {'trans':[td,td], 'setpoints':[sp,sp]}
        color=color[axes]
    else:
        print('Invalid axis')
        return
        
    p1=df.hvplot(x='t', y=ycols['trans'], kind = 'scatter',color=color,
                   ylabel='br-EFB units', title=label, height = 400, width = 900, ylim=(-1.1,1.1))
    p2=df.hvplot(x='t', y=ycols['setpoints'], kind = 'line', line_dash='dashed',color=color,
                   ylabel='br-EFB units', title=label, height = 400, width = 900, ylim=(-1.1,1.1))
    p3= hv.HLine(0.0).opts(line_dash='dotted', color='black')
    return p1*p2*p3

def create_matplot(df,label,axes=4, save=False, fname='test.png'):
    ''' use matplotlib to display the data from brEFB'''
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
    return plt.show()

# -------- SPARKLINE AND CONSOLE OUTPUT -----------
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
    text = f'Progress: [{"#"*block + "="*(bar_length-block)}] {100*progress:.1f}%'
    print('\r',text,end='', flush=True)
          
# -*- coding: utf-8 -*-
# Unicode: 9601, 9602, 9603, 9604, 9605, 9606, 9607, 9608
#bar = '▁▂▃▄▅▆▇█'
# get rid of those two that have a vastly different width
bar = '▁▂▃▅▆▇'
          
barcount = len(bar)
 
def sparkline(numbers, autoscale=True):
    if autoscale:
        mn, mx = np.min(numbers), np.max(numbers)
    else:
        mn, mx = -1.0, 1.0
    extent = mx - mn
    sparkline = ''.join(bar[min([barcount - 1,int((n - mn) / extent * barcount)])] for n in numbers)
    return sparkline

def update_progress_sparkline(progress, sparkdata, print_spark = True):
    '''progress bar to look at while waiting for data'''
    bar_length = 10
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >=1:
        progress = 1
    spark_string=[]
    if print_spark:
        for i in range(4):
            spark_string.append(sparkline(sparkdata[i],autoscale=False))
    block = int(round(bar_length * progress))
    clear_output(wait = True)
    text = f'Progress: [{"#"*block + "="*(bar_length-block)}] {100*progress:4.1f}% '
    if print_spark:
        text = text + (f' 0:{spark_string[0]:^8} 1:{spark_string[1]:^8}' 
        + f' 2:{spark_string[2]:^8} 3:{spark_string[3]:^8} ')
    print('\r',text,end='', flush=True)


          
# -------- POSTING SECTION  -----------
def play_show_urllib(show, bank='a'):
    response, post_url = get_url(bank, 'command')
    if response == -1:
        return
    body = {
    "command":"play",
    "value":show
    }
    req = urllib.request.Request(post_url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(body)
    jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    print (jsondataasbytes)
    response = urllib.request.urlopen(req, jsondataasbytes)
    print(f'Response from server using urllib: {response.read()}')

def play_show_requests(show,bank='a'):
    response, post_url = get_url(bank, 'command')
    if response == -1:
        return
    body = {"command":"play","value":show}
    jsondata = json.dumps(body)
    print (jsondata)
    response = requests.post(post_url, json=jsondata)
    print(f'Response from server using requests and json.dumps: {response.content}')
    response = requests.post(post_url, data=body)
    print(f'Response from server using requests and python dictionary: {response.content}')
    
def stop_show_requests(bank='a'):
    response, post_url = get_url(bank, 'command')
    if response == -1:
        return
    body = {'command':'stop'}
    payload = '{"command":"stop"}'.encode('utf-8')
    jsondata = json.dumps(body)
    print (jsondata)
    # this jsondata one seems to send a '"{\\"command\\": \\"stop\\"}"'
    response = requests.post(post_url, json=jsondata)
    print(f'Response from server using requests and json.dumps: {response.content}')
    # this data=bode one seems to send 'command=stop'
    time.sleep(0.25)
    response = requests.post(post_url, data=body)
    print(f'Response from server using requests and python dictionary: {response.content}')
    time.sleep(0.25)
    response = requests.post(post_url, data=payload)
    print(f'Response from server using requests and a plain encoded string: {response.content}')


# -------- PICKLE SECTION -----------
# -------- PANDAS SECTION -----------


