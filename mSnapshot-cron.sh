#!/bin/bash
export WORKON_HOME=/home/pi/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
workon cv

touch /home/pi/jb/tmp/run-mSnapshot-cron
python /home/pi/jb/pipy/motion-detect-recorder/mSnapshot.py /home/pi/jb/json/mdr-mdArea.json

