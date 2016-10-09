from tkinter import *
from tkinter.ttk import *
from tkinter import Button

import subprocess
import threading
import serial

import serscan

portStrings = ('COM1','COM2','COM47')

class commThread(threading.Thread):
    def __init__(self, portName, retFcn, runFcn):
        threading.Thread.__init__(self)
        self.portName = portName
        self.retFcn = retFcn
        self.runFcn = runFcn
        self.stopVal = False
    def run(self):
        try:
            with serial.Serial(self.portName,9600,timeout=0.1) as port:
                while True:
                    s = port.readlines()
                    if s==[b'PUSH\r\n']:
                        self.runFcn()
                    if self.stopVal==True:
                        break
                try: # maybe the parent doesn't exist anymore
                    self.retFcn('OK')
                except:
                    pass
        except:
            self.retFcn('ERROR')
    def stop(self):
        self.stopVal = True

class app:
    def __init__(self, master):
        root.title("Push Button v0.1")
        root.resizable(False,False)

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.mainfrm = Frame(root,padding='3 3 3 3')
        self.mainfrm.pack(side=TOP,fill=BOTH)

        self.portLabelfrm = LabelFrame(self.mainfrm,text='Port',padding='3 3 3 3')
        self.portLabelfrm.pack(side=TOP,fill=X)

        self.serialLabel = Label(self.portLabelfrm,text='Name:')
        self.serialLabel.pack(side=LEFT)
        self.portStr = StringVar()
        self.ports = portStrings
        self.scanPorts()
        self.serialCombo = Combobox(self.portLabelfrm,textvariable=self.portStr,
                                    values=self.ports,width=10,justify=CENTER)
        self.serialCombo.current(0)
        self.serialCombo.pack(side=LEFT)
        self.autoVar = IntVar()
        self.serialChbox = Checkbutton(self.portLabelfrm,text='Auto Connect',
                                       variable=self.autoVar)
        self.serialChbox.pack(side=LEFT,padx=10)
        self.serialButton = Button(self.portLabelfrm,text='CONNECT',
                                   command=self.connect)
        self.serialButton.pack(side=LEFT)

        self.dirLabelfrm = LabelFrame(self.mainfrm,text='Directory',padding='3 3 3 3')
        self.dirLabelfrm.pack(side=TOP,fill=X)

        self.directory = StringVar()
        self.directory.set('D:\Projekty\TivaWare_C_Series-2.1.2.111\examples\section_brd_fw')
        self.dirEntry = Entry(self.dirLabelfrm,textvariable=self.directory)
        self.dirEntry.pack(side=LEFT,fill=X,expand=True)
        self.dirButton = Button(self.dirLabelfrm,text='SELECT',
                                command=self.selectdir)
        self.dirButton.pack(side=LEFT,padx=3)

        self.cmdLabelfrm = LabelFrame(self.mainfrm,text='Command',padding='3 3 3 3')
        self.cmdLabelfrm.pack(side=TOP,fill=X)

        self.command = StringVar()
        self.command.set('make program_win')
        self.cmdEntry = Entry(self.cmdLabelfrm,textvariable=self.command)
        self.cmdEntry.pack(side=LEFT,fill=X,expand=True)
        self.cmdButton = Button(self.cmdLabelfrm,text='RUN',
                                command=self.run)
        self.cmdButton.pack(side=LEFT,padx=3)

        self.retColor = self.cmdButton.cget('bg')

    def on_closing(self):
        if self.serialButton['text']!='CONNECT':
            self.connect()
        root.destroy()

    def scanPorts(self):
        ports = serscan.scan()
        portnames = []
        for port in ports:
            portnames.append(port[1])
        self.ports = portnames

    def setBgColor(self,wdget,color):
        c = wdget.cget('bg')
        wdget['bg']=color
        return c

    def selectdir(self):
        pass

    def connect(self):
        if self.serialButton['text']=='CONNECT':
            portName = self.serialCombo.get()
            #print(portName)
            self.thread = commThread(portName,self.conRet,self.run)
            self.thread.start()
            self.serialButton['text']='DISCONNECT'
        else:
            self.thread.stop()

    def conTest(self):
        return(self.retColor)

    def conRet(self,retVal):
        self.serialButton['text']='CONNECT' 
        #print(retVal)
            
    def run(self):
        try:
            ret = subprocess.call('make program_win',cwd=r'{}'.format(self.directory.get()))
            if ret==0:
                self.setBgColor(self.cmdButton,'lightgreen')
            else:
                self.setBgColor(self.cmdButton,'red')
        except:
            self.setBgColor(self.cmdButton,'red')
        root.update_idletasks()
        root.after(600,lambda w=self.cmdButton,c=self.retColor: self.setBgColor(w,c))

root = Tk()
gui = app(root)
root.mainloop()
