


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
            output(msg)

            # If the message contains a trial completion signal
            if msg.find('Trial completed at')>-1:
                config["running"]=False
                update_enabled()
            
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
                      




def update_enabled():
    """ Update the state of buttons depending on our state."""
    config["go.button"]   .configure(state=NORMAL if config["capturing"] else DISABLED)
    config["abort.button"].configure(state=NORMAL if config["capturing"] and config["running"] else DISABLED)





    
def send_config():
    """ Communicate the settings for this trial to the Teensy """

    # First, let's collect and verify the data

    trialinfo = {}

    trialinfo["auditory.feedback"]           =config["auditoryfb"].get()
    trialinfo["auditory.fb.delay"]           =config["fbdelay"].get()
    trialinfo["metronome"]                   =config["metronome"].get()
    trialinfo["metronome.interval"]          =config["metronome_interval"].get()
    trialinfo["metronome.nclicks.predelay"]  =config["nclicks_predelay"].get()
    trialinfo["metronome.nclicks"]           =config["nclicks"].get()
    trialinfo["ncontinuation.clicks"]        =config["ncontinuation"].get()

    # Verify that string data is really an integer
    for val in ["auditory.fb.delay","metronome.interval","metronome.nclicks","ncontinuation.clicks","metronome.nclicks.predelay"]:
        trialinfo[val] = check_and_convert_int(val,trialinfo)
        if trialinfo[val]==None:
            return False # Conversion failed

    print(trialinfo)
    
    # Okay, so now we need to talk to Teensy to tell him to start this trial

    # First, tell Teensy to stop whatever it is it is doing at the moment (go to non-active mode)
    config["comm"].write(struct.pack('!B',MESSAGE_STOP))

    config["comm"].write(struct.pack('!B',MESSAGE_CONFIG))

    # Now we tell Teensy that we are going to send some config information
    config["comm"].write(struct.pack('7i',
                                     trialinfo["auditory.feedback"],
                                     trialinfo["auditory.fb.delay"],
                                     trialinfo["metronome"],
                                     trialinfo["metronome.interval"],
                                     trialinfo["metronome.nclicks.predelay"],
                                     trialinfo["metronome.nclicks"],
                                     trialinfo["ncontinuation.clicks"]))

    time.sleep(1) # Just wait a moment to allow Teensy to process (not sure if this is actually necessary)
    

    # Create the output file
    subjectid = config["subj"].get().strip()
    outdir = os.path.join('data',subjectid)
    if not os.path.exists(outdir): 
        os.makedirs(outdir)
    outf = os.path.join(outdir,"%s_%s.txt"%(subjectid,time.strftime("%Y%m%d_%H%M%S")))
    config["out.filename"]=outf
    output("")
    output("Output to %s"%config["out.filename"])

    return True
    






def run_one_trial(delay1,delay2):
    """ This function runs one delay detection trial.
    delay1 is the delay to be given on the first tap,
    delay2 is, surprise, the delay for the second note."""

    # Need to communicate this to the Teensy
    # Verify that string data is really an integer
    trialinfo={}

    # Grab the info from the text box
    for v in ["delay1","delay2"]:
        trialinfo[v] = config[v].get()

    # Recode the data as integers
    for val in ["delay1","delay2"]:
        trialinfo[val] = check_and_convert_int(val,trialinfo)
        if trialinfo[val]==None:
            return False # Conversion failed

    # TODO -- communicate this to the Teensy

    # First, tell Teensy to stop whatever it is it is doing at the moment (go to non-active mode)
    config["comm"].write(struct.pack('!B',MESSAGE_STOP))

    config["comm"].write(struct.pack('!B',MESSAGE_DELAYDETECT_CONFIG))

    # Now we tell Teensy that we are going to send some config information
    config["comm"].write(struct.pack('2i',
                                     trialinfo["delay1"],
                                     trialinfo["delay2"]))

    time.sleep(1) # Just wait a moment to allow Teensy to process (not sure if this is actually necessary)

    return True





def single_trial():
    config["running"]=False
    update_enabled()
    if send_config(): # this sends the configuration for the current trial
    
        # Okay, when it has swallowed all this, now we can make it start!
        config["comm"].write(struct.pack('!B',MESSAGE_START))
        config["running"]=True
    update_enabled()

    


def respond_first():
    """ Collects the response that the subject said "first" """
    pass


def respond_second():
    """ Collects the response that the subject said "second" """
    pass

    


def go():
    """
    This is when we run a block of trials
    """
    config["running"]=False
    update_enabled()

    ## Prepare the trials to be run
    trials = []
    
    for _ in N_REPETITIONS:
        block = DELAYS[:]
        random.shuffle(block)
        trials+=block
        
    config["trials"] = trials


    
    
    if send_config(): # this sends the configuration for the current trial
    
        # Okay, when it has swallowed all this, now we can make it start!
        config["comm"].write(struct.pack('!B',MESSAGE_START))
        config["running"]=True
    update_enabled()

    
    
    
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
    w,h= 800,500
    
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
    Label(buttonframe, text="Single Trial").grid(column=0,row=row,sticky=E,pady=20)

    
    row += 1
    Label(buttonframe, text="delay 1").grid(column=0,row=row,sticky=E,pady=0)
    config["delay1"] = StringVar()
    config["delay1"].set("0")
    Entry(buttonframe,textvariable=config["delay1"]).grid(column=1,row=row,sticky=W)

    row += 1
    Label(buttonframe, text="delay 1").grid(column=0,row=row,sticky=E)
    config["delay2"] = StringVar()
    config["delay2"].set("150")
    Entry(buttonframe,textvariable=config["delay2"]).grid(column=1,row=row,sticky=W)
    
    config["singletrb"]=Button(buttonframe,
                               text="single trial",
                               command=single_trial,
                               #background="green",
                               #activebackground="lightgreen"
    )
    config["singletrb"].grid(column=3, row=row, sticky=W, padx=5)

    row += 1
    Label(buttonframe, text="Run block").grid(column=0,row=row,sticky=E,pady=20)

    row += 1
    #Button(buttonframe,text="configure",     command=launch) .grid(column=2, row=row, sticky=W, padx=5,pady=20)
    config["go.button"]=Button(buttonframe,
                               text="start block",
                               command=go,
                               background="green",
                               activebackground="lightgreen")
    config["go.button"].grid(column=3, row=row, sticky=W, padx=5,pady=20)
    config["abort.button"]=Button(buttonframe,
                                  text="abort",
                                  command=abort,
                                  background="red",
                                  activebackground="darkred")
    config["abort.button"].grid(column=4, row=row, sticky=W, padx=5,pady=20)
    



    config["firstb"]=Button(buttonframe,
                            text="first tap delayed",
                            command=respond_first)
    config["firstb"].grid(column=1, row=row, sticky=W, padx=5,pady=20)

    row+=1
    config["secondb"]=Button(buttonframe,
                            text="second tap delayed",
                             command=respond_second)
    config["secondb"].grid(column=1, row=row, sticky=W, padx=5,pady=0)

    
    
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
config["capturing"]=False
config["running"]=False





build_gui()


keep_going = True

while keep_going:

    listen()

    config["master"].update_idletasks()
    config["master"].update()
    
    time.sleep(0.01) # frame rate of our GUI update

    
