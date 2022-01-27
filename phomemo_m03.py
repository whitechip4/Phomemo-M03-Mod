#!python

#for Phomemo M03 

import serial
from PIL import Image,ImageEnhance


#For Phomemo M03 with USB connection
class Printer:
    

    #For Paper Select
    PAPER_WIDTH_58 = 0
    PAPER_WIDTH_80 = 1
    

    #CONST
    _MAX_WIDTH_80PAPER_PIX = 576     # for 80mm width paper
    _MAX_WIDTH_80PAPER_BYTE = 72     # Available area 72mm    203.2DPI

    _MAX_WIDTH_58PAPER_PIX = 384     # for 58mm width paper
    _MAX_WIDTH_58PAPER_BYTE = 48      #Available area 48mm    203.2DPI

    #COMMAND CONST
    _ESC= 0x1b
    _LF = 0x0a

    _INITIALIZE = [_ESC,0x40]             # [ESC @]

    _JUSTIFY_LEFT    = [_ESC,0x61,0x00]   # Justify select (Center)     ESC a [x]  (X=0:Left 1:center 2:right)
    _JUSTIFY_CENTER  = [_ESC,0x61,0x01]   # Justify select (Center)
    _JUSTIFY_RIGHT   = [_ESC,0x61,0x02]   # Justify select (Center)

    _FEED_FINISH = [_ESC,0x64,0x04]       # [ESC d (feed line num)]

    _GSV0 = [0x1d,0x76,0x30,0x00]        # GS v 0 [m]   ラスタイメージ印刷モード指定
                                        # m=0:等倍 1:横倍、2縦倍、3,縦横倍　とりあえず等倍で良さそう…？

    def __init__(self,target_com,paper_width) :
        """Initialization

        Args:
            target_com (str): COM Port name (ex: "COM1")
            paper_width (int): Paper width. Use Value defined in this class member
        """

        self.trg_comport = target_com   #Com name
        self.com =None
        
        if paper_width == Printer.PAPER_WIDTH_58:
            self.paper_width = Printer.PAPER_WIDTH_58
        else :
            self.paper_width = Printer.PAPER_WIDTH_80




    def connect_printer(self):
        """Connect to phomemo Printer

        Returns:
            int : result status (wip)
        """

        retval = 0
        try:
            self.com = serial.Serial(self.trg_comport,115200,timeout=1)
        except:
            retval = -1
        return retval

    def disconnect_printer(self):
        """Disconnect from phomemo printer
        """
        if self.com != None:
            if self.com.is_open:
                self.com.close()

    def send_data(self,data):
        """Send data for printer.
            com port must be opened before use this function.

        Args:
            data (list(int)): send data . the value of the each element must be 0~255
        """
        if self.com.is_open:
            if isinstance(data ,list):    
                self.com.write(bytes(data))
            else :
                self.com.write(bytes([data]))


    def print_img(self,img_path):
        """Print image (Test function)

        Args:
            img_path (str): image path 

        Returns:
            int : result status (wip)
        """

        #width setting from paper width param of instance
        if self.paper_width == Printer.PAPER_WIDTH_58:
            g_max_width = Printer._MAX_WIDTH_58PAPER_PIX
            g_max_width_byte = Printer._MAX_WIDTH_58PAPER_BYTE
        else :
            g_max_width = Printer._MAX_WIDTH_80PAPER_PIX
            g_max_width_byte = Printer._MAX_WIDTH_80PAPER_BYTE


        #image proessing
        #image open
        img_test = Image.open(img_path)

        #Image Rotate to portrait
        if img_test.height <  img_test.width:   #短辺を横幅とする
            img_test = img_test.rotate(90,expand=True)

        #Image Resize (short side => Printer Max Width)
        height_tmp =  round(img_test.height * g_max_width / img_test.width)
        img_resized = img_test.resize((g_max_width,height_tmp))

        ##　メモ： リサイズしない感じにする場合、横幅が8ビットで割り切れないときは面倒くさくなりそうなので、横幅まで余白埋めしてしまう方がよさそう

        #Image processing (Test)
        enhancer = ImageEnhance.Contrast(img_resized)  
        img_resized = enhancer.enhance(1.1)

        enhancer = ImageEnhance.Brightness(img_resized)  
        img_resized = enhancer.enhance(1.1)

        enhancer = ImageEnhance.Sharpness(img_resized)  
        img_resized = enhancer.enhance(3)

        #convert to binary image
        img_mono = img_resized.convert("L")      
        img_mono = img_mono.convert("1")        

        #!image processing



        #prepare image size data command 
        height_tmp_higher = int(img_mono.height / 256)
        height_tmp_lower = img_mono.height % 256
        width_byte = int(img_mono.width/8)  

        cmd_imgsize = [width_byte,0x00,height_tmp_lower,height_tmp_higher]  #画像サイズ　(x1,x2,y1,y2 として、　x1 + 256 * x2 が横幅みたいな感じ。yも同様  )
                                                                            #そんでこの後に必要となるデータ数は  (x1 + 256 * x2) *8bit * 縦列　という感じ 
                                                                            #1bit = 1pix

        #prepare datas from image for send to printer
        cmd_data = []   

        for y in range (img_mono.height):   #vert
            for x in range(width_byte):         # line

                #1pixel=1bitとして、8ピクセル->1バイトにまとめていく
                tmp_byte = 0    
                for bit in range (8) :            #bit
                    tmp_byte = tmp_byte << 1
                    if img_mono.getpixel( (( (width_byte - 1 -x) * 8 + (7 - bit)) , img_mono.height-y-1)) == 0:     #x,yのピクセル値を取得(モノクロイメージなのでbit)
                        tmp_byte |= 0x01                                                                            #0の場合はそのピクセルのビットを立てる
                                                                                                                    #画像が上下逆に出てくるのが気に入らなかったのでピクセル指定がちょっとアレな感じになっている
            
                if tmp_byte == 0x0A:     #0x0a(LF)を送信すると改行になってしまう模様（要検証）
                    tmp_byte = tmp_byte << 1      # 0b00001010 → 0b000101000 と1ビットシフトし誤魔化し処理をする

                cmd_data.append(tmp_byte)   #append to image data for send 

        # connect to printer
        self.connect_printer()

        # send Header
        cmd_header = [*Printer._INITIALIZE,*Printer._JUSTIFY_CENTER]
        self.send_data(cmd_header)

        #send image print command
        self.send_data([*Printer._GSV0,*cmd_imgsize])    #Send print bitimage command and image size
        
        #send image data         
        data_len = len(cmd_data)    
        for i in range(int(data_len/256)+1):    #長尺時バッファ溢れてるっぽいので、分割送信 256byteずつ
            if (data_len - 256 * i) > 0:
                tmp_data = cmd_data[(i*256):((i+1)*256)]
            else:
                tmp_data = cmd_data[(i*256):]

            self.send_data(tmp_data)  


        #feed when finished
        self.send_data(Printer._FEED_FINISH)

        #Wait for printing to finish
        while True:
            self.com.write([0x1F,0x11,0x0E])    #get command
            try :
                ret = self.com.read()   
            except: 
                continue
            
            if ret != b'':      #if printer status is not busy , some responce returned
                break
            
        self.disconnect_printer()

        return 0





