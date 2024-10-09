import spotipy
from spotipy.oauth2 import SpotifyOAuth
# import tkinter as tk
# from tkinter import *
# from tkinter import ttk
from SpotClass import SpotPy
from random import randint
import PIL
# from PIL import ImageTk
from PIL import Image
import requests
from io import BytesIO
import time
import schedule
import threading
import sqlite3
from RGBMatrixEmulator import graphics, RGBMatrix, RGBMatrixOptions
from PIL import ImageDraw
import os
from dotenv import load_dotenv



con = sqlite3.connect("list.db")
cur = con.cursor()

test = None
prev = 0
prevtime = 1000000
buff = 0
count=0
c=0
i=0
pos=32

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope="user-read-currently-playing"))

def nowPlaying():
    tr = sp.current_user_playing_track()
    if tr is None or tr['item']['is_local']==True:
        return False
    else:
        str = ""
        for i in range(len(tr['item']['artists'])):
            if(str == ""):
                str = (str +  tr['item']['artists'][i]['name'])
            else:
                str = (str + ", " + tr['item']['artists'][i]['name'])
        currentPlaying = SpotPy(tr['item']['name'], tr['item']['album']['name'], str, tr['item']['album']['images'][1]['url'],tr['item']['id'], tr['progress_ms'], tr['is_playing'],tr['item']['duration_ms'])
        return currentPlaying

music = nowPlaying()


def dbasecreate():
    cur.execute("CREATE TABLE music(songid, song, artists, album, image, plays)")
    con.commit()

def dbasedelete():
    cur.execute("DROP TABLE music")
    con.commit()

def dbase(songid, song, art, album, image, playback, playing, prev, prevtime):
    res = cur.execute("SELECT songid FROM music")
    changed = 0 
    songsids=res.fetchall()
    if playing == True:
        for songsID in songsids:
            if songsID[0] == songid:
                changed = 1
                if song!=prev or playback < prevtime:
                    plays = cur.execute("SELECT plays FROM music WHERE songid = (?)", (songid,))
                    plays = (plays.fetchall())[0][0]
                    plays+=1
                    cur.execute("UPDATE music SET plays = (?) WHERE songid = (?)", [plays,songid])
                    con.commit()
        if changed == 0:
            cur.execute("INSERT INTO music VALUES (?,?,?,?,?,1)", [songid, song, art, album, image])
            con.commit()      


def getTopPlaysStr():
    res = cur.execute("SELECT * FROM music ORDER BY plays DESC LIMIT 10")
    res = res.fetchall()
    string = ""
    for line in res:
        #print(line[5])
        string = string + line[1] + ", " + line[2] + ", " + line[3] + ", " + str(line[5]) + "\n"
    return string

def getTopPlays():
    res = cur.execute("SELECT * FROM music ORDER BY plays DESC LIMIT 5")
    res = res.fetchall()
    return res


topFive = getTopPlays()


def update():
    global test
    global prev
    global prevtime
    global music
    global topTen
    global buff
    global songname
    if music!= False:
        prev = music.song
        buff = 0
        songname = music.song
    music = nowPlaying()
    if music!=False:
        dbase(music.songid, music.song,music.artists,music.album,music.image, music.playback, music.playing, prev, prevtime)
        prevtime = music.playback
    else:
        topTen = getTopPlays()


def playthrough(current, duration):
    return ((current/duration)*100)
if music!= False:
    playt = playthrough(music.playback, music.duration)



options = RGBMatrixOptions()
options.rows=32
options.cols=64
options.chain_length=1
options.parallel=1
options.hardware_mapping='regular'
matrix = RGBMatrix(options=options) 
canvas = matrix.CreateFrameCanvas()

font = graphics.Font()
font.LoadFont("poke-8.bdf")
redgreenblue = [graphics.Color(255,0,0),graphics.Color(0,255,0),graphics.Color(0,0,255)]


def textLength(text):
    return graphics.DrawText(canvas,font,-50,-50,redgreenblue[2],text)

if music != False:
    lengthOfText = textLength(music.song)
    lengthOfText2 = textLength(music.artists)
else:
    lengthOfText = textLength(topFive[3][1])
    lengthOfText2=textLength(topFive[3][2])


pos2 = lengthOfText + 35 
pos3 = 32
pos4 = lengthOfText + 35
posart=32
posart2=35+lengthOfText2

def justChanged(songC, songP):
    if songC!=songP:
        return True
    else:
        return False


def drawCanvas():
    global count, c, i, pos, lengthOfText, pos2, canvas, pos3, pos4, len1, len2, prev, buff, playt, posart, posart2

    # Clear the canvas and set its width
    canvas.Clear()
    canvas.width = 64
    
    if music == False:
        # Get the length of the text
        len2 = textLength(topFive[3][1])

        # Draw the text at two different positions for a scrolling effect
        graphics.DrawText(canvas, font, pos, 10, redgreenblue[0], topFive[3][1])
        graphics.DrawText(canvas, font, pos2, 10, redgreenblue[1], topFive[3][1])
        
        # Move both positions leftward (for scrolling effect)
        pos -= 1
        pos2 -= 1
        
        # Smooth wrapping: if the text goes out of the canvas, reset it to just outside the right edge
        if pos + len2 < 0:
            pos = canvas.width  # Reset to the right side of the canvas
        if pos2 + len2 < 0:
            pos2 = canvas.width  # Reset to the right side of the canvas
        
        # Fetch and display the image (this part is the same)
        response = requests.get(topFive[count % 5][4])
        image1 = Image.open(BytesIO(response.content))
        image1.thumbnail((32, 32))  # Thumbnail image size (32x32)
        canvas.SetImage(image1.convert('RGB'))
        
        c += 1
        if c % 100 == 0:
            count += 1

    else:
        # Handle the music playback scrolling (similar adjustments can be made here)
        if pos is 32:
           songname = music.song
        len1 = textLength(music.song)
        lenart1 = textLength(music.artists)
        
        if justChanged(music.song, prev) == True and buff == 0:
            pos3 = 32
            pos4 = len1 + 35
            posart = 32
            posart2 = 35 + lenart1
            buff = 1
            songname = music.song
        
        graphics.DrawText(canvas, font, pos3, 8, redgreenblue[0],songname)
        graphics.DrawText(canvas, font, pos4, 8, redgreenblue[1],songname)
        
        # Scroll song title text
        pos3 -= 1
        pos4 -= 1
        print(f"pos: {pos3}, pos2: {pos4}, text length: {len1}")
        
        # Smooth wrapping for song text
        if pos3 + len1 < 0:
            pos3 = canvas.width
        if pos4 + len1 < 0:
            pos4 = canvas.width
        
        # Draw artist name and scroll it similarly
        graphics.DrawText(canvas, font, posart, 18, redgreenblue[0], music.artists)
        graphics.DrawText(canvas, font, posart2, 18, redgreenblue[1], music.artists)
        
        posart -= 1
        posart2 -= 1
        
        if posart + lenart1 < 0:
            posart = canvas.width
        if posart2 + lenart1 < 0:
            posart2 = canvas.width
        
        # Fetch and display album art (this part is unchanged)
        response = requests.get(music.image)
        image1 = Image.open(BytesIO(response.content))
        image1.thumbnail((32, 32))
        canvas.SetImage(image1.convert('RGB'))
        
        # Display progress bar for song playback
        playt = playthrough(music.playback, music.duration)
        for pl in range(26):
            if playt > (pl * (100 / 26)):
                graphics.DrawLine(canvas, 35 + pl, 25, 35 + pl, 27, redgreenblue[2])
        
        # Draw the progress bar frame
        graphics.DrawLine(canvas, 35, 24, 61, 24, redgreenblue[1])
        graphics.DrawLine(canvas, 35, 28, 61, 28, redgreenblue[1])
        graphics.DrawLine(canvas, 34, 24, 34, 28, redgreenblue[1])
        graphics.DrawLine(canvas, 61, 24, 61, 28, redgreenblue[1])
    
    # Swap the canvas buffer
    canvas = matrix.SwapOnVSync(canvas)






schedule.every(2).seconds.do(update)
# schedule.every(0.5).seconds.do(drawCanvas)


while True:
    drawCanvas()
    schedule.run_pending()
    time.sleep(0.2)


# root.mainloop()


#TODO artist on the most plays with a plays count line. See about removing the brackets in song name