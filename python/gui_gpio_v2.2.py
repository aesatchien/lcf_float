from tkinter import *
import tkinter.font
import time
import threading
import csv
import pyautogui, sys
from gpiozero import LED
import gpiozero
import RPi.GPIO as GPIO
import brEFB_CJH as brefb

GPIO.setmode(GPIO.BCM)

##settings and filing
settingData = [[0 for x in range(4)] for y in range(17)]

with open('Settings.csv', newline='') as settingFile:
    reader = csv.reader(settingFile)
    i = 0;
    for row in reader:
        settingData[i][:] = row
        i = i + 1

##labeling
ch1en = settingData[1][1]
ch1dis = settingData[1][2]
ch2en = settingData[2][1]
ch2dis = settingData[2][2]
ch3en = settingData[3][1]
ch3dis = settingData[3][2]
ch4en = settingData[4][1]
ch4dis = settingData[4][2]
ch5en = settingData[5][1]
ch5dis = settingData[5][2]
ch6en = settingData[6][1]
ch6dis = settingData[6][2]
ch7en = settingData[7][1]
ch7dis = settingData[7][2]
ch8en = settingData[8][1]
ch8dis = settingData[8][2]
ch9en = settingData[9][1]
ch9dis = settingData[9][2]
ch10en = settingData[10][1]
ch10dis = settingData[10][2]
ch11en = settingData[11][1]
ch11dis = settingData[11][2]
ch12en = settingData[12][1]
ch12dis = settingData[12][2]
ch13en = settingData[13][1]
ch13dis = settingData[13][2]
ch14en = settingData[14][1]
ch14dis = settingData[14][2]
ch15en = settingData[15][1]
ch15dis = settingData[15][2]
ch16en = settingData[16][1]
ch16dis = settingData[16][2]

##touchscreen setup
xpadding = 10
ypadding = 25
buttonh = 4
buttonw = 11

##hardware
en1io = LED(13)
en2io = LED(6)
en3io = LED(19)
en4io = LED(12)

en5io = LED(7)
en6io = LED(11)
en7io = LED(5)
en8io = LED(8)

en9io = LED(9)
en10io = LED(24)
en11io = LED(25)
en12io = LED(10)

en13io = LED(27)
en14io = LED(4)
en15io = LED(22)
en16io = LED(17)

show1io = LED(20)
show2io = LED(16)
playio = LED(21)
stopio = LED(26)

bank1In = 23
bank2In = 18
bank3In = 15
bank4In = 14

##toggling states
en1 = 0
en2 = 0
en3 = 0
en4 = 0
en5 = 0
en6 = 0
en7 = 0
en8 = 0
en9 = 0
en10 = 0
en11 = 0
en12 = 0
en13 = 0
en14 = 0
en15 = 0
en16 = 0

bank1 = 0
bank2 = 0
bank3 = 0
bank4 = 0

pauseState = 0

##set Br-EFB status lines as input
GPIO.setup(bank1In, GPIO.IN)
GPIO.setup(bank2In, GPIO.IN)
GPIO.setup(bank3In, GPIO.IN)
GPIO.setup(bank4In, GPIO.IN)

##mouse reset
# y of 768 seems to kill pyautogui on the updated version of raspbian set it to 766
mouseRx = 0
mouseRy = 766


##functions
def bank1Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank1
    if bank1 == 0:
        bank1EnButton["text"] = "Bank 1 En"
        bank1EnButton["bg"] = "limegreen"
        bank1 = 1
    else:
        bank1EnButton["text"] = "Bank 1 Dis"
        bank1EnButton["bg"] = "red"
        bank1 = 0

    if en1 == 1 and bank1 == 1:
        en1Button["text"] = ch1en
        en1Button["bg"] = "limegreen"
        en1io.on()
    elif en1 == 1 and bank1 == 0:
        en1Button["text"] = ch1dis
        en1Button["bg"] = "yellow"
        en1io.off()

    if en2 == 1 and bank1 == 1:
        en2Button["text"] = ch2en
        en2Button["bg"] = "limegreen"
        en2io.on()
    elif en2 == 1 and bank1 == 0:
        en2Button["text"] = ch2dis
        en2Button["bg"] = "yellow"
        en2io.off()

    if en3 == 1 and bank1 == 1:
        en3Button["text"] = ch3en
        en3Button["bg"] = "limegreen"
        en3io.on()
    elif en3 == 1 and bank1 == 0:
        en3Button["text"] = ch3dis
        en3Button["bg"] = "yellow"
        en3io.off()

    if en4 == 1 and bank1 == 1:
        en4Button["text"] = ch4en
        en4Button["bg"] = "limegreen"
        en4io.on()
    elif en4 == 1 and bank1 == 0:
        en4Button["text"] = ch4dis
        en4Button["bg"] = "yellow"
        en4io.off()


def ch1Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank1
    global en1
    if en1 == 0:
        ch1En()
    elif en1 == 1:
        ch1Dis()


def ch1En():
    global bank1
    global en1
    if bank1 == 0:
        en1Button["text"] = ch1en
        en1Button["bg"] = "yellow"
        en1io.off()
        en1 = 1
    elif bank1 == 1:
        en1Button["text"] = ch1en
        en1Button["bg"] = "limegreen"
        en1io.on()
        en1 = 1


def ch1Dis():
    global bank1
    global en1
    en1Button["text"] = ch1dis
    en1Button["bg"] = "red"
    en1io.off()
    en1 = 0


def ch2Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank1
    global en2
    if en2 == 0:
        ch2En()
    elif en2 == 1:
        ch2Dis()


def ch2En():
    global bank1
    global en2
    if bank1 == 0:
        en2Button["text"] = ch2en
        en2Button["bg"] = "yellow"
        en2io.off()
        en2 = 1
    elif bank1 == 1:
        en2Button["text"] = ch2en
        en2Button["bg"] = "limegreen"
        en2io.on()
        en2 = 1


def ch2Dis():
    global bank1
    global en2
    en2Button["text"] = ch2dis
    en2Button["bg"] = "red"
    en2io.off()
    en2 = 0


def ch3Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank1
    global en3
    if en3 == 0:
        ch3En()
    elif en3 == 1:
        ch3Dis()


def ch3En():
    global bank1
    global en3
    if bank1 == 0:
        en3Button["text"] = ch3en
        en3Button["bg"] = "yellow"
        en3io.off()
        en3 = 1
    elif bank1 == 1:
        en3Button["text"] = ch3en
        en3Button["bg"] = "limegreen"
        en3io.on()
        en3 = 1


def ch3Dis():
    global bank1
    global en3
    en3Button["text"] = ch3dis
    en3Button["bg"] = "red"
    en3io.off()
    en3 = 0


def ch4Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank1
    global en4
    if en4 == 0:
        ch4En()
    elif en4 == 1:
        ch4Dis()


def ch4En():
    global bank1
    global en4
    if bank1 == 0:
        en4Button["text"] = ch4en
        en4Button["bg"] = "yellow"
        en4io.off()
        en4 = 1
    elif bank1 == 1:
        en4Button["text"] = ch4en
        en4Button["bg"] = "limegreen"
        en4io.on()
        en4 = 1


def ch4Dis():
    global bank1
    global en4
    en4Button["text"] = ch4dis
    en4Button["bg"] = "red"
    en4io.off()
    en4 = 0


##########################################
def bank2Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank2
    if bank2 == 0:
        bank2EnButton["text"] = "Bank 2 En"
        bank2EnButton["bg"] = "limegreen"
        bank2 = 1
    else:
        bank2EnButton["text"] = "Bank 2 Dis"
        bank2EnButton["bg"] = "red"
        bank2 = 0

    if en5 == 1 and bank2 == 1:
        en5Button["text"] = ch5en
        en5Button["bg"] = "limegreen"
        en5io.on()
    elif en5 == 1 and bank2 == 0:
        en5Button["text"] = ch5dis
        en5Button["bg"] = "yellow"
        en5io.off()

    if en6 == 1 and bank2 == 1:
        en6Button["text"] = ch6en
        en6Button["bg"] = "limegreen"
        en6io.on()
    elif en6 == 1 and bank2 == 0:
        en6Button["text"] = ch6dis
        en6Button["bg"] = "yellow"
        en6io.off()

    if en7 == 1 and bank2 == 1:
        en7Button["text"] = ch7en
        en7Button["bg"] = "limegreen"
        en7io.on()
    elif en7 == 1 and bank2 == 0:
        en7Button["text"] = ch7dis
        en7Button["bg"] = "yellow"
        en7io.off()

    if en8 == 1 and bank2 == 1:
        en8Button["text"] = ch8en
        en8Button["bg"] = "limegreen"
        en8io.on()
    elif en8 == 1 and bank2 == 0:
        en8Button["text"] = ch8dis
        en8Button["bg"] = "yellow"
        en8io.off()


def ch5Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank2
    global en5
    if en5 == 0:
        ch5En()
    elif en5 == 1:
        ch5Dis()


def ch5En():
    global bank2
    global en5
    if bank2 == 0:
        en5Button["text"] = ch5en
        en5Button["bg"] = "yellow"
        en5io.off()
        en5 = 1
    elif bank2 == 1:
        en5Button["text"] = ch5en
        en5Button["bg"] = "limegreen"
        en5io.on()
        en5 = 1


def ch5Dis():
    global bank2
    global en5
    en5Button["text"] = ch5dis
    en5Button["bg"] = "red"
    en5io.off()
    en5 = 0


def ch6Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank2
    global en6
    if en6 == 0:
        ch6En()
    elif en6 == 1:
        ch6Dis()


def ch6En():
    global bank2
    global en6
    if bank2 == 0:
        en6Button["text"] = ch6en
        en6Button["bg"] = "yellow"
        en6io.off()
        en6 = 1
    elif bank2 == 1:
        en6Button["text"] = ch6en
        en6Button["bg"] = "limegreen"
        en6io.on()
        en6 = 1


def ch6Dis():
    global bank2
    global en6
    en6Button["text"] = ch6dis
    en6Button["bg"] = "red"
    en6io.off()
    en6 = 0


def ch7Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank2
    global en7
    if en7 == 0:
        ch7En()
    elif en7 == 1:
        ch7Dis()


def ch7En():
    global bank2
    global en7
    if bank2 == 0:
        en7Button["text"] = ch7en
        en7Button["bg"] = "yellow"
        en7io.off()
        en7 = 1
    elif bank2 == 1:
        en7Button["text"] = ch7en
        en7Button["bg"] = "limegreen"
        en7io.on()
        en7 = 1


def ch7Dis():
    global bank2
    global en7
    en7Button["text"] = ch7dis
    en7Button["bg"] = "red"
    en7io.off()
    en7 = 0


def ch8Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank2
    global en8
    if en8 == 0:
        ch8En()
    elif en8 == 1:
        ch8Dis()


def ch8En():
    global bank2
    global en8
    if bank2 == 0:
        en8Button["text"] = ch8en
        en8Button["bg"] = "yellow"
        en8io.off()
        en8 = 1
    elif bank2 == 1:
        en8Button["text"] = ch8en
        en8Button["bg"] = "limegreen"
        en8io.on()
        en8 = 1


def ch8Dis():
    global bank2
    global en8
    en8Button["text"] = ch8dis
    en8Button["bg"] = "red"
    en8io.off()
    en8 = 0


##########################################
def bank3Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank3
    if bank3 == 0:
        bank3EnButton["text"] = "Bank 3 En"
        bank3EnButton["bg"] = "limegreen"
        bank3 = 1
    else:
        bank3EnButton["text"] = "Bank 3 Dis"
        bank3EnButton["bg"] = "red"
        bank3 = 0

    if en9 == 1 and bank3 == 1:
        en9Button["text"] = ch9en
        en9Button["bg"] = "limegreen"
        en9io.on()
    elif en9 == 1 and bank3 == 0:
        en9Button["text"] = ch9dis
        en9Button["bg"] = "yellow"
        en9io.off()

    if en10 == 1 and bank3 == 1:
        en10Button["text"] = ch10en
        en10Button["bg"] = "limegreen"
        en10io.on()
    elif en10 == 1 and bank3 == 0:
        en10Button["text"] = ch10dis
        en10Button["bg"] = "yellow"
        en10io.off()

    if en11 == 1 and bank3 == 1:
        en11Button["text"] = ch11en
        en11Button["bg"] = "limegreen"
        en11io.on()
    elif en11 == 1 and bank3 == 0:
        en11Button["text"] = ch11dis
        en11Button["bg"] = "yellow"
        en11io.off()

    if en12 == 1 and bank3 == 1:
        en12Button["text"] = ch12en
        en12Button["bg"] = "limegreen"
        en12io.on()
    elif en12 == 1 and bank3 == 0:
        en12Button["text"] = ch12dis
        en12Button["bg"] = "yellow"
        en12io.off()


def ch9Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank3
    global en9
    if en9 == 0:
        ch9En()
    elif en9 == 1:
        ch9Dis()


def ch9En():
    global bank3
    global en9
    if bank3 == 0:
        en9Button["text"] = ch9en
        en9Button["bg"] = "yellow"
        en9io.off()
        en9 = 1
    elif bank3 == 1:
        en9Button["text"] = ch9en
        en9Button["bg"] = "limegreen"
        en9io.on()
        en9 = 1


def ch9Dis():
    global bank3
    global en9
    en9Button["text"] = ch9dis
    en9Button["bg"] = "red"
    en9io.off()
    en9 = 0


def ch10Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank3
    global en10
    if en10 == 0:
        ch10En()
    elif en10 == 1:
        ch10Dis()


def ch10En():
    global bank3
    global en10
    if bank3 == 0:
        en10Button["text"] = ch10en
        en10Button["bg"] = "yellow"
        en10io.off()
        en10 = 1
    elif bank3 == 1:
        en10Button["text"] = ch10en
        en10Button["bg"] = "limegreen"
        en10io.on()
        en10 = 1


def ch10Dis():
    global bank3
    global en10
    en10Button["text"] = ch10dis
    en10Button["bg"] = "red"
    en10io.off()
    en10 = 0


def ch11Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank3
    global en11
    if en11 == 0:
        ch11En()
    elif en11 == 1:
        ch11Dis()


def ch11En():
    global bank3
    global en11
    if bank3 == 0:
        en11Button["text"] = ch11en
        en11Button["bg"] = "yellow"
        en11io.off()
        en11 = 1
    elif bank3 == 1:
        en11Button["text"] = ch11en
        en11Button["bg"] = "limegreen"
        en11io.on()
        en11 = 1


def ch11Dis():
    global bank3
    global en11
    en11Button["text"] = ch11dis
    en11Button["bg"] = "red"
    en11io.off()
    en11 = 0


def ch12Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank3
    global en12
    if en12 == 0 and bank3 == 0:
        en12Button["text"] = ch12en
        en12Button["bg"] = "yellow"
        en12io.off()
        en12 = 1
    elif en12 == 0 and bank3 == 1:
        en12Button["text"] = ch12en
        en12Button["bg"] = "limegreen"
        en12io.on()
        en12 = 1
    elif en12 == 1:
        en12Button["text"] = ch12dis
        en12Button["bg"] = "red"
        en12io.off()
        en12 = 0


def ch12En():
    global bank3
    global en12
    if bank3 == 0:
        en12Button["text"] = ch12en
        en12Button["bg"] = "yellow"
        en12io.off()
        en12 = 1
    elif bank3 == 1:
        en12Button["text"] = ch12en
        en12Button["bg"] = "limegreen"
        en12io.on()
        en12 = 1


def ch12Dis():
    global bank3
    global en12
    en12Button["text"] = ch12dis
    en12Button["bg"] = "red"
    en12io.off()
    en12 = 0


##########################################
def bank4Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank4
    if bank4 == 0:
        bank4EnButton["text"] = "Bank 4 En"
        bank4EnButton["bg"] = "limegreen"
        bank4 = 1
    else:
        bank4EnButton["text"] = "Bank 4 Dis"
        bank4EnButton["bg"] = "red"
        bank4 = 0

    if en13 == 1 and bank4 == 1:
        en13Button["text"] = ch13en
        en13Button["bg"] = "limegreen"
        en13io.on()
    elif en13 == 1 and bank4 == 0:
        en13Button["text"] = ch13dis
        en13Button["bg"] = "yellow"
        en13io.off()

    if en14 == 1 and bank4 == 1:
        en14Button["text"] = ch14en
        en14Button["bg"] = "limegreen"
        en14io.on()
    elif en14 == 1 and bank4 == 0:
        en14Button["text"] = ch14dis
        en14Button["bg"] = "yellow"
        en14io.off()

    if en15 == 1 and bank4 == 1:
        en15Button["text"] = ch15en
        en15Button["bg"] = "limegreen"
        en15io.on()
    elif en15 == 1 and bank4 == 0:
        en15Button["text"] = ch15dis
        en15Button["bg"] = "yellow"
        en15io.off()

    if en16 == 1 and bank4 == 1:
        en16Button["text"] = ch16en
        en16Button["bg"] = "limegreen"
        en16io.on()
    elif en16 == 1 and bank4 == 0:
        en16Button["text"] = ch16dis
        en16Button["bg"] = "yellow"
        en16io.off()


def ch13Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank4
    global en13
    if en13 == 0:
        ch13En()
    elif en13 == 1:
        ch13Dis()


def ch13En():
    global bank4
    global en13
    if bank4 == 0:
        en13Button["text"] = ch13en
        en13Button["bg"] = "yellow"
        en13io.off()
        en13 = 1
    elif bank4 == 1:
        en13Button["text"] = ch13en
        en13Button["bg"] = "limegreen"
        en13io.on()
        en13 = 1


def ch13Dis():
    global bank4
    global en13
    en13Button["text"] = ch13dis
    en13Button["bg"] = "red"
    en13io.off()
    en13 = 0


def ch14Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank4
    global en14
    if en14 == 0:
        ch14En()
    elif en14 == 1:
        ch14Dis()


def ch14En():
    global bank4
    global en14
    if bank4 == 0:
        en14Button["text"] = ch14en
        en14Button["bg"] = "yellow"
        en14io.off()
        en14 = 1
    elif bank4 == 1:
        en14Button["text"] = ch14en
        en14Button["bg"] = "limegreen"
        en14io.on()
        en14 = 1


def ch14Dis():
    global bank4
    global en14
    en14Button["text"] = ch14dis
    en14Button["bg"] = "red"
    en14io.off()
    en14 = 0


def ch15Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank4
    global en15
    if en15 == 0:
        ch15En()
    elif en15 == 1:
        ch15Dis()


def ch15En():
    global bank4
    global en15
    if bank4 == 0:
        en15Button["text"] = ch15en
        en15Button["bg"] = "yellow"
        en15io.off()
        en15 = 1
    elif bank4 == 1:
        en15Button["text"] = ch15en
        en15Button["bg"] = "limegreen"
        en15io.on()
        en15 = 1


def ch15Dis():
    global bank4
    global en15
    en15Button["text"] = ch15dis
    en15Button["bg"] = "red"
    en15io.off()
    en15 = 0


def ch16Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    global bank4
    global en16
    if en16 == 0:
        ch16En()
    elif en16 == 1:
        ch16Dis()


def ch16En():
    global bank4
    global en16
    if bank4 == 0:
        en16Button["text"] = ch16en
        en16Button["bg"] = "yellow"
        en16io.off()
        en16 = 1
    elif bank4 == 1:
        en16Button["text"] = ch16en
        en16Button["bg"] = "limegreen"
        en16io.on()
        en16 = 1


def ch16Dis():
    global bank4
    global en16
    en16Button["text"] = ch16dis
    en16Button["bg"] = "red"
    en16io.off()
    en16 = 0


def show1Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    show1io.on()
    time.sleep(0.2)
    show1io.off()


def show2Update():
    pyautogui.moveTo(mouseRx, mouseRy)
    show2io.on()
    time.sleep(0.2)
    show2io.off()


def playUpdate():
    pyautogui.moveTo(mouseRx, mouseRy)
    global pauseState
    if pauseState == 0:
        pauseState = 1
        playio.on()
        playButton["text"] = "Pausing\n(tap to play)"
    elif pauseState == 1:
        pauseState = 0
        playio.off()
        playButton["text"] = "Playing\n(tap to pause)"


def stopUpdate():
    pyautogui.moveTo(mouseRx, mouseRy)
    stopio.on()
    time.sleep(0.2)
    stopio.off()


def loadUpdate():
    pyautogui.moveTo(mouseRx, mouseRy)
    settingData = [[0 for x in range(4)] for y in range(17)]

    with open('Settings.csv', newline='') as settingFile:
        reader = csv.reader(settingFile)
        i = 0;
        for row in reader:
            settingData[i][:] = row
            i = i + 1
    if settingData[1][3] == '1' or settingData[1][3] == 1:
        ch1En()
    if settingData[1][3] == '0' or settingData[1][3] == 0:
        ch1Dis()
    if settingData[2][3] == '1' or settingData[1][3] == 1:
        ch2En()
    if settingData[2][3] == '0' or settingData[1][3] == 0:
        ch2Dis()
    if settingData[3][3] == '1' or settingData[1][3] == 1:
        ch3En()
    if settingData[3][3] == '0' or settingData[1][3] == 0:
        ch3Dis()
    if settingData[4][3] == '1' or settingData[1][3] == 1:
        ch4En()
    if settingData[4][3] == '0' or settingData[1][3] == 0:
        ch4Dis()
    if settingData[5][3] == '1' or settingData[1][3] == 1:
        ch5En()
    if settingData[5][3] == '0' or settingData[1][3] == 0:
        ch5Dis()
    if settingData[6][3] == '1' or settingData[1][3] == 1:
        ch6En()
    if settingData[6][3] == '0' or settingData[1][3] == 0:
        ch6Dis()
    if settingData[7][3] == '1' or settingData[1][3] == 1:
        ch7En()
    if settingData[7][3] == '0' or settingData[1][3] == 0:
        ch7Dis()
    if settingData[8][3] == '1' or settingData[1][3] == 1:
        ch8En()
    if settingData[8][3] == '0' or settingData[1][3] == 0:
        ch8Dis()
    if settingData[9][3] == '1' or settingData[1][3] == 1:
        ch9En()
    if settingData[9][3] == '0' or settingData[1][3] == 0:
        ch9Dis()
    if settingData[10][3] == '1' or settingData[1][3] == 1:
        ch10En()
    if settingData[10][3] == '0' or settingData[1][3] == 0:
        ch10Dis()
    if settingData[11][3] == '1' or settingData[1][3] == 1:
        ch11En()
    if settingData[11][3] == '0' or settingData[1][3] == 0:
        ch11Dis()
    if settingData[11][3] == '1' or settingData[1][3] == 1:
        ch11En()
    if settingData[11][3] == '0' or settingData[1][3] == 0:
        ch11Dis()
    if settingData[12][3] == '1' or settingData[1][3] == 1:
        ch12En()
    if settingData[12][3] == '0' or settingData[1][3] == 0:
        ch12Dis()
    if settingData[13][3] == '1' or settingData[1][3] == 1:
        ch13En()
    if settingData[13][3] == '0' or settingData[1][3] == 0:
        ch13Dis()
    if settingData[13][3] == '1' or settingData[1][3] == 1:
        ch13En()
    if settingData[13][3] == '0' or settingData[1][3] == 0:
        ch13Dis()
    if settingData[14][3] == '1' or settingData[1][3] == 1:
        ch14En()
    if settingData[14][3] == '0' or settingData[1][3] == 0:
        ch14Dis()
    if settingData[15][3] == '1' or settingData[1][3] == 1:
        ch15En()
    if settingData[15][3] == '0' or settingData[1][3] == 0:
        ch15Dis()
    if settingData[16][3] == '1' or settingData[1][3] == 1:
        ch16En()
    if settingData[16][3] == '0' or settingData[1][3] == 0:
        ch16Dis()


def save():
    pyautogui.moveTo(mouseRx, mouseRy)
    settingData[1][3] = en1
    settingData[2][3] = en2
    settingData[3][3] = en3
    settingData[4][3] = en4
    settingData[5][3] = en5
    settingData[6][3] = en6
    settingData[7][3] = en7
    settingData[8][3] = en8
    settingData[9][3] = en9
    settingData[10][3] = en10
    settingData[11][3] = en11
    settingData[12][3] = en12
    settingData[13][3] = en13
    settingData[14][3] = en14
    settingData[15][3] = en15
    settingData[16][3] = en16

    settingFile = open('Settings.csv', 'w')
    with settingFile:
        writer = csv.writer(settingFile)
        writer.writerows(settingData)


def exit2ndWindow():
    pyautogui.moveTo(mouseRx, mouseRy)
    top.destroy()


def exitProg():
    pyautogui.moveTo(mouseRx, mouseRy)
    top = Toplevel()
    top.title("LCFTRA Animation Controller Save/Exit Menu")
    top.resizable(width=False, height=False)
    top.geometry('{}x{}'.format(1015, 730))

    killButton = Button(top, text='Shut Down Controller', font=myFont, command=killProg, bg='red', height=6, width=55)
    killButton.grid(row=0, column=1, padx=xpadding * 20, pady=ypadding * 2)

    saveButton = Button(top, text='Save Current Configuration', font=myFont, command=save, bg='white', height=6,
                        width=55)
    saveButton.grid(row=1, column=1, padx=xpadding * 20, pady=ypadding * 2)

    cancelButton = Button(top, text='Return to Controller', font=myFont, command=top.destroy, bg='limegreen', height=6,
                          width=55)
    cancelButton.grid(row=2, column=1, padx=xpadding * 20, pady=ypadding * 2)


def killProg():
    pyautogui.moveTo(mouseRx, mouseRy)
    en1io.off()
    en2io.off()
    en3io.off()
    en4io.off()
    en5io.off()
    en6io.off()
    en7io.off()
    en8io.off()
    en9io.off()
    en10io.off()
    en11io.off()
    en12io.off()
    en13io.off()
    en14io.off()
    en15io.off()
    en16io.off()
    show1io.off()
    show2io.off()
    playio.off()
    stopio.off()
    command = "/usr/bin/sudo /sbin/shutdown -P now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]


def bankStat():
    # ok, this is really bad.  there is a thread starting every time but never ending, so we just keep getting more!
    # I don't know why it wasn't crashing on the old version but it is on the new raspbian - 10/5/2019 CJH
    # threading.Timer(1, bankStat).start()
    if GPIO.input(bank1In):
        bank1Stat["text"] = "Bank 1 Fail"
        bank1Stat["bg"] = "red"
    else:
        bank1Stat["text"] = "Bank 1 Ok"
        bank1Stat["bg"] = "limegreen"

    if GPIO.input(bank2In):
        bank2Stat["text"] = "Bank 2 Fail"
        bank2Stat["bg"] = "red"
    else:
        bank2Stat["text"] = "Bank 2 Ok"
        bank2Stat["bg"] = "limegreen"

    if GPIO.input(bank3In):
        bank3Stat["text"] = "Bank 3 Fail"
        bank3Stat["bg"] = "red"
    else:
        bank3Stat["text"] = "Bank 3 Ok"
        bank3Stat["bg"] = "limegreen"

    if GPIO.input(bank4In):
        bank4Stat["text"] = "Bank 4 Fail"
        bank4Stat["bg"] = "red"
    else:
        bank4Stat["text"] = "Bank 4 Ok"
        bank4Stat["bg"] = "limegreen"


##gui setup
win = Tk()
win.title("LCFTRA Animation Controller v2.0")
myFont = tkinter.font.Font(family='Helvetiva', size=12, weight="bold")
win.resizable(width=False, height=False)
win.geometry('{}x{}'.format(1015, 730))
# win.config(background='lightgrey', cursor='none')


##widgets
bank1EnButton = Button(win, text='Bank 1 Dis', font=myFont, command=bank1Update, bg='red', height=buttonh,
                       width=buttonw)
bank1EnButton.grid(row=1, column=1, padx=xpadding, pady=ypadding)
en1Button = Button(win, text=ch1dis, font=myFont, command=ch1Update, bg='red', height=buttonh, width=buttonw)
en1Button.grid(row=1, column=2, padx=xpadding, pady=ypadding)
en2Button = Button(win, text=ch2dis, font=myFont, command=ch2Update, bg='red', height=buttonh, width=buttonw)
en2Button.grid(row=1, column=3, padx=xpadding, pady=ypadding)
en3Button = Button(win, text=ch3dis, font=myFont, command=ch3Update, bg='red', height=buttonh, width=buttonw)
en3Button.grid(row=1, column=4, padx=xpadding, pady=ypadding)
en4Button = Button(win, text=ch4dis, font=myFont, command=ch4Update, bg='red', height=buttonh, width=buttonw)
en4Button.grid(row=1, column=5, padx=xpadding, pady=ypadding)

bank2EnButton = Button(win, text='Bank 2 Dis', font=myFont, command=bank2Update, bg='red', height=buttonh,
                       width=buttonw)
bank2EnButton.grid(row=2, column=1, padx=xpadding, pady=ypadding)
en5Button = Button(win, text=ch5dis, font=myFont, command=ch5Update, bg='red', height=buttonh, width=buttonw)
en5Button.grid(row=2, column=2, padx=xpadding, pady=ypadding)
en6Button = Button(win, text=ch6dis, font=myFont, command=ch6Update, bg='red', height=buttonh, width=buttonw)
en6Button.grid(row=2, column=3, padx=xpadding, pady=ypadding)
en7Button = Button(win, text=ch7dis, font=myFont, command=ch7Update, bg='red', height=buttonh, width=buttonw)
en7Button.grid(row=2, column=4, padx=xpadding, pady=ypadding)
en8Button = Button(win, text=ch8dis, font=myFont, command=ch8Update, bg='red', height=buttonh, width=buttonw)
en8Button.grid(row=2, column=5, padx=xpadding, pady=ypadding)

bank3EnButton = Button(win, text='Bank 3 Dis', font=myFont, command=bank3Update, bg='red', height=buttonh,
                       width=buttonw)
bank3EnButton.grid(row=3, column=1, padx=xpadding, pady=ypadding)
en9Button = Button(win, text=ch9dis, font=myFont, command=ch9Update, bg='red', height=buttonh, width=buttonw)
en9Button.grid(row=3, column=2, padx=xpadding, pady=ypadding)
en10Button = Button(win, text=ch10dis, font=myFont, command=ch10Update, bg='red', height=buttonh, width=buttonw)
en10Button.grid(row=3, column=3, padx=xpadding, pady=ypadding)
en11Button = Button(win, text=ch11dis, font=myFont, command=ch11Update, bg='red', height=buttonh, width=buttonw)
en11Button.grid(row=3, column=4, padx=xpadding, pady=ypadding)
en12Button = Button(win, text=ch12dis, font=myFont, command=ch12Update, bg='red', height=buttonh, width=buttonw)
en12Button.grid(row=3, column=5, padx=xpadding, pady=ypadding)

bank4EnButton = Button(win, text='Bank 4 Dis', font=myFont, command=bank4Update, bg='red', height=buttonh,
                       width=buttonw)
bank4EnButton.grid(row=4, column=1, padx=xpadding, pady=ypadding)
en13Button = Button(win, text=ch13dis, font=myFont, command=ch13Update, bg='red', height=buttonh, width=buttonw)
en13Button.grid(row=4, column=2, padx=xpadding, pady=ypadding)
en14Button = Button(win, text=ch14dis, font=myFont, command=ch14Update, bg='red', height=buttonh, width=buttonw)
en14Button.grid(row=4, column=3, padx=xpadding, pady=ypadding)
en15Button = Button(win, text=ch15dis, font=myFont, command=ch15Update, bg='red', height=buttonh, width=buttonw)
en15Button.grid(row=4, column=4, padx=xpadding, pady=ypadding)
en16Button = Button(win, text=ch16dis, font=myFont, command=ch16Update, bg='red', height=buttonh, width=buttonw)
en16Button.grid(row=4, column=5, padx=xpadding, pady=ypadding)

show1Button = Button(win, text='Start\nShow 1', font=myFont, command=show1Update, bg='gold', height=buttonh,
                     width=buttonw)
show1Button.grid(row=5, column=1, padx=xpadding, pady=ypadding)
show2Button = Button(win, text='Start\nShow 2', font=myFont, command=show2Update, bg='gold', height=buttonh,
                     width=buttonw)
show2Button.grid(row=5, column=2, padx=xpadding, pady=ypadding)
playButton = Button(win, text='Pause', font=myFont, command=playUpdate, bg='gold', height=buttonh, width=buttonw)
playButton.grid(row=5, column=3, padx=xpadding, pady=ypadding)
stopButton = Button(win, text='End Show', font=myFont, command=stopUpdate, bg='gold', height=buttonh, width=buttonw)
stopButton.grid(row=5, column=4, padx=xpadding, pady=ypadding)
loadButton = Button(win, text='Load\nSettings', font=myFont, command=loadUpdate, bg='white', height=buttonh,
                    width=buttonw)
loadButton.grid(row=5, column=5, padx=xpadding, pady=ypadding)
saveButton = Button(win, text='Save / Exit', font=myFont, command=exitProg, bg='cyan', height=buttonh, width=buttonw)
saveButton.grid(row=5, column=6, padx=xpadding, pady=ypadding)

bank1Stat = Button(win, text='Bank 1 Stat', font=myFont, command=bankStat, bg='red', height=buttonh, width=buttonw)
bank1Stat.grid(row=1, column=6, padx=xpadding, pady=ypadding)
bank2Stat = Button(win, text='Bank 2 Stat', font=myFont, command=bankStat, bg='red', height=buttonh, width=buttonw)
bank2Stat.grid(row=2, column=6, padx=xpadding, pady=ypadding)
bank3Stat = Button(win, text='Bank 3 Stat', font=myFont, command=bankStat, bg='red', height=buttonh, width=buttonw)
bank3Stat.grid(row=3, column=6, padx=xpadding, pady=ypadding)
bank4Stat = Button(win, text='Bank 4 Stat', font=myFont, command=bankStat, bg='red', height=buttonh, width=buttonw)
bank4Stat.grid(row=4, column=6, padx=xpadding, pady=ypadding)

# status labels - 10/6/2019 CJH
# setpointLabel = Label(win, text = 'Setpoints', font = myFont, bg = 'white', height = 1, width = buttonw)
# setpointLabel.grid(row = 6, padx = 0, pady = 1, sticky=W, columnspan=5)
# transducerLabel = Label(win, text = 'Transducers', font = myFont, bg = 'white', height = 1, width = buttonw)
# transducerLabel.grid(row = 7, padx = 0, pady = 1, sticky=W, columnspan=4)

##loop/interrupt setup
counter = 0
brefb.set_banks()


def task():
    # Updated this message printing so it keeps the terminal a bit more sane - 10/5/2019 CJH
    version = "2.2"
    global counter
    counter = counter + 1
    print("Version {} Run Update: {} with {} threads active".format(version, counter, threading.active_count()),
          end="\r", flush=True)
    bankStat()
    # check every minute to see if we have changed banks - timeout needs to be longer for this one otherwise we get errors
    if counter % 120 == 0:
        brefb.set_banks(verbose=False)
    brefb.update_sparks()
    bank1Stat.config(
        text=bank1Stat["text"] + "\nTD: " + brefb.sparkline(brefb.sparks['a'][::2], False) + "\nSP: " + brefb.sparkline(
            brefb.sparks['a'][1::2], False))
    bank2Stat.config(
        text=bank2Stat["text"] + "\nTD: " + brefb.sparkline(brefb.sparks['b'][::2], False) + "\nSP: " + brefb.sparkline(
            brefb.sparks['b'][1::2], False))
    win.after(500, task)


win.after(1000, task)
win.mainloop()
print("\nExiting...")


