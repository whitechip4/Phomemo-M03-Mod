# Phomemo M03 Printer Module
simple image printing python module for phomemo M03 Series (https://phomemo.com/collections/m03-series).

*This module tested only in Windows 10 PC.


## Requirement
* python3 
* pyserial 3.5
* pillow 9.0.0


## Usage
* connect to Phomemo M03 with USB Cable (Currently Bluetooth is not supported)
* simple application script as follows
   ```python
    from phomemo_03 import Printer

    printer = Printer("COM1",Printer.PAPER_WIDTH_80)        # Arguments is ComPort and Paper width
                                                            # *Paper width is 58mm and 80mm available
    printer.print_img("img.png")                            # print                                                        
   ```

## sample
Some sample application is in the sample folder  

* simple_print.py  
This script print the image you choose on dialog

* auto_print.py  
    This script ovserving specified directry and auto printing when added image file on that directory.  
    (need watchdog module. install ``` $pip install watchdog ``` before use)

## Todo 
* Error handling
* Bluetooth 
* process structure improvement