from time import sleep, time
from threading import Thread
from sys import exit
from serial import Serial
from termcolor import colored, cprint
import curses

SERIAL_PORT_NAME = "/dev/ttyAMA0"
SERIAL_BAUD_RATE = 115200

GREETING_TEXT = 'Please type some stuff / Escriba algo:'

def drawScreen():
    global mScreen, mMessages
    for i,m in enumerate(mMessages):
        s = m[1:]
        mScreen.addstr(i,0,"")

        s = "".join(s.split('\x00'))
        mScreen.addstr(i,mScreen.getyx()[1],s, curses.color_pair(int(m[0])))
        mScreen.clrtoeol()
    mScreen.refresh()

class writeThread (Thread):
    def __init__(self):
        Thread.__init__(self)
        self.mThreadRunning = False
        self.currentString = ""
        self.cColor = 0
        mScreen.addstr(mScreen.getmaxyx()[0]-5,0,GREETING_TEXT+"\n"+self.currentString)
        mScreen.refresh()
    def run(self):
        self.mThreadRunning = True
        while(self.mThreadRunning):
            event = mScreen.getch()
            if event == ord("\n"):
                if(len(mMessages) >= mScreen.getmaxyx()[0]-7):
                    del mMessages[0:3]

                mMessages.append(str(self.cColor)+"DATE TIME:")
                mMessages.append(str(self.cColor)+self.currentString)
                mMessages.append(str(self.cColor)+"")
                self.cColor = (self.cColor+1)%2
                mSerial.write(self.currentString+'\n')
                self.currentString  = ""
                mScreen.addstr(mScreen.getmaxyx()[0]-5,0,GREETING_TEXT+"\n"+self.currentString)
                mScreen.clrtoeol()
                drawScreen()
            elif (event == 8) or (event == 127):
                self.currentString = self.currentString[:-1]
                mScreen.addstr(mScreen.getmaxyx()[0]-5,0,GREETING_TEXT+"\n"+self.currentString)
                mScreen.clrtoeol()
                drawScreen()
            else:
                try:
                    self.currentString += chr(event)
                except Exception as e:
                    pass

            mScreen.addstr(mScreen.getmaxyx()[0]-5,0,GREETING_TEXT+"\n"+self.currentString)
            mScreen.refresh()

    def stop(self):
        self.mThreadRunning = False


def setup():
    global mSerial, mWriteThread, mMessages, mScreen

    mMessages = []

    mScreen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    mScreen.keypad(1)
    curses.init_pair(1, curses.COLOR_RED, -1)

    cprint("STARTING SERIAL PORT", 'green', attrs=['bold','reverse'], end='\n')
    mSerial = Serial(SERIAL_PORT_NAME, baudrate=SERIAL_BAUD_RATE, timeout=0.01, writeTimeout=0.5)

    cprint("STARTING WRITE THREAD", 'green', attrs=['bold','reverse'], end='\n')
    mWriteThread = writeThread()
    mWriteThread.start()


def loop():
    global mSerial, mWriteThread, mMessages, mScreen
    pass


def cleanUp():
    global mSerial, mWriteThread, mMessages, mScreen

    mScreen.keypad(0)
    curses.echo()
    curses.endwin()

    cprint("STOPPING SERIAL PORT", 'red', attrs=['bold', 'reverse'], end='\n')
    mSerial.close()
    cprint("STOPPING WRITE THREAD", 'red', attrs=['bold', 'reverse'], end='\n')
    mWriteThread.stop()
    mWriteThread.join(1)

if __name__=="__main__":
    setup()

    while True:
        try:
            loopStart = time()
            loop()
            loopTime = time() - loopStart
            sleep(max(0.016 - loopTime, 0))
        except KeyboardInterrupt:
            cleanUp()
            exit(0)
        except Exception as e:
            cprint("LOOP EXCEPTION CAUGHT:", 'red', attrs=['bold', 'reverse'], end='\n')
            cprint(str(e), attrs=['bold'], end='\n')
            cleanUp()
            setup()
