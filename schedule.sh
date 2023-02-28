#!/usr/bin/bash

# This bash script adds to crontab a task to run a python script[$1] twice a day [at 00:00 and 12:00].
# The python script [$1] has to be in the same dir as this bash script, and run the write python virtual env.
# A log file [cron.log] is added in the same directory.
# should be run once as 
# bash schedule.sh python_script.py

# add a way to remove the job
# add a way to change the schedule of the job

username=$USER
currentdir=$(pwd)
pythonpath=$(which python)
script=$1

croncmd="$pythonpath ${currentdir}/${script} >> ${currentdir}/cron.log"
cronjob="0 0,12 * * * $croncmd"

# add the task to the crontab, with no duplication:
#crontab -l | fgrep -i -v "$croncmd" | { cat; echo "$cronjob"; } | crontab -


# to remove the task from the crontab whatever its current schedule:
#( crontab -l | grep -v -F "$croncmd" ) | crontab -