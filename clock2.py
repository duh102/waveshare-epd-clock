#!/usr/bin/env python3
from datetime import datetime, timedelta
from waveshare_epd import epd4in2
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import time, sched, os

epd = epd4in2.EPD()
epd.init()

timeSizes = [128, 72, 48, 36, 24, 18, 12]
timeSize = 0

home = str(Path.home())

fontName = os.path.join(home, '.fonts', 'trs-million rg.ttf')
yearDayFontName = os.path.join(home, '.fonts', 'digital-7 (mono).ttf')
timeFont = ImageFont.truetype(fontName, timeSizes[timeSize])
yearDayFont = ImageFont.truetype(yearDayFontName, 30)

testString = '00:00'
testWidth = int(epd.width * 0.8)

while timeFont.getsize(testString)[0] > testWidth:
    if timeSize > len(timeSizes):
        raise Exception('Can\'t fit {} into the test width {} :('.format(testString, testWidth))
    timeSize+=1
    timeFont = ImageFont.truetype(fontName, timeSizes[timeSize])


# epd.GRAY1 is white
# GRAY4 is black
# GRAY 2 and 3 are increasingly dark
# For B&W images, use mode '1'
# For 4-color grayscale, use mode 'L'
oneMinute = timedelta(minutes=1)
scheduler = sched.scheduler()

def scheduleForNextMinute(function):
    now = datetime.now()
    next = (now+oneMinute).replace(second=0, microsecond=0)
    toDelay = next-now
    scheduler.enter(toDelay.total_seconds(), 1, function)

def drawTime():
    timeImage = Image.new('1', (epd.width, epd.height), epd.GRAY1)
    draw = ImageDraw.Draw(timeImage)

    now = datetime.now()
    # on the hour, flash the screen a few times to reduce ghosting
    if now.strftime('%M') == '00' or now.strftime('%M') == '30':
        draw.rectangle((0,0,epd.width,epd.height), fill=0)
        epd.display(epd.getbuffer(timeImage))
        draw.rectangle((0,0,epd.width,epd.height), fill=epd.GRAY1)
        epd.display(epd.getbuffer(timeImage))
    
    timeStr = now.strftime('%H:%M')
    timeStrSize = timeFont.getsize(timeStr)
    timeOffsets = (int( (epd.width - timeStrSize[0])/2 ), int( (epd.height-timeStrSize[1])/2 ))
    yearDayStr = now.strftime('%A %b %d %Y')
    yearStrSize = yearDayFont.getsize(yearDayStr)
    yearOffsets = (int( (epd.width-yearStrSize[0])/2), int(timeOffsets[1]+timeStrSize[1]+20))

    draw.text(timeOffsets, timeStr, font=timeFont, fill=0)
    draw.text(yearOffsets, yearDayStr, font=yearDayFont, fill=0)
    epd.display(epd.getbuffer(timeImage))

def drawAndSchedule():
    drawTime()
    scheduleForNextMinute(drawAndSchedule)

def notUsed():
    epd.Init_4Gray()
    Limage = Image.new('L', (epd.width, epd.height), 0)  # 255: clear the frame
    draw = ImageDraw.Draw(Limage)
    epd.display_4Gray(epd.getbuffer_4Gray(Limage))

drawAndSchedule()
scheduler.run()
