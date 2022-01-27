#!python

from phomemo_m03 import Printer

import tkinter as tk
from tkinter import filedialog

PHOMEMO_COMPORT="COM3"  #phomemo comport


if __name__ == '__main__':

    root = tk.Tk()
    root.withdraw()
    
    #printer instance
    printer = Printer(PHOMEMO_COMPORT,Printer.PAPER_WIDTH_80)

    #file select
    image_file = filedialog.askopenfilename(filetypes=[("JPGイメージ", "*.jpg"),("PNGイメージ", "*.png")])

    print("Target File : {}".format(image_file))
    print("")

    #print
    print("Printing...")
    printer.print_img(image_file)
    print("Finished.")
