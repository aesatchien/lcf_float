#!/usr/bin/python
# coding: utf-8

import serial
import io
import time
import threading
import sys
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import re
from datetime import datetime
import sys


# #### Need to:
# #####  1  Poll requests from Molly as they are requested and send responses
# #####   a  Poll valve settings over TCP/IP and send back to molly (does it time out?  is the 'single serial link' of the 800 series?)
# #####   b  Wait for request to change SL from Molly
# #####   c Send new PV to TCP/IP

# data structures
# SMC stuff
modbus_registers = {'PV':100, 'SP': 102, 'SL':134, 'RR':136, 'OP':8,'XP':140}
smc_values = {'PV':0, 'SP': 0, 'SL':0, 'RR':0, 'OP':0}
# bisync stuff - back and forth to Molly
# SL is the command to send a new setpoint
bisync_commands = ['PV','SP','ER','SL','RR','OP','XP']

# Classes to allow for reading and writing floats to the SMC
class FloatModbusClient(ModbusClient):
    def read_float(self, address, number=1):
        reg_l = self.read_holding_registers(address, number * 2)
        if reg_l:
            return [utils.decode_ieee(f) for f in utils.word_list_to_long(reg_l)][0]
        else:
            return None

    def write_float(self, address, floats_list):
        b32_l = [utils.encode_ieee(f) for f in floats_list]
        b16_l = utils.long_list_to_word(b32_l)
        return self.write_multiple_registers(address, b16_l)

def set_setpoint_eu808(ser, setpoint):
# This does not work - the SMC will not listen over the serial port
    if setpoint < 0 or setpoint > 300:
        print('Invalid range for setpoint, must be between 0 and 300')
        return
    if ser.is_open:
        msg = b'\x041100SP' + bytes(str(setpoint), encoding='ascii') + b'\x05'
        print(f"Sending '{msg}' to {ser.port}")
        #ser.write(bytes(msg, encoding='ascii'))
        ser.write(msg)
    else:
        print('Serial port {ser} is not open')
    time.sleep(0.02)
    return ser.readline()

def read_setpoint_from_eu808(ser, address):
# This one should not require a checksum
    # EOT(x04) UNIT_ADDRESS MNEMONIC ENQ (x05)
    if ser.is_open:
        add_str = str(address)
        add_formatted = bytes(2*add_str[0]+2*add_str[1], encoding='ascii')
        msg = b'\x04'+add_formatted+b'PV\x05'
        print(f"Sending {msg} to {ser.port}")
        #ser.write(bytes(msg, encoding='ascii'))
        ser.write(msg)
    else:
        print('Serial port {ser} is not open')
    time.sleep(0.2)
    return ser.readline()

def respond_to_molly(key, value, verbose=False):
    '''Send a single value to Molly'''       
    # STX (x02) MNEMONIC DATA ETX (x03) BCC
    key_formatted = bytes(key, encoding='ascii')
    if type(value)==str:
        round_value = value
    else:
        round_value = str(round(value,2))
    value_formatted = bytes(round_value, encoding='ascii')
    msg = b'\x02'+key_formatted+value_formatted+b'\x03'
    msg = msg + check_sum(msg)
    if verbose:
        print(f'sending {str(msg)} to molly')
    if ser.is_open:
        ser.write(msg)
    else:
        print(f"Serial port {ser.port} not open")

def send_ack_to_molly(verbose=False):
    msg = b'\x06'
    if verbose:
        print(f'sending {str(msg)} to molly')
    if ser.is_open:
        ser.write(msg)
    else:
        print(f"Serial port {ser.port} not open")

    
def update_molly():
    '''Send all valve parameters to Molly'''
    for key in smc_values:
        respond_to_molly(key, smc_values[key])

# CJH functions to get and set values on the SMC via TCP/IP
def get_valve_values(verbose=True):
    ''' Ask for all values from the SMC'''
    c = FloatModbusClient(host='192.168.1.240', port=0, auto_open=True)
    # open or reconnect TCP to server
    if not c.is_open():
        if not c.open():
            print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
    if c.is_open():
        for key in modbus_registers:
            smc_values[key] = round(c.read_float(modbus_registers[key], 1),2)
            #float_l = c.read_float(modbus_dict[key], 1)
            #print(f'Key: {key}  Value:{float_l}')
        c.close()
    if verbose:
        print(f'SMV values: {smc_values}') 
    
def set_valve(register='SL', setpoint=0):
    '''Write valve setpoint to SMC'''
    if setpoint < 0 or setpoint > 300:
        return
    # open or reconnect TCP to server
    c = FloatModbusClient(host='192.168.1.240', port=0, auto_open=True)
    if not c.is_open():
        if not c.open():
            print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
    if c.is_open():
        c.write_float(modbus_registers[register], [setpoint])
        c.close() 

def check_sum(message, debug=False):
    # Need this to finish the formatting of a message going back to Molly
    msg = message
    # Skip the first ETX (msg[0]), then XOR everything else
    result = msg[1]^msg[2]
    for char in msg[3:]:
        result = result ^ char
    if debug:
        print(f"message: {msg}, running check_sum: {result} (hex {hex(result)}) --> " + str(msg + bytes(chr(result),encoding='ascii')))
    return bytes(chr(result),encoding='ascii')


# Recognizing Molly requests
molly_change_requests = [b'\x040011\x02SL   0.0\x03\x12', b'\x040011\x02SL 155.0\x03\x13', b'\x040011\x02SL 300.0\x03\x11']
molly_read_requests = [b'\x040011SL\x05', b'\x040011SL\x05', b'\x040011PV\x05', 
                       b'\x040011SL\x05', b'\x040011SP\x05', b'\x040011SL\x05', b'\x040011OP\x05']
molly_requests = molly_change_requests + molly_read_requests
# straight from the EU808 handbook - answers are 0x39, 0x2e, 0x1c, 0x2c
# Note you always start with the 0x02, so it gets jammed in after the address
bcc_examples = [ b'\x02SW>0000\x03', b'\x02SP  44.\x03', b'\x02SL99\x03',b'\x02OP 61.9\x03']

def parse_molly(requests, verbose=False, debug=False):
    r_enq = re.compile(b'\x04[0-9]+([A-Z]+)\x05')
    r_sl = re.compile(b'\\x02SL([ 0-9A-Z.]+)\\x03')
    r_rr = re.compile(b'\\x02RR([ 0-9A-Z.]+)\\x03')
    for msg in requests:
        handled = False
        if len(r_enq.findall(msg))>0:
            handled = True
            if verbose:
                print(f"Msg: {msg} ---> ENQ: {(r_enq.findall(msg))[0].decode('ascii')}  ---> SET: {r_sl.findall(msg)}", end="\n")
            # do enquiry code here
            enquiry_string = (r_enq.findall(msg))[0].decode('ascii')
            if enquiry_string in bisync_commands:
                print(f'{datetime.now()}: Sending {enquiry_string} value of {smc_values[enquiry_string]} to Molly  (prompted by {msg})')
                key = enquiry_string
                if not debug:
                    respond_to_molly(key, smc_values[key], verbose=verbose)            
            else:
                print(f'Invalid request: {enquiry_string}')
        
        if len(r_sl.findall(msg))>0:
            handled = True
            if verbose:
                print(f"Msg: {msg} ---> ENQ: {r_enq.findall(msg)}  ---> SET: {(r_sl.findall(msg))[0].decode('ascii').strip()}", end="\n")
            # do setting code here            
            setpoint = float((r_sl.findall(msg))[0].decode('ascii'))
            print(f'{datetime.now()}: Setting SMC setpoint to: {setpoint}  (prompted by {msg})')
            if not debug:
                send_ack_to_molly()
                set_valve(register='SL',setpoint=setpoint)
                
        if len(r_rr.findall(msg))>0:
            handled = True
            if verbose:
                print(f"Msg: {msg} ---> ENQ: {r_enq.findall(msg)}  ---> SET: {(r_rr.findall(msg))[0].decode('ascii').strip()}", end="\n")
            # do setting code here            
            setpoint = float((r_rr.findall(msg))[0].decode('ascii'))
            print(f'{datetime.now()}: Setting SMC ramp rate to: {setpoint}  (prompted by {msg})')
            if not debug:
                send_ack_to_molly()
                set_valve(register='RR',setpoint=setpoint)
        if not handled:
            print(f'{datetime.now()}: Unable to handle: {msg}')
            
def continuous_monitoring(runtime=None, verbose=False, debug=False):
    '''Continuously monitor Molly and translate requests to SMC'''
    start_time = time.time()
    elapsed_time = 0
    timed_out = False
    #flush the buffer - it's a pain to cut them all up, rather deal with it one at a time
    clear_buffer = ser.readline()
    while timed_out is False:
        if runtime is not None:
            elapsed_time = time.time()-start_time
            if elapsed_time > runtime:
                timed_out = True
        data=ser.readline()
        if len(data) > 0:
            get_valve_values(verbose=verbose)
            if verbose:
                print(data, len(data))
            parse_molly([data], verbose=verbose, debug=debug)
            time.sleep(0.01)


if __name__ == "__main__":
    
    if sys.platform()=='win32'
        port = 'COM24'
    else:
        port = '/dev/ttyUSB0'
    #COM24 is my RS232, 25 is my 485
    try:
        print("Opening com port...")
        ser = serial.Serial(port, 9600, timeout=0.25)
    except:
        ser.close()
        ser = serial.Serial(port, 9600, timeout=0.25)
    print("Starting communications between Molly and SMC controller...")
    continuous_monitoring(runtime=None, verbose=False, debug=False)