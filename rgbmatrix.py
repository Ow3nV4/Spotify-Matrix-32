from RGBMatrixEmulator import graphics, RGBMatrix, RGBMatrixOptions
import time
import sqlite3
import requests
from io import BytesIO
from PIL import Image
from PIL import ImageDraw

con = sqlite3.connect("list.db")
cur = con.cursor()
res = cur.execute("SELECT * FROM music ORDER BY plays DESC LIMIT 10")
res = res.fetchall()

count=0
c=0
i=0


options = RGBMatrixOptions()
options.rows=32
options.cols=64
options.chain_length=1
options.parallel=1
options.hardware_mapping='regular'
matrix = RGBMatrix(options=options) 
canvas = matrix.CreateFrameCanvas()

font = graphics.Font()
font.LoadFont("7x13.bdf")
redgreenblue = [graphics.Color(255,0,0),graphics.Color(0,255,0),graphics.Color(0,0,255)]

def textLength(index):
    return graphics.DrawText(canvas,font,pos,10,redgreenblue[0],res[index][1])


pos=32
lengthOfText = textLength(4)
pos2 = lengthOfText + 35 
while True:
    canvas.Clear()
    canvas.width = 64
    graphics.DrawText(canvas,font,pos,10,redgreenblue[0],res[4][1])
    graphics.DrawText(canvas,font,pos2,10,redgreenblue[1],res[4][1])
    pos-=1
    if pos + lengthOfText < 32:
        pos = lengthOfText + 35 
    pos2-=1
    if pos2 + lengthOfText < 32:
        pos2 = lengthOfText + 35 
    response = requests.get(res[count%10][4])
    image1= Image.open(BytesIO(response.content))
    image1.thumbnail((32,32), Image.ANTIALIAS)
    canvas.SetImage(image1.convert('RGB'))
    c+=1
    if c%100==0:
        count+=1
    canvas = matrix.SwapOnVSync(canvas)

