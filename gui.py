


baudrate = 9600 # for the discrete data transfer rate (has to match with the Teensy script)

serial_timeout = .01 # the timeout (in seconds) for port reading



# Define the communication protocol with the Teensy (needs to match the corresponding variables in Teensy)
MESSAGE_CONFIG = 88
MESSAGE_START  = 77
MESSAGE_STOP   = 55




from tkinter import *
import time

from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import struct
import os


def error_message(msg):
    print(msg)
    messagebox.showinfo("Error", msg)
    return



try:
    import serial
except:
    msg = "An error occurred while importing the pySerial module.\n\nGo to https://pypi.python.org/pypi/pyserial to install the module,\nor refer to our manual for help.\n\nThe program will now quit."
    error_message(msg)
    sys.exit(-1)



def openserial():
    # Open serial communications with the Teensy
    # This assumes that the Teensy is connected (otherwise the device will not be created).
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
    config["report"].insert(END,msg+"\n")
    config["report"].see(END) #scroll down to the end
    print(msg)
    

    
def listen():
    # Listen for incoming data on the COMM port
    global config

    if config["capturing"]:

        ln = config["comm"].readline()
        if ln!=None and len(ln)>0:
            # Probably an incoming tap
            msg= ln.decode('ascii').strip()
            output(msg)

            # Output to file if we have a output filename
            if "out.filename" in config:
                with open(config["out.filename"],'a') as f:
                    f.write(msg+"\n")



            
def check_and_convert_int(key,datadict):
    """ Check that a particular key in the datadict is really associated with an int, and if so, cast it to that datatype."""
    if key not in datadict:
        error_message("Internal error -- %s variable is not set")
        return

    val = datadict[key].strip()
    
    if not val.isdigit():
        error_message("Error, you entered '%s' for %s but that has to be an integer (whole) number"%(val,key))
        return

    return int(val)
                      




def launch():
    # Launch a trial

    # First, let's collect and verify the data

    trialinfo = {}

    trialinfo["auditory.feedback"]   =config["auditoryfb"].get()
    trialinfo["auditory.fb.delay"]   =config["fbdelay"].get()
    trialinfo["metronome"]           =config["metronome"].get()
    trialinfo["metronome.interval"]  =config["metronome_interval"].get()
    trialinfo["metronome.nclicks"]   =config["nclicks"].get()
    trialinfo["ncontinuation.clicks"]=config["ncontinuation"].get()

    # Verify that string data is really an integer
    for val in ["auditory.fb.delay","metronome.interval","metronome.nclicks","ncontinuation.clicks"]:
        trialinfo[val] = check_and_convert_int(val,trialinfo)
        if trialinfo[val]==None:
            return # Conversion failed


    print(trialinfo)
    
    # Okay, so now we need to talk to Teensy to tell him to start this trial

    # First, tell Teensy to stop whatever it is it is doing at the moment (go to non-active mode)
    config["comm"].write(struct.pack('!B',MESSAGE_STOP))

    config["comm"].write(struct.pack('!B',MESSAGE_CONFIG))

    # Now we tell Teensy that we are going to send some config information
    config["comm"].write(struct.pack('6i',
                                     trialinfo["auditory.feedback"],
                                     trialinfo["auditory.fb.delay"],
                                     trialinfo["metronome"],
                                     trialinfo["metronome.interval"],
                                     trialinfo["metronome.nclicks"],
                                     trialinfo["ncontinuation.clicks"]))

    time.sleep(1) # Just wait a moment to allow Teensy to process
    

    # Create the output file
    subjectid = config["subj"].get().strip()
    outdir = os.path.join('data',subjectid)
    if not os.path.exists(outdir): 
        os.makedirs(outdir)
    outf = os.path.join(outdir,"%s_%s.txt"%(subjectid,time.strftime("%Y%m%d_%H%M%S")))
    config["out.filename"]=outf
    output("Output to %s"%config["out.filename"])


    
def go():
    # Okay, when it has swallowed all this, now we can make it start!
    config["comm"].write(struct.pack('!B',MESSAGE_START))

    
    
    
def abort():
    config["comm"].write(struct.pack('!B',MESSAGE_STOP))
    
    


def build_gui():
    
    #
    # 
    # Build the GUI
    #
    #

    # Set up the main interface scree
    w,h= 800,700
    
    master = Tk() #"TeensyTap")
    master.title("TeensyTap")
    master.geometry('%dx%d+%d+%d' % (w, h, 500, 200))

    buttonframe = Frame(master) #,padding="3 3 12 12")

    buttonframe.pack(padx=10,pady=10)

    row = 0
    openb = Button(buttonframe,text="open",        command=openserial) .grid(column=2, row=row, sticky=W)
    commport = StringVar()
    commport.set("/dev/ttyACM0") # default comm port
    Label(buttonframe, text="comm port").grid(column=0,row=row,sticky=W)
    ttydev  = Entry(buttonframe,textvariable=commport).grid(column=1,row=row,sticky=W)
    config["commport"]=commport

    row += 1 
    subj = StringVar()
    subj.set("subject") 
    Label(buttonframe, text="subject ID").grid(column=0,row=row,sticky=W)
    subjentry = Entry(buttonframe,textvariable=subj).grid(column=1,row=row,sticky=W)
    config["subj"]=subj

    
    row += 1
    config["auditoryfb"] = IntVar()
    c = Checkbutton(buttonframe, text="Auditory feedback", variable=config["auditoryfb"])
    c.grid(column=0,row=row,sticky=W,padx=5,pady=5)

    row+=1
    Label(buttonframe, text="delay").grid(column=0,row=row,sticky=E)
    config["fbdelay"] = StringVar()
    config["fbdelay"].set("0")
    Entry(buttonframe,textvariable=config["fbdelay"]).grid(column=1,row=row,sticky=W)
    Label(buttonframe, text="ms").grid(column=2,row=row,sticky=W)


    row += 1
    config["metronome"] = IntVar()
    c = Checkbutton(buttonframe, text="Metronome", variable=config["metronome"])
    c.grid(column=0,row=row,sticky=W,padx=5,pady=10)

    row += 1
    Label(buttonframe, text="interval").grid(column=0,row=row,sticky=E)
    config["metronome_interval"] = StringVar()
    config["metronome_interval"].set("600")
    Entry(buttonframe,textvariable=config["metronome_interval"]).grid(column=1,row=row,sticky=W)
    Label(buttonframe, text="ms").grid(column=2,row=row,sticky=W)


    row += 1
    Label(buttonframe, text="# clicks").grid(column=0,row=row,sticky=E)
    config["nclicks"] = StringVar()
    config["nclicks"].set("10")
    Entry(buttonframe,textvariable=config["nclicks"]).grid(column=1,row=row,sticky=W)


    row += 1
    Label(buttonframe, text="# continuation clicks").grid(column=0,row=row,sticky=E)
    config["ncontinuation"] = StringVar()
    config["ncontinuation"].set("10")
    Entry(buttonframe,textvariable=config["ncontinuation"]).grid(column=1,row=row,sticky=W)


    row += 1
    Button(buttonframe,text="configure",     command=launch) .grid(column=2, row=row, sticky=W, padx=5,pady=20)
    Button(buttonframe,text="go",            command=go)     .grid(column=3, row=row, sticky=W, padx=5,pady=20)
    Button(buttonframe,text="abort",         command=abort)  .grid(column=4, row=row, sticky=W, padx=5,pady=20)
    
    
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

    
