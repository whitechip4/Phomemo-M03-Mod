#!python

#for Phomemo M03 

import serial
from PIL import Image

#CONST
MAX_WIDTH_80PAPER_PIX = 576     # for 80mm width paper
MAX_WIDTH_80PAPER_BYTE = 72     # Available area 72mm    203.2DPI

MAX_WIDTH_58PAPER_PIX = 384     # for 58mm width paper
MAX_WIDTH_58PAPER_BYTE = 48      #Available area 48mm    203.2DPI

ESC= 0x1b
LF = 0x0a

INITIALIZE = [ESC,0x40]     # [ESC @]

JUSTIFY_LEFT    = [ESC,0x61,0x00]   # Justify select (Center)     ESC a [x]  (X=0:Left 1:center 2:right)
JUSTIFY_CENTER  = [ESC,0x61,0x01]   # Justify select (Center)
JUSTIFY_RIGHT   = [ESC,0x61,0x02]   # Justify select (Center)


# HEADER_ETC = [0x1f,0x11,0x02,0x04]                                            #他のHackしてる人はヘッダ最後にこれを付加している コマンド探してもUS(0x1f)から始まるコマンドが無い
#                                                                               #Bluetooth系の独自コマンド…？　有線だと無くても動く
# FOOTER   = [0x1f,0x11,0x08,0x1f,0x11,0x0e,0x1f,0x11,0x07,0x1f,0x11,0x09]      #特殊コマンド…？ これもBluetooth系？　有線だと無くても動いてる。無線化したときに考える

FEED_FINISH = [ESC,0x64,0x02]              # [ESC d フィード行数]

GSV0 = [0x1d,0x76,0x30,0x00]        # GS v 0 [m]   ラスタイメージ印刷モード指定
                                    # m=0:等倍 1:横倍、2縦倍、3,縦横倍　とりあえず等倍で良さそう…？

#########################################

g_max_width = MAX_WIDTH_80PAPER_PIX
g_max_width_byte = MAX_WIDTH_80PAPER_BYTE


#COM PORT OPEN (今決め打ち)
com = serial.Serial("COM3",115200)


#image open
img_test = Image.open("img.jpg")

#場合によって画像回転
if img_test.height <  img_test.width:   #短辺を横幅とする
    img_test = img_test.rotate(90,expand=True)

#リサイズ…処理　（小さいサイズの場合はやらないとかでもいいかも
height_tmp =  round(img_test.height * g_max_width / img_test.width)
img_resized = img_test.resize((g_max_width,height_tmp))

##　メモ： リサイズしない感じにする場合、横幅が8ビットで割り切れないときは面倒くさくなりそうなので、横幅まで余白埋めしてしまう方がよさそう


#とりあえずライブラリで2値化
img_mono = img_resized.convert("L")      #いったんグレースケール
img_mono = img_mono.convert("1")        #とりあえず適当にディザリング

#img_mono.show()
height_tmp_higher = int(img_mono.height / 256)
height_tmp_lower = img_mono.height % 256

width_byte = int(img_mono.width/8)  #計算で必要なので、横幅をバイト単位に直しておく


cmd_imgsize = [width_byte,0x00,height_tmp_lower,height_tmp_higher]  #画像サイズ　(x1,x2,y1,y2 として、　x1 + 256 * x2 が横幅みたいな感じ。yも同様  )
                                                                    #そんでこの後に必要となるデータ数は  (x1 + 256 * x2) *8bit * 縦列　という感じ 
                                                                    #1bit = 1pix


#データ用意
cmd_data = []   #送信する本データ

for y in range (img_mono.height):   #vert
    for x in range(width_byte): # line
        tmp_byte = 0
        for bit in range (8) :            #bit
            tmp_byte = tmp_byte << 1
            if img_mono.getpixel( (( (width_byte - 1 -x) * 8 + (7 - bit)) , img_mono.height-y-1)) == 0:  #x,yのピクセル値を取得(モノクロイメージなのでbit)
                tmp_byte |= 0x01                                                                         #0の場合はそのピクセルのビットを立てる
    
        if tmp_byte == 0x0A:     #0x0a(LF)を送信すると改行になってしまう模様（要検証）
            tmp_byte = tmp_byte << 1      # 0b00001010 → 0b000101000 と1ビットシフトし誤魔化し処理をする

        cmd_data.append(tmp_byte)   #送信用点群データに追加


# #送信
#cmd_header = [*INITIALIZE,*JUSTIFY_CENTER,*HEADER_ETC] #なんかヘッダの最後の部分は投げなくても有線だと動くっぽい。謎なのでいったん保留

cmd_header = [*INITIALIZE,*JUSTIFY_CENTER]
com.write(bytes(cmd_header))
com.write(bytes([*GSV0,*cmd_imgsize]))    #画像モード指定と画像サイズ送信

#画像本体データ送信 
data_len = len(cmd_data)    
for i in range(int(data_len/256)+1):    #長尺時バッファ溢れてるっぽいので、分割送信
    if (data_len - 256 * i) > 0:
        tmp_data = cmd_data[(i*256):((i+1)*256)]
    else:
        tmp_data = cmd_data[(i*256):]

    #send data 
    com.write(bytes(tmp_data))  


#feed when finished
com.write(bytes(FEED_FINISH))

# #com.write(bytes(FOOTER)) #ヘッダ同様、有線だと動いてるのでいったん保留

com.close()