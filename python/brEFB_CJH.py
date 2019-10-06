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

ip='201'
# -------- WEB SECTION -----------
# Set up the urls that the br-EFB responds to
current_url = 'http://192.168.2.'+ip+'/current.php'
settings_url = 'http://192.168.2.'+ip+'/settings.php'
shows_url = 'http://192.168.2.'+ip+'/shows.php'
post_url = 'http://192.168.2.'+ip+'/command.php'

ipdict = {'a':'200','b':'201'}
def set_banks():
    ips=['200','201','202','203']
    for ip in ips:
        try:
            with urllib.request.urlopen('http://192.168.2.'+ip+'/settings.php',data=None, timeout=1.0) as url:
                data = json.loads(url.read().decode())
                dmx = data['first_channel']
                if int(dmx)==6:
                        ipdict['a']=ip
                elif int(dmx)==10:
                        ipdict['b']=ip
                print(f'found dmx {dmx} at ip {ip}')
        except ue.URLError:
            print(f'No answer at {ip}')
            #need to find some way of keeping myself from using the bad ips
    print(f"Set bank a to {ipdict['a']} and bank b to {ipdict['b']}")

def set_urls(bank='a'):
    '''probably a much cleaner way of doing this - one set for each, or a lambda for each'''
    global current_url, settings_url, shows_url, post_url
    if bank.lower() == 'a':
        ip = ipdict['a']
    else:
        ip = ipdict['b']
    current_url = 'http://192.168.2.'+ip+'/current.php'
    settings_url = 'http://192.168.2.'+ip+'/settings.php'
    shows_url = 'http://192.168.2.'+ip+'/shows.php'
    post_url = 'http://192.168.2.'+ip+'/command.php'

def get_brefb(brefb_url):
    '''generic function for returning one of the three json structures the br-EFB listens for'''
    with urllib.request.urlopen(brefb_url) as url:
        data = json.loads(url.read().decode())
    return data

def get_shows_df(bank='a'):
    '''define a pandas data frame with the current shows, axis config, etc'''
    set_urls(bank)
    show_data = get_brefb(shows_url)
    df = pd.DataFrame(show_data, columns =['name','length', 'frame_rate', 'steppable','end_action']) 
    return df

def get_conf_df(bank='a'):
    '''pandas df of the current br-EFB config'''
    set_urls(bank)
    conf = get_brefb(settings_url)
    df = pd.DataFrame(conf['axis'], columns = ['proportional_gain','integral_gain', 'derivative_gain','reversed','scaled_min','scaled_max'])
    return df

def play_show_urllib(show):
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

def play_show_requests(show):
    body = {"command":"play","value":show}
    jsondata = json.dumps(body)
    print (jsondata)
    response = requests.post(post_url, json=jsondata)
    print(f'Response from server using requests and json.dumps: {response.content}')
    response = requests.post(post_url, data=body)
    print(f'Response from server using requests and python dictionary: {response.content}')
    
def stop_show_requests():
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
    
def show_length(shows,show):
    '''return the length of a show in seconds'''
    return shows.values[show][1] / shows.values[show][2]

def current_state_df(bank='a'):
    ''' function to print the current state of the br-EFB'''
    set_urls(bank)
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
    sparkdata=[]
    for i in range(4):
        sparkdata.append(list(np.zeros(8)))
    brdata = []
    start = time.time()

    while time.time()-start < end_time:
        points = get_axes_values()     
        points.insert(0,time.time()-start)
        brdata.append(points)
        time.sleep(dt)
        #update_progress((time.time()-start)/end_time)
        for i in range(4):
            sparkdata[i].insert(0,points[2*(i+1)])
            sparkdata[i].pop()
        update_progress_sparkline((time.time()-start)/end_time, sparkdata)
    update_progress_sparkline(1,sparkdata)
    
    return brdata

def prepare_all_telemetry(end_time=30, dt=0.1,axes=4,bank='a'):
    '''Plot data from all axes (or only a selected axis) for a given time and step'''
    set_urls(bank)
    shows = get_shows_df()
    time_stamp = datetime.now()
    dt_string = time_stamp.strftime("%Y-%m-%d %H:%M:%S")
    label = shows.values[get_brefb(current_url)['current_show']][0] + f" (Bank {bank.upper()} at {dt_string} )"
    brdata = acquire_telemetry(end_time, dt, bank)
    df = pd.DataFrame(brdata, columns =['t', 'td 0', 'sp 0', 'td 1', 'sp 1', 'td 2', 'sp 2', 'td 3', 'sp 3']) 
    return df, label

def create_hvplot(df,label,axes=4):
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
# get rid of those two the have a vastly different width
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

def update_progress_sparkline(progress, sparkdata):
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
    for i in range(4):
        spark_string.append(sparkline(sparkdata[i],autoscale=False))
    block = int(round(bar_length * progress))
    clear_output(wait = True)
    text = f'Progress: [{"#"*block + "="*(bar_length-block)}] {100*progress:4.1f}%  0:{spark_string[0]:^8} 1:{spark_string[1]:^8} 2:{spark_string[2]:^8} 3:{spark_string[3]:^8}'
    print('\r',text,end='', flush=True)

# -------- ITEM CREATION SECTION -----------


# -------- UTILITY SECTION -----------



# -------- PICKLE SECTION -----------
def save_db(items,outfile=''):
    """Save the database to pkl format"""
    if outfile == '':
        outfile = 'RoD_Database.pkl'
    with open(outfile, 'wb') as fp:
        pickle.dump(items, fp)

def load_db(infile=''):
    """Save the database to pkl format"""
    if infile == '':
        infile = 'RoD_Database.pkl'
    with open(infile, 'rb') as fp:
        items = pickle.load(fp)
    return items

# -------- PANDAS SECTION -----------
# columns for the pandas save
xcel_cols_old = ['ITEM_NAME','Area','LEVEL','ITEM_TYPE','WORN','AC','WEAPON_TYPE','AVERAGE_DAMAGE','VALUE','STR','INT',
        'WIS','DEX','CON','CHA','LCK','HP','MANA','HIT_ROLL','DAMAGE_ROLL','GLANCE_DESCRIPTION',
        'SPECIAL_PROPERTIES','WEIGHT','GOLD', 'AFFECTS_LIST', 'DAMAGE', 'Manufactured',
        'Minimum Level', 'Mob', 'Out of Game', 'Pop','Known Keywords','CATEGORIES',
        'GENRES_ALLOWED','ARMOR_CLASS','EXAM_DESCRIPTION','HTTP_DESCRIPTION']
xcel_cols = ['ITEM_NAME', 'AREA', 'LEVEL', 'ITEM_TYPE', 'WORN', 'AC', 'WEAPON_TYPE', 'AVERAGE_DAMAGE', 'VALUE','STR',
             'INT', 'WIS', 'DEX', 'CON', 'CHA', 'LCK', 'HP', 'MANA', 'HIT_ROLL', 'DAMAGE_ROLL', 'GLANCE_DESCRIPTION',
             'SPECIAL_PROPERTIES', 'WEIGHT', 'GOLD', 'AFFECTS_LIST', 'DAMAGE', 'MANUFACTURED',
             'MINIMUM_LEVEL', 'MOB', 'OUT_OF_GAME', 'POP', 'KNOWN_KEYWORDS', 'CATEGORIES',
             'GENRES_ALLOWED', 'RACES_ALLOWED', 'ARMOR_CLASS', 'EXAM_DESCRIPTION', 'HTTP_DESCRIPTION']

def make_pandas_df(items,errors='ignore'):
    """Make a dataframe and make sure the right strings can be treated as numbers"""
    df = pd.DataFrame(items)
    #order them
    df = df[xcel_cols]
    numerics = ['LEVEL','AC','AVERAGE_DAMAGE','STR','INT','VALUE',
        'WIS','DEX','CON','CHA','LCK','HP','MANA','HIT_ROLL','DAMAGE_ROLL','WEIGHT','GOLD','MINIMUM_LEVEL']
    for col in numerics:
       #for excel you want to ignore, but for using in python you need to coerce
       #df[col]= pd.to_numeric(df[col], errors='ignore')
       #df[col] = pd.to_numeric(df[col], errors='coerce')
       df[col] = pd.to_numeric(df[col], errors=errors)
    df['AFFECTS'] = df.AFFECTS_LIST.apply(format_affects_list)
    return df

def save_pd_to_excel(df,outfile='',sheet_name=''):
    """Make the excel file formatted so that I never have to touch it manually"""
    if outfile=='':
        outfile = 'RodDatabase.xlsx'
    if sheet_name=='':
        sheet_name = 'CJH RoD DB v0.1 06212019'
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    # add columns created explicitly for pandas and excel
    pandas_cols = xcel_cols.copy()
    pandas_cols.insert(22,'AFFECTS')
    df.to_excel(writer, sheet_name=sheet_name, columns=pandas_cols)
    worksheet = writer.sheets[sheet_name]
    # Change the column widths - my imposed default is the length of the column name's string
    col_names= ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y','Z',
                'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL','AM','AN']
    for s, col in zip(pandas_cols, col_names):
        #apprently you can't just give it a single column name - have to use 'B:B' when you mean 'B'
        worksheet.set_column(col+':'+col, len(s)+3)
    # Item name and maybe a few other are the only ones I'll make bigger than default
    worksheet.set_column('B:B', 42)
    worksheet.set_column('C:C', 35)
    writer.save()

