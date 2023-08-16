from tkinter import *
from tkinterdnd2 import *
from PIL import Image, ImageTk
import struct
import zlib
import sys
import os


class png_img:
    def __init__(self,inputfile):
        self.f = open(inputfile,'rb')
        self.imgdata = self.f.read()
        self.head = struct.unpack_from(">33s", self.imgdata, 0)
        if struct.unpack_from(">3s", self.imgdata, 1) == (b'PNG',):
            self.i_width = struct.unpack_from(">I", self.imgdata, 16)
            self.i_height = struct.unpack_from(">I", self.imgdata, 20)
            self.bit_depth = struct.unpack_from(">B", self.imgdata, 24)
            self.color_type = struct.unpack_from(">B", self.imgdata, 25)
            self.comp_method = struct.unpack_from(">B", self.imgdata, 26)
            self.filter_method = struct.unpack_from(">B", self.imgdata, 27)
            self.interlace_method = struct.unpack_from(">B", self.imgdata, 28)
            self.crc = struct.unpack_from(">B", self.imgdata, 29)
            self.count = 30
            self.idata_type = struct.unpack_from(">4s", self.imgdata, self.count)
            self.img_length = 0 
            self.img_data = b'' 
            self.cnt = 0        
            while self.idata_type != (b'IEND',):
                self.idata_type = struct.unpack_from(">4s", self.imgdata, self.count)
                if self.idata_type == (b'IDAT',):
                    self.idata_length = struct.unpack_from(">I",self.imgdata,self.count-4)
                    self.img_length += self.idata_length[0]
                    self.img_subdata = struct.unpack_from(">"+str(self.idata_length[0])+"s",self.imgdata,self.count+4)
                    self.img_data += self.img_subdata[0]
                    self.cnt += 1
                self.count += 1
            print('read OK','This Image is',self.count,'byte')
        else:
            print('This file is not PNG image')
        self.f.close()

    def searchTNK(self,thunk, outputfile):
        self.dmy1 = 0
        self.dmy2 = 0
        self.thunk_type = (b'',)
        with open(outputfile, 'w') as f:
            while self.thunk_type != (b'IEND',):
                self.thunk_type = struct.unpack_from(">4s", self.imgdata, self.dmy1)
                if self.thunk_type == (thunk,):
                    self.thunk_length = struct.unpack_from(">I",self.imgdata,self.dmy1-4)
                    self.thunk_value = struct.unpack_from(">"+str(self.thunk_length[0])+"s",self.imgdata,self.dmy1+4)
                    if self.dmy2 > 0:
                        s = self.thunk_value[0].decode('ascii') 
                        s = s.replace('workflow', '')
                        s = s[1:]
                        f.write(s + '\n')
                    self.dmy2 += 1
                self.dmy1 += 1
            if self.dmy2 == 0:
                f.write('no thunk ' + thunk.decode())


def drop(event):
    #print(event.data)
    p=png_img(event.data)
    s= os.path.basename(event.data)
   
    s = s.replace('.png','')
    p.searchTNK(b'tEXt', s + '.json')
    global display_image, canvas
    canvas.delete("image")
    img = Image.open(event.data)
    # 2. 画像のサイズを取得
    original_width, original_height = img.size
    # 3. 500x500のキャンバスに収まるようにリサイズするサイズを計算
    aspect_ratio = original_width / original_height
    if original_width > original_height:
        new_width = 500
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = 500
        new_width = int(new_height * aspect_ratio)
    resized_img = img.resize((new_width, new_height))

    display_image = ImageTk.PhotoImage(resized_img)
    canvas.create_image((500-new_width)/2, (500-new_height)/2, image = display_image, anchor = "nw")
    return event.action

# メインウィンドウの生成
display_image = None
root = TkinterDnD.Tk()
root.geometry("500x500")
root.title('PNG -> ComfyUI workflow')
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)
# Canvasウィジェットの生成
canvas = Canvas(root, width=640, height=480)
# ウィジェットの配置
canvas.pack()
root.mainloop()