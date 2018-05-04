import json
import os
import pandas as pd
from datetime import datetime

JsonFile = "{}/hqMeta{}.json"
class HqMetaFile:

    def __init__(self, hqConf, day):
        self.hqConf = hqConf
        self.day = day

    def writeJson(self, hqMeta):
        hqMetaFile = JsonFile.format(self.hqConf['repo'], self.day)
        # print(hqMetaFile)
        with open(hqMetaFile, 'w') as outfile:
            json.dump(hqMeta, outfile)

    def readJson(self):
        hqMetaFile = JsonFile.format(self.hqConf['repo'], self.day)
        hqMetas = json.load(open(hqMetaFile))
        for hqMeta in hqMetas:
            print(hqMeta)
        return hqMetas

    def toCsv(self):
        hqMetaFile = JsonFile.format(self.hqConf['repo'], self.day)
        return pd.read_json(hqMetaFile)
