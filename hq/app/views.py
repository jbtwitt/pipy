import json
import math
from flask import render_template, request, redirect
from datetime import datetime, timedelta
import glob
import urllib
import os

from app import app

import hqrobot
from hqrobot import CsvFolder, CsvFileName, hqrobotMain
from HqMetaFile import JsonFile
from HqMeta import HqMeta
from HqCsv import HqCsv

HQ_CONF = 'hqrobot.json'
hqConf = json.load(open(HQ_CONF))
# print(hqConf)
dayDelta = -0
def getDays():
    return [(datetime.now() + timedelta(days=dayDelta)).strftime("%Y%m%d"),
            (datetime.now() + timedelta(days=dayDelta-1)).strftime("%Y%m%d"),
            (datetime.now() + timedelta(days=dayDelta-2)).strftime("%Y%m%d")]

days = getDays()

def getHqMetaFiles(hqConf, day):
    # hqMetaFiles = glob.glob(hqConf['repo'] + '/hqMeta*.json')
    # listFiles = hqMetaFiles[len(hqMetaFiles)-1:]
    # hqMetaFiles = []
    # for hqMetaFile in listFiles:
    #     hqMetaFiles.append(urllib.parse.urlencode({'hqMetaFile': hqMetaFile}))
    hqMetaFiles = []
    hqMetaFile = JsonFile.format(hqConf['repo'], day)
    hqMetaFiles.append(urllib.parse.urlencode({'hqMetaFile': hqMetaFile}))
    return hqMetaFiles

templateMeta = {
        "day": days[0],
        "days": days,
        "hqConf": hqConf,
        "hqMetaFiles": getHqMetaFiles(hqConf, days[0])
    }

def getHqMetas(hqConf, day, startDayIdx=0):
    tickers = hqConf["tickers"]
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    hqMetas = []
    for ticker in tickers:
        hqFile = CsvFileName.format(csvFolder, ticker)
        if os.path.exists(hqFile):
            hqMeta = HqMeta(ticker, hqFile)
            hqMetas.append(hqMeta.collect(startDayIdx))
    # hqMetas = sorted(hqMetas, key=lambda x: x['LP'])
    hqMetas = sorted(hqMetas, key=lambda x: (x['change']-x['LP']), reverse=True)
    return hqMetas

def getHqDailyMetas(hqConf, day, ticker, nDays=50):
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    csvFile = CsvFileName.format(csvFolder, ticker)
    hqMeta = HqMeta(ticker, csvFile)
    hqMetas = []
    for dayIdx in range(nDays):
        hqMetas.append(hqMeta.collect(dayIdx))
    return hqMetas

def getHqCsv(hqConf, ticker, day):
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    csvFile = CsvFileName.format(csvFolder, ticker)
    return HqCsv(ticker, csvFile)


@app.route('/')
def index():
    return render_template('index.html',
                            title='HQ',
                            templateMeta=templateMeta)

@app.route('/hqCsv')
def hqCsv():
    ticker = request.args.get('ticker')
    return render_template('hqCsv.html',
                           title='{} HqCsv'.format(ticker),
                           templateMeta=templateMeta,
                           hqCsv=getHqCsv(templateMeta['hqConf'], ticker, templateMeta['day']),
                           upAlert=0.05,
                           downAlert=-0.1,
                           round=round)

@app.route('/hqDailyMetas')
def hqDailyMetas():
    ticker = request.args.get('ticker')
    return render_template('hqDailyMetas.html',
                           title='{} HDM'.format(ticker),
                           templateMeta=templateMeta,
                           hqMetas=getHqDailyMetas(templateMeta['hqConf'], templateMeta['day'], ticker, 100),
                           upAlert=0.05,
                           downAlert=-0.1,
                           round=round)

@app.route('/hqMeta')
def hqMeta():
    hqMetaFile = request.args.get('hqMetaFile')
    hqMetas = json.load(open(hqMetaFile))
    hqMetas = sorted(hqMetas, key=lambda x: (x['change']-x['LP']), reverse=True)
    return render_template('hqMeta.html',
                           title='HQ Meta',
                           templateMeta=templateMeta,
                           hqMetas=hqMetas,
                           upAlert=0.1,
                           downAlert=-0.1,
                           round=round)

@app.route('/hqMeta/dayIdx')
def hqMetaStartDayIdx():
    startDayIdx = int(request.args.get('startDayIdx'))
    return render_template('hqMeta.html',
                           title='HQ Meta',
                           templateMeta=templateMeta,
                           hqMetas=getHqMetas(templateMeta['hqConf'], templateMeta['day'], startDayIdx),
                           upAlert=0.1,
                           downAlert=-0.1,
                           round=round)

@app.route('/hqrobot')
def hqrobot():
    days = getDays()
    templateMeta['days'] = days
    templateMeta['day'] = days[0]
    hqConf = json.load(open(HQ_CONF))
    hqrobotMain(hqConf, templateMeta['day'])
    templateMeta['hqConf'] = hqConf
    return redirect('/hqMeta/dayIdx?startDayIdx=0')

@app.route('/hqSetDay')
def hqSetDay():
    day = request.args.get('day')
    templateMeta['day'] = day
    templateMeta["hqMetaFiles"] = getHqMetaFiles(templateMeta['hqConf'], day)
    return redirect('/')

@app.route('/hqConf')
def hqConf():
    return open(HQ_CONF).read()
