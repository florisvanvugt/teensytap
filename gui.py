


baudrate = 9600 # for the discrete data transfer rate (has to match with the Teensy script)

serial_timeout = .01 # the timeout (in seconds) for port reading





from tkinter import *
import time

from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

try:
    import serial
except:
    msg = "An error occurred while importing the pySerial module.\n\nGo to https://pypi.python.org/pypi/pyserial to install the module,\nor refer to our manual for help.\n\nThe program will now quit."
    print(msg)
    messagebox.showinfo("Error importing pySerial", msg)
    sys.exit(-1)



def launch():
    # Launch a trial
    global config

    port = config["commport"].get()
    
    try:
        comm = serial.Serial(port, baudrate, timeout=0.01)
    except:
        print("Cannot open USB port %s. Is the device connected?\n"%port)
        config["capturing"]=False
        return False

    config["comm"]=comm
    config["capturing"]=True
    output("Now capturing\n")
    
    

def on_closing():
    global keep_going
    keep_going = False
    


def output(msg):
    # Function that shows output on the screen and in the terminal
    global config

    fmt = time.strftime('[%Y-%m-%d %H:%M:%S] ')
    msg = fmt + msg
    config["report"].insert(END,msg)
    config["report"].see(END) #scroll down to the end
    print(msg)
    

    
def listen():
    # Listen for incoming data on the COMM port
    global config

    if config["capturing"]:

        ln = config["comm"].readline()
        if ln!=None and len(ln)>0:
            # Probably an incoming tap
            msg= ln.decode('ascii')
            output(msg)
    




def build_gui():
    
    #
    # 
    # Build the GUI
    #
    #

    # Set up the main interface scree
    w,h= 800,600
    
    master = Tk()
    master.geometry('%dx%d+%d+%d' % (w, h, 500, 200))

    buttonframe = Frame(master) #,padding="3 3 12 12")

    buttonframe.pack(padx=10,pady=10)
    row = 0
    launchb = Button(buttonframe,text="launch",        command=launch) .grid(column=0, row=row, sticky=W)

    row+=1
    commport = StringVar()
    commport.set("/dev/ttyACM0") # default comm port
    Label(buttonframe, text="comm port").grid(column=0,row=row,sticky=W)
    ttydev  = Entry(buttonframe,textvariable=commport).grid(column=1,row=row,sticky=W)
    config["commport"]=commport

    row+=1
    report = ScrolledText(master)
    report.pack(padx=10,pady=10,fill=BOTH,expand=True)
    config["report"]=report


    # Draw the background against which everything else is going to happen
    master.protocol("WM_DELETE_WINDOW", on_closing)

    config["master"]=master





            
            
global config
config = {}
config["capturing"]=False





build_gui()


keep_going = True

while keep_going:

    listen()

    config["master"].update_idletasks()
    config["master"].update()
    
    time.sleep(0.01) # frame rate of our GUI update

    
