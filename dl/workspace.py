"""
Workspace structure

garage/
garage/apply
garage/apply/close
garage/apply/open
garage/learn
garage/learn/close
garage/learn/open
garage/savedModels
"""
import os

# my repository
Pirepo = "/pirepo/"

class Workspace:
    def __init__(self, name):
        self.rootPath = Pirepo + name
        if not os.path.exists(self.rootPath):
            os.makedirs(self.rootPath)


    def modelStore(self, modelName):
        folder = self.rootPath + '/savedModels/' + modelName
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder + '/' + modelName + '_model'

if __name__ == "__main__":
    ws = Workspace('garage')
    print(ws.modelStore('mnst'))
