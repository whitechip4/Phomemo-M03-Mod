#!python

#Auto Print test program
""" This Script Ovserving specified directry and Auto Printing when added image file on that directory
"""

from phomemo_m03 import Printer

import time
import os
import queue

import shutil

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

#Dir Path
OBSERVE_DIR_PATH = "D:/OneDrive/phomemo_print"

PHOMEMO_COMPORT = "COM3"

#
img_queue = queue.Queue()
img_num = 0

############  Watchdog handler
class HandlerForWatchdog(LoggingEventHandler):
    def on_created(self, event):   
        global img_queue
        global img_num
    
        print("File Added" + event.src_path)
        ext = os.path.splitext(event.src_path)[1][1:]
        if ext == 'TMP':    #ignore OneDrive tmp file(temp)
            return

        img_queue.put(event.src_path)
        img_num += 1
    

############ Main process
if __name__ == "__main__":

    if not os.path.exists(OBSERVE_DIR_PATH+"/ok"):  
        os.makedirs(OBSERVE_DIR_PATH+"/ok") 
    if not os.path.exists(OBSERVE_DIR_PATH+"/ng"):  
        os.makedirs(OBSERVE_DIR_PATH+"/ng") 

    #printer instance 
    printer = Printer(PHOMEMO_COMPORT,Printer.PAPER_WIDTH_80)

    #watchdog setting
    path = OBSERVE_DIR_PATH
    event_handler = HandlerForWatchdog()
    observer = Observer()       #Observe setting
    observer.schedule(          
        event_handler,
        path,
        recursive=False
        )
    observer.start()            #Start Observing



    try:
        while True:
            time.sleep(1)

            #if file added
            if img_num > 0:
                img_num-=1
                trg_path = img_queue.get()
                ext = os.path.splitext(trg_path)[1][1:]
                
                # added file is image -> print and move to ok directory
                if ext == 'png' or ext == 'jpg' :   # or ext == 'gif' : # now gif file ignore because cannot use image enhancer , etc.
                    #print image
                    printer.print_img(trg_path)
                
                    #move to ok directory
                    print(OBSERVE_DIR_PATH+"/ok/"+os.path.basename(trg_path))
                    shutil.move(trg_path, OBSERVE_DIR_PATH+"/ok/"+os.path.basename(trg_path))
                    print("Print Finished : move to -> " + OBSERVE_DIR_PATH+"/ok/"+os.path.basename(trg_path))
                
                # added file is not image -> move to ng directory
                else:
                    shutil.move(trg_path, OBSERVE_DIR_PATH+"/ng/"+os.path.basename(trg_path))
                
                    print("Cannot print : move to -> " + OBSERVE_DIR_PATH+"/ng/"+os.path.basename(trg_path))
                print("")
                

    except KeyboardInterrupt:   #for abort (CTRL + C)
        observer.stop()
        observer.join()


