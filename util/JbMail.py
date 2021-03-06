import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
# from email.MIMEText import MIMEText   # python 2
from email.mime.text import MIMEText    # python 3
from email.mime.base import MIMEBase
from email import encoders

import re
import json
def var2Json(var):
    jsonstr = json.dumps(var)
    print(jsonstr)
    jsonstr = jsonstr.replace('{"', '{').replace('":', ':')
    jsonstr = re.sub(r'[,][ ]["]([a-z\-A-Z]*)[:]', r', \1:', jsonstr)
    return jsonstr

class JbMail:
    def __init__(self, mdrConf):
        self.mdrConf = mdrConf
        mailConf = mdrConf['email']
        msg = MIMEMultipart()
        msg['From'] = mailConf['from']
        msg['Subject'] = mailConf['subject']
        COMMASPACE = ', '
        msg['To'] = COMMASPACE.join(mailConf['to'])
        msg.attach(MIMEText(mailConf['body'], 'plain'))
        # msg.attach(MIMEText(html, 'html'))
        self.mdrMail = msg

    def send(self):
        smtpConf = self.mdrConf['email']
        smtp = smtplib.SMTP(smtpConf['smtp-server'])
        smtp.sendmail(smtpConf['from'], smtpConf['to'], self.mdrMail.as_string())
        smtp.quit()
        
    def send_ssl(self):
        smtpConf = self.mdrConf['email']
        host = smtpConf['smtp-server']
        port = smtpConf['smtp-port']
        log = smtpConf['log']
        sender = smtpConf['from']
        try:
            smtp = smtplib.SMTP_SSL(host, port)
            smtp.login(sender, log)
            smtp.sendmail(smtpConf['from'], smtpConf['to'], self.mdrMail.as_string())
            print('send_ssl ok')
        except Exception as e:
            print(e) 


    def attachImage(self, imgFile):
        fp = open(imgFile, 'rb')
        img = MIMEImage(fp.read(), name=os.path.basename(imgFile))
        fp.close()
        self.mdrMail.attach(img)

    def attachImages(self, imgFiles):
        for file in imgFiles:
            self.attachImage(file)


def test():
    import json
    conf = json.load(open('../mdr.json'))
    mdrMail = JbMail(conf)
    imgFiles = ['../../../../camCache/img001.jpg']
    mdrMail.attachImage(imgFiles[0])
    mdrMail.attachImages(imgFiles)
    mdrMail.send()


if __name__ == "__main__":
    test()
