#!/usr/bin/env python3
from datetime import datetime, timedelta
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import time, sched, os, argparse, traceback

parser = argparse.ArgumentParser()
parser.add_argument('--test', action='store_true', help='Run this as a test rather than the real thing')
args = parser.parse_args()

def displayToEPD(image, clearToo):
    try:
        from waveshare_epd import epd4in2
        epd = epd4in2.EPD()
        epd.init()
        if(clearToo):
            epd.Clear()
        epd.display(epd.getbuffer(image))
        epd.sleep()
    except:
        traceback.print_exc()
        epd4in2.epdconfig.module_exit()

def saveToFile(image):
    image.save('test.png', 'PNG')

dateFmt = '%A %b %d %Y'
timeFmt = '%H:%M'
epd_size = (400, 300)

home = os.path.join(str(Path.home()), '.fonts')
curDir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.fonts')

def tryPath(filename):
    for basePath in [home, curDir, '/usr/share/fonts/truetype', '/usr/share/fonts/opentype']:
        trialPath = os.path.join(basePath, filename)
        if os.path.isfile(trialPath):
            return trialPath
    return None

def fitLargestFont(fontName, startSize, testString=None, maxHeight=None, maxWidth=None):
    if testString is None:
        testString = '00:00'
    if maxHeight is None and maxWidth is None:
        raise Exception('Must define at least one of maxHeight and maxWidth')
    noneOrSmaller = lambda siz, limit: limit is None or siz < limit
    size = startSize
    imageFont = ImageFont.truetype(fontName, size)
    while noneOrSmaller(imageFont.getsize(testString)[0], maxWidth) and noneOrSmaller(imageFont.getsize(testString)[1], maxHeight):
        size = size+2
        imageFont = ImageFont.truetype(fontName, size)
    return imageFont

fontName = tryPath('trs-million rg.ttf')
yearDayFontName = tryPath('digital-7 (mono).ttf')

# 0s are usually the widest numeral in base-10
testTimeString = '00:00'
# a Thursday (longest day name) in a 4 digit year in September (longest month name) with a 2 digit date
testDateString = datetime(2018, 9, 27).strftime(dateFmt)
targetTimeSize = (int(epd_size[0]), int(epd_size[1]*0.6))
targetDateSize = (int(epd_size[0]), int(epd_size[1]*0.4))

timeFont = fitLargestFont(fontName, 10, testString=testTimeString, maxWidth=targetTimeSize[0], maxHeight=targetTimeSize[1])
yearDayFont = fitLargestFont(yearDayFontName, 10, testString=testDateString, maxWidth=targetDateSize[0], maxHeight=targetDateSize[1])

def scheduleForNextMinute(function):
    now = datetime.now()
    next = (now+oneMinute).replace(second=0, microsecond=0)
    toDelay = next-now
    scheduler.enter(toDelay.total_seconds(), 1, function)

def drawTime():
    timeImage = Image.new('1', epd_size, 0xff)
    draw = ImageDraw.Draw(timeImage)

    now = datetime.now()
    # on the hour, flash the screen a few times to reduce ghosting
    clearScreen = False
    if now.strftime('%M') == '00' or now.strftime('%M') == '30':
        clearScreen = True
    
    timeStr = now.strftime('%H:%M')
    timeStrSize = timeFont.getsize(timeStr)
    timeOffsets = (int( (epd_size[0] - timeStrSize[0])/2 ), 0)
    yearDayStr = now.strftime('%A %b %d %Y')
    yearStrSize = yearDayFont.getsize(yearDayStr)
    yearOffsets = (int( (epd_size[0]-yearStrSize[0])/2), int(epd_size[1]*0.95-yearStrSize[1]))

    draw.text(timeOffsets, timeStr, font=timeFont, fill=0)
    draw.text(yearOffsets, yearDayStr, font=yearDayFont, fill=0)
    if args.test:
        saveToFile(timeImage)
    else:
        displayToEPD(timeImage, clearScreen)

drawTime()
