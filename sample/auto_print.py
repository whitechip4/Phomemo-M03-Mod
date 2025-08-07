#!python

# Auto Print test program
""" This Script Ovserving specified directry and Auto Printing when added image file on that directory
"""

from phomemo_m03 import Printer

import time
import os
import queue

import shutil

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

from PIL import Image,ImageEnhance
import sys


# Dir Path
OBSERVE_DIR_PATH = "./phomemo_print_queue_folder"

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
        if ext == "TMP":  # ignore OneDrive tmp file(temp)
            return

        img_queue.put(event.src_path)
        img_num += 1


############ Main process
if __name__ == "__main__":

    if not os.path.exists(OBSERVE_DIR_PATH + "/ok"):
        os.makedirs(OBSERVE_DIR_PATH + "/ok")
    if not os.path.exists(OBSERVE_DIR_PATH + "/ng"):
        os.makedirs(OBSERVE_DIR_PATH + "/ng")

    # printer instance
    printer = Printer(PHOMEMO_COMPORT, Printer.PAPER_WIDTH_80)

    # watchdog setting
    path = OBSERVE_DIR_PATH
    event_handler = HandlerForWatchdog()
    observer = Observer()  # Observe setting
    observer.schedule(event_handler, path, recursive=False)
    observer.start()  # Start Observing

    print("target Directory : {}".format(OBSERVE_DIR_PATH))
    print("observing...")

    try:
        while True:
            time.sleep(1)

            # if file added
            if img_num > 0:
                img_num -= 1
                trg_path = img_queue.get()
                ext = os.path.splitext(trg_path)[1][1:]

                # added file is image -> print and move to ok directory
                # now gif file ignore because cannot use image enhancer , etc.
                if not ext == "png" and not ext == "jpg":
                    # move to ng directory if image is not png or jpg
                    shutil.move(
                        trg_path, OBSERVE_DIR_PATH + "/ng/" + os.path.basename(trg_path)
                    )

                    print(
                        "Cannot print : move to -> "
                        + OBSERVE_DIR_PATH
                        + "/ng/"
                        + os.path.basename(trg_path)
                    )
                    print("")
                    continue
                    
                print("Printing...")
                
                # image processing to adjust monochrome color
                proccesed_img = Image.open(trg_path)
                enhancer = ImageEnhance.Contrast(proccesed_img)  
                proccesed_img = enhancer.enhance(1.1)

                enhancer = ImageEnhance.Brightness(proccesed_img)  
                proccesed_img = enhancer.enhance(1.1)

                enhancer = ImageEnhance.Sharpness(proccesed_img)  
                proccesed_img = enhancer.enhance(3)
                base, ext = os.path.splitext(trg_path)
                processed_path = f"{base}_processed{ext}"
                proccesed_img.save(processed_path, quality=100)
            
                # print image
                #if printer.print_img(trg_path):
                if not printer.print_img(processed_path):
                    print("Print Failed : " + trg_path)
                    shutil.move(
                        trg_path, OBSERVE_DIR_PATH + "/ng/" + os.path.basename(trg_path)
                    )
                    print(
                        "Move to -> "
                        + OBSERVE_DIR_PATH
                        + "/ng/"
                        + os.path.basename(trg_path)
                    )
                    continue

                # move to ok directory
                # print(OBSERVE_DIR_PATH+"/ok/"+os.path.basename(trg_path))
                shutil.move(
                    trg_path, OBSERVE_DIR_PATH + "/ok/" + os.path.basename(trg_path)
                )
                print(
                    "Print Finished : move to -> "
                    + OBSERVE_DIR_PATH
                    + "/ok/"
                    + os.path.basename(trg_path)
                )

    except KeyboardInterrupt:  # for abort (CTRL + C)
        observer.stop()
        observer.join()
