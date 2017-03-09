from tkinter import *
from tkinter.ttk import *
from tkinter import Button
from tkinter import filedialog

import sys
import subprocess
import threading
import serial

import serscan

import xml.etree.ElementTree as ET


defaultPort = 'select port'
defaultAutoconnect = 'False'
defaultDirectory = 'select directory'
defaultCommand = 'put command here'

defaultPortStrings = ('COM1','COM2','COM3')


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
        try:
            root.iconbitmap(r'button.ico')
        except:
            pass
        root.resizable(False,False)

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.mainfrm = Frame(root,padding='3 3 3 3')
        self.mainfrm.pack(side=TOP,fill=BOTH)

        self.portLabelfrm = LabelFrame(self.mainfrm,text='Port',padding='3 3 3 3')
        self.portLabelfrm.pack(side=TOP,fill=X)

        self.serialLabel = Label(self.portLabelfrm,text='Name:')
        self.serialLabel.pack(side=LEFT)
        self.portStr = StringVar()
        self.ports = defaultPortStrings
        #self.scanPorts()
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
        self.directory.set(defaultDirectory)
        self.dirEntry = Entry(self.dirLabelfrm,textvariable=self.directory)
        self.dirEntry.pack(side=LEFT,fill=X,expand=True)
        self.dirButton = Button(self.dirLabelfrm,text='SELECT',
                                command=self.selectdir)
        self.dirButton.pack(side=LEFT,padx=3)

        self.cmdLabelfrm = LabelFrame(self.mainfrm,text='Command',padding='3 3 3 3')
        self.cmdLabelfrm.pack(side=TOP,fill=X)

        self.command = StringVar()
        self.command.set(defaultCommand)
        self.cmdEntry = Entry(self.cmdLabelfrm,textvariable=self.command)
        self.cmdEntry.pack(side=LEFT,fill=X,expand=True)
        self.cmdButton = Button(self.cmdLabelfrm,text='RUN',
                                command=self.run)
        self.cmdButton.pack(side=LEFT,padx=3)

        self.retColor = self.cmdButton.cget('bg')

        self.load_config()

    def load_config(self):
        try:
            self.configtree = ET.parse('config.xml')
            self.config = self.configtree.getroot()
        except:
            #config file doesnt exist (most probably)
            self.config = ET.Element('config')
            portElement = ET.SubElement(self.config,'port')
            portElement.text = defaultPort
            autoElement = ET.SubElement(self.config,'autoconnect')
            autoElement.text = defaultAutoconnect
            dirElement = ET.SubElement(self.config,'directory')
            dirElement.text = defaultDirectory
            cmdElement = ET.SubElement(self.config,'command')
            cmdElement.text = defaultCommand
            f = open('config.xml','w')
            f.write(ET.tostring(self.config).decode('utf8'))
            f.close()
            self.configtree = ET.parse('config.xml')
            self.config = self.configtree.getroot()

        try:
            self.portStr.set(self.config.find('port').text)
        except:
            portElement = ET.SubElement(self.config,'port')
            portElement.text = defaultPort

        try:
            self.directory.set(self.config.find('directory').text)
        except:
            dirElement = ET.SubElement(self.config,'directory')
            dirElement.text = defalutDirectory

        try:
            self.command.set(self.config.find('command').text)
        except:
            cmdElement = ET.SubElement(self.config,'command')
            cmdElement.text = defaultCommand
        
        try:
            if self.config.find('autoconnect').text=='True':
                self.autoVar.set(True)
                self.connect()
            else:
                self.autoVar.set(False)
        except:
            autoElement = ET.SubElement(self.config,'autoconnect')
            autoElement.text = defaultAutoconnect

    def save_config(self):
        self.config.find('port').text = self.portStr.get()
        self.config.find('autoconnect').text = 'False' if self.autoVar.get()==0 else 'True'
        self.config.find('directory').text = self.directory.get()
        self.config.find('command').text = self.command.get()
        self.configtree.write('config.xml')

    def on_closing(self):
        if self.serialButton['text']!='CONNECT':
            self.connect()
        else:
            self.portOK = True
        self.save_config()
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
        dir = filedialog.askdirectory()
        if dir!='':
            self.directory.set(dir)

    def connect(self):
        if self.serialButton['text']=='CONNECT':
            portName = self.serialCombo.get()
            self.thread = commThread(portName,self.conRet,self.run)
            self.thread.start()
            self.serialButton['text']='DISCONNECT'
        else:
            self.thread.stop()

    def conRet(self,retVal):
        if retVal=='OK':
            self.portOK = True
        self.serialButton['text']='CONNECT' 
            
    def run(self):
        try:
        #if True:
            cmd = r'{}'.format(self.command.get())
            print(cmd)
            dir = r'{}'.format(self.directory.get())
            print(dir)
            #os.system(cmd,cwd=dir)
            #subprocess.Popen(self.command.get(),cwd=r'{}'.format(self.directory.get()),shell=True)
            ret = subprocess.call(dir+cmd,cwd=dir)
            if ret==0:
                self.setBgColor(self.cmdButton,'lightgreen')
                self.cmdOK = True
            else:
                self.setBgColor(self.cmdButton,'red')
        except:
            print(sys.exc_info())
            self.setBgColor(self.cmdButton,'red')
        root.update_idletasks()
        root.after(600,lambda w=self.cmdButton,c=self.retColor: self.setBgColor(w,c))


if __name__ == "__main__":
    
    root = Tk()
    gui = app(root)
    root.mainloop()
