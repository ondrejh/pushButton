from tkinter import *
from tkinter.ttk import *
from tkinter import Button

import subprocess
import threading
import serial

portStrings = ('COM1','COM2','COM47')

class commThread(threading.Thread):
    def __init__(self, portName, retFcn, testFcn):
        threading.Thread.__init__(self)
        self.portName = portName
        self.retFcn = retFcn
        self.testParent = testFcn
        self.stopVal = False
    def run(self):
        try:
            with serial.Serial(self.portName,9600,timeout=0.1) as port:
                while True:
                    s = port.readlines()
                    if s!=b'':
                        print(s)
                    self.testParent()
                    if self.stopVal==True:
                        break
                self.retFcn('OK')
        except:
            self.retFcn('ERROR')
    def stop(self):
        self.stopVal = True

class app:
    def __init__(self, master):
        root.title("Push Button v0.1")
        root.resizable(False,False)

        self.mainfrm = Frame(root,padding='3 3 3 3')
        self.mainfrm.pack(side=TOP,fill=BOTH)

        self.portLabelfrm = LabelFrame(self.mainfrm,text='Port',padding='3 3 3 3')
        self.portLabelfrm.pack(side=TOP,fill=X)

        self.serialLabel = Label(self.portLabelfrm,text='Name:')
        self.serialLabel.pack(side=LEFT)
        self.portStr = StringVar()
        self.serialCombo = Combobox(self.portLabelfrm,textvariable=self.portStr,
                                    values=portStrings,width=10,justify=CENTER)
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

    def setBgColor(self,wdget,color):
        c = wdget.cget('bg')
        wdget['bg']=color
        return c

    def selectdir(self):
        pass

    def connect(self):
        if self.serialButton['text']=='CONNECT':
            portName = self.serialCombo.get()
            print(portName)
            self.thread = commThread(portName,self.conRet,self.conTest)
            self.thread.start()
            self.serialButton['text']='DISCONNECT'
        else:
            self.thread.stop()

    def conTest(self):
        return(self.retColor)

    def conRet(self,retVal):
        self.serialButton['text']='CONNECT' 
        print(retVal)
            
    def run(self):
        ret = subprocess.call('make program_win',cwd=r'{}'.format(self.directory.get()))
        if ret==0:
            self.setBgColor(self.cmdButton,'lightgreen')
        else:
            self.setBgColor(self.cmdButton,'red')
        root.after(600,lambda w=self.cmdButton,c=self.retColor: self.setBgColor(w,c))

root = Tk()
gui = app(root)
root.mainloop()
