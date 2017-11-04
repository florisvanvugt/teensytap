


baudrate = 9600 # for the discrete data transfer rate (has to match with the Teensy script)

serial_timeout = .01 # the timeout (in seconds) for port reading



# Define the communication protocol with the Teensy (needs to match the corresponding variables in Teensy)
MESSAGE_CONFIG             = 88 # not actually used -- for the tapping
MESSAGE_DELAYDETECT_CONFIG = 66
MESSAGE_START              = 77
MESSAGE_STOP               = 55



# The delays to be presented (in ms)
DELAYS = [ 0, 25, 50, 75, 100, 125, 150, 175, 200 ]

# How often each delay is presented
N_REPETITIONS = 10



import sys

if (sys.version_info > (3, 0)): # Python 3
    from tkinter import *
    from tkinter import messagebox
    from tkinter.scrolledtext import ScrolledText
    from tkinter import filedialog
else: # probably Python 2
    from Tkinter import *
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    from ScrolledText import ScrolledText

import glob
import time
import struct
import os
import random




def error_message(msg):
    print(msg)
    messagebox.showinfo("Error", msg)
    return


def show_message(msg):
    print(msg)
    messagebox.showinfo("Message", msg)
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
        error_message("Cannot open USB port %s. Is the device connected?\n"%port)
        config["capturing"]=False
        return False

    config["comm"]=comm
    config["capturing"]=True
    output("Now listening to serial port %s\n"%port)
    
    update_enabled()
    



def browse_serial():
    # Browse for serial port
    comm = config["commport"].get()
    if not os.path.exists(comm):
        comm = guess_serial()

    file_path_string = filedialog.askopenfilename(initialdir="/dev/",
                                                  title="Select serial communication port",
                                                  filetypes=(("tty","tty*"),("all files","*.*")),
                                                  initialfile=comm)
    if file_path_string:
        config["commport"].set(file_path_string)
    


    
def guess_serial():
    # Try to automatically find the serial port
    acm = '/dev/ttyACM0'
    if os.path.exists(acm):
        return acm

    candidates = glob.glob('/dev/tty.usb*')
    if len(candidates)>0:
        return candidates[0]

    return acm # the default
    

    
    
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

            # Add this to the incoming buffer
            config["in.buffer"]+=msg
            
            output(msg)


            
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
                      




def update_enabled():
    """ Update the state of buttons depending on our state."""
    config["go.button"]   .configure(state=NORMAL if config["capturing"] else DISABLED)
    config["abort.button"].configure(state=NORMAL if config["capturing"] and config["running"] else DISABLED)
    config["firstb"] .configure(state=NORMAL if config["running.block"] else DISABLED)
    config["secondb"].configure(state=NORMAL if config["running.block"] else DISABLED)
    config["singletrb"].configure(state=NORMAL if config["capturing"] else DISABLED)








def start_teensy_trial(delay1,delay2):
    """ This function runs one delay detection trial.
    delay1 is the delay to be given on the first tap,
    delay2 is, surprise, the delay for the second note."""

    # Communicate this to the Teensy

    # First, tell Teensy to stop whatever it is it is doing at the moment (go to non-active mode)
    config["comm"].write(struct.pack('!B',MESSAGE_STOP))

    output("Starting trial on Teensy...")
    
    # Now we tell Teensy that we are going to send some config information
    config["comm"].write(struct.pack('!B',MESSAGE_DELAYDETECT_CONFIG))
    config["comm"].write(struct.pack('2i',delay1,delay2))
    
    time.sleep(1) # Just wait a moment to allow Teensy to process (not sure if this is actually necessary)

    # Okay, when it has swallowed all this, now we can make it start!
    config["comm"].write(struct.pack('!B',MESSAGE_START))
    config["running"] = True
    config["delay1"]=delay1
    config["delay2"]=delay2
    
    config["in.buffer"]="" # empty the buffer (which should just contain the messages for this trial)
        
    update_enabled()
    return True




def next_trial():
    """ Present the next trial. """

    config["trial"]+=1
    config["timestamp"]=time.strftime("%Y%m%d_%H%M%S")
    config["response"]="N/A"

    if config["trial"]>=len(config["trials"]):
        config["running.block"]=False
        config["running"]      =False
        show_message("Block completed.")
        
    
    # The delay to be tested on this trial
    delay = config["trials"][config["trial"]]

    delays = [delay,0]
    random.shuffle(delays)

    start_teensy_trial(delays[0],delays[1])

    


def single_trial():
    """ Run just one trial """
               
    config["running"]=False
    update_enabled()

    # Need to communicate this to the Teensy
    # Verify that string data is really an integer
    trialinfo={}

    # Grab the info from the text box
    for v in ["delay1","delay2"]:
        trialinfo[v] = config[v+"var"].get()

    # Recode the data as integers
    for val in ["delay1","delay2"]:
        trialinfo[val] = check_and_convert_int(val,trialinfo)
        if trialinfo[val]==None:
            return False # Conversion failed


    start_teensy_trial(trialinfo["delay1"],trialinfo["delay2"])
        



def write_log_header():
    header = "trial timestamp delay1 delay2 tap1.t tap2.t sound1.t sound2.t response"
    with open(config["out.filename"],'a') as f:
        f.write(header+"\n")
    
    

def process_response():
    """ The subject has responded something, and now we process the 
    data we got from Teensy to put into the log file."""

    # Make a little report about this trial

    # Here I need to process the incoming buffer
    config["in.buffer"]

    tap1t,tap2t= -1,-1 # get this from the Teensy output
    fb1t,fb2t=-1,-1
    
    report = "%i %s %i %i %d %d %d %d %s"%(config["trial"],
                                           config["timestamp"],
                                           config["delay1"],
                                           config["delay2"],
                                           tap1t,
                                           tap2t,
                                           fb1t,
                                           fb2t,
                                           config["response"])

    # Output to file if we have a output filename
    with open(config["out.filename"],'a') as f:
        f.write(report+"\n")

    output(report)
        
    next_trial()
    


def respond_first():
    """ Collects the response that the subject said "first" """
    config["response"]="first"
    process_response()


def respond_second():
    """ Collects the response that the subject said "second" """
    config["response"]="second"
    process_response()

    


def start_block():
    """
    This is when we run a block of trials
    """
    config["running"]=False
    update_enabled()

    ## Prepare the trials to be run
    trials = []
    
    for _ in range(N_REPETITIONS):
        block = DELAYS[:]
        random.shuffle(block)
        trials+=block
        
    config["trials"] = trials

    output("")
    output("Prepared %i trials"%len(config["trials"]))

    # Create the output file
    subjectid = config["subj"].get().strip()
    outdir = os.path.join('data',subjectid)
    if not os.path.exists(outdir): 
        os.makedirs(outdir)
    outf = os.path.join(outdir,"%s_delaydetection_%s.txt"%(subjectid,time.strftime("%Y%m%d_%H%M%S")))
    config["out.filename"]=outf
    write_log_header()
    output("")
    output("Output to %s"%config["out.filename"])

    
    config["trial"] = -1
    config["running.block"]=True
    next_trial()
    

    
    
    
def abort():
    config["comm"].write(struct.pack('!B',MESSAGE_STOP))
    config["running"]=False
    update_enabled()
    
    


def build_gui():
    
    #
    # 
    # Build the GUI
    #
    #

    # Set up the main interface scree
    w,h= 800,600
    
    master = Tk() #"TeensyTap")
    master.title("Delay Detection")
    master.geometry('%dx%d+%d+%d' % (w, h, 500, 200))

    buttonframe = Frame(master) #,padding="3 3 12 12")

    buttonframe.pack(padx=10,pady=10)

    row = 0
    openb = Button(buttonframe,text="open",        command=openserial)
    openb.grid(column=2, row=row, sticky=W)
    browseb = Button(buttonframe,text="browse",    command=browse_serial)
    browseb.grid(column=3, row=row, sticky=W)
    commport = StringVar()
    commport.set(guess_serial()) # default comm port
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
    Label(buttonframe, text="Single Trial").grid(column=0,row=row,sticky=E,pady=30)

    
    row += 1
    Label(buttonframe, text="delay 1").grid(column=0,row=row,sticky=E,pady=0)
    config["delay1var"] = StringVar()
    config["delay1var"].set("0")
    Entry(buttonframe,textvariable=config["delay1var"]).grid(column=1,row=row,sticky=W)

    row += 1
    Label(buttonframe, text="delay 2").grid(column=0,row=row,sticky=E)
    config["delay2var"] = StringVar()
    config["delay2var"].set("150")
    Entry(buttonframe,textvariable=config["delay2var"]).grid(column=1,row=row,sticky=W)
    
    config["singletrb"]=Button(buttonframe,
                               text="single trial",
                               command=single_trial,
                               #background="green",
                               #activebackground="lightgreen"
    )
    config["singletrb"].grid(column=3, row=row, sticky=W, padx=5)

    row += 1
    Label(buttonframe, text="Run block").grid(column=0,row=row,sticky=E,pady=35)

    row += 1
    #Button(buttonframe,text="configure",     command=launch) .grid(column=2, row=row, sticky=W, padx=5,pady=20)
    config["go.button"]=Button(buttonframe,
                               text="start block",
                               command=start_block,
                               background="green",
                               activebackground="lightgreen")
    config["go.button"].grid(column=3, row=row, sticky=W, padx=5)
    config["abort.button"]=Button(buttonframe,
                                  text="abort",
                                  command=abort,
                                  background="red",
                                  activebackground="darkred")
    config["abort.button"].grid(column=4, row=row, sticky=W, padx=5)
    
    row +=1

    config["firstb"]=Button(buttonframe,
                            text="respond first tap delayed",
                            command=respond_first)
    config["firstb"].grid(column=1, row=row, sticky=W, padx=5)

    row+=1
    config["secondb"]=Button(buttonframe,
                            text="respond second tap delayed",
                             command=respond_second)
    config["secondb"].grid(column=1, row=row, sticky=W, padx=5,pady=10)

    
    
    row+=1
    report = ScrolledText(master)
    report.pack(padx=10,pady=10,fill=BOTH,expand=True)
    config["report"]=report


    # Draw the background against which everything else is going to happen
    master.protocol("WM_DELETE_WINDOW", on_closing)

    config["master"]=master


    update_enabled()



            
            
global config
config = {}
config["capturing"]     =False
config["running"]       =False
config["running.block"] =False
config["in.buffer"]     =""



build_gui()


keep_going = True

while keep_going:

    listen()

    config["master"].update_idletasks()
    config["master"].update()
    
    time.sleep(0.01) # frame rate of our GUI update

    
