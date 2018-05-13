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
print(hqConf)
dayDelta = -1
day = (datetime.now() + timedelta(days=dayDelta)).strftime("%Y%m%d")

def getHqMetas(hqConf, day, startDayIdx=0):
    tickers = hqConf["tickers"]
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    hqMetas = []
    for ticker in tickers:
        hqFile = CsvFileName.format(csvFolder, ticker)
        if os.path.exists(hqFile):
            hqMeta = HqMeta(ticker, hqFile)
            hqMetas.append(hqMeta.collect(startDayIdx))
    return hqMetas

def getHqMetaFiles():
    # hqMetaFiles = glob.glob(hqConf['repo'] + '/hqMeta*.json')
    # listFiles = hqMetaFiles[len(hqMetaFiles)-1:]
    # hqMetaFiles = []
    # for hqMetaFile in listFiles:
    #     hqMetaFiles.append(urllib.parse.urlencode({'hqMetaFile': hqMetaFile}))
    hqMetaFiles = []
    hqMetaFile = JsonFile.format(hqConf['repo'], day)
    hqMetaFiles.append(urllib.parse.urlencode({'hqMetaFile': hqMetaFile}))
    return hqMetaFiles

def getHqCsv(hqConf, ticker, day):
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    csvFile = CsvFileName.format(csvFolder, ticker)
    return HqCsv(ticker, csvFile)


@app.route('/')
def index():
    return render_template('index.html',
                           title='HQ',
                           day=day,
                           hqUrl=hqConf['hqUrl'],
                           hqMetaFiles=getHqMetaFiles(),
                           tickers=hqConf['tickers'])

@app.route('/hqMeta')
def hqMeta():
    hqMetaFile = request.args.get('hqMetaFile')
    hqMetas = json.load(open(hqMetaFile))
    return render_template('hqMeta.html',
                           title='HQ',
                           day=day,
                           hqUrl=hqConf['hqUrl'],
                           hqMetaFiles=getHqMetaFiles(),
                           hqMetas=hqMetas,
                           upAlert=0.1,
                           downAlert=-0.1,
                           round=round)

@app.route('/hqCsv')
def hqCsv():
    ticker = request.args.get('ticker')
    return render_template('hqCsv.html',
                           title='HQ',
                           day=day,
                           hqUrl=hqConf['hqUrl'],
                           hqMetaFiles=getHqMetaFiles(),
                           hqCsv=getHqCsv(hqConf, ticker, day),
                           upAlert=0.05,
                           downAlert=-0.1,
                           round=round)

@app.route('/hqrobot')
def hqrobot():
    day = (datetime.now() + timedelta(days=dayDelta)).strftime("%Y%m%d")
    hqConf = json.load(open(HQ_CONF))
    hqrobotMain(hqConf, day)
    return redirect('/hqMeta/dayIdx?startDayIdx=0')

@app.route('/hqMeta/dayIdx')
def hqMetaStartDayIdx():
    startDayIdx = int(request.args.get('startDayIdx'))
    return render_template('hqMeta.html',
                           title='HQ',
                           day=day,
                           hqUrl=hqConf['hqUrl'],
                           hqMetaFiles=getHqMetaFiles(),
                           hqMetas=getHqMetas(hqConf, day, startDayIdx),
                           upAlert=0.1,
                           downAlert=-0.1,
                           round=round)
