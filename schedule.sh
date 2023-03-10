# This bash script adds to crontab a task to run a python script 1 to 4 times a day.
# It can also remove the task to run a python script from crontab.
# Note: Run this bash script in the right python virtual env required to run the script.
# A log file [cron.log] is added in the same directory.

# This script can be run as 
# bash schedule.sh
# or
# chmod +x schedule.sh; ./schedule.sh

#---------------------
username=$USER
currentdir=$(pwd)
pythonpath=$(which python)

# If command which python return is empty, python3 should be used instead.
if [ -z "$pythonpath" ]
    then pythonpath=$(which python3)
fi

# Ask the user to choose betweeing to adding/modifying a task, or deleting a task from crontab. 
echo "What do you want to do? 
1. Schedule/Reschedule running a python script at specific times every day, or
2. Stop the automatic running a particular python script.
Enter the number corresponding to desired option (1 or 2): "
read op

# Confirm the user's choice
case $op in
1) echo "Scheduling the run of script / modifying an existing schedule ...";;
2) echo "Removing a scheduled run ...";;
*) echo "Error: entered value is not 1 or 2."
exit 1;;
esac

# Ask user to input the path to python script
echo "Enter the path to the python script:"
read script

# If path is relative change it to an absolute path.
if [[ "$script" != /* ]]
    then script=${currentdir}/${script}
fi

# Raise error if path does not exist.
if [ ! -e $script ]
    then echo "$script does not exists!"
    exit 1
fi

# Define the cron command to be added/modified/deleted.
croncmd="$pythonpath ${script} >> ${currentdir}/cron.log"

# Delete task from crontab
if [ $op -eq 2 ]
    then
        ( crontab -l | grep -v -F "$croncmd" ) | crontab -
        echo "Successfuly removed!"
        exit 0
fi

# Ask user to choose a schedule
echo "How many times a day should the script run? Enter a number between 1-4
    1. script will run once, at 00:00
    2. script will run twice, at 00:00 and 12:00
    3. script will run 3 times, at 00:00, 08:00 and 16:00
    4. script will run 4 times, at 00:00, 06:00, 12:00 and 18:00"
read freq

# Define the full cron job to be added     
case $freq in
1) cronjob="0 */24 * * * $croncmd";;
2) cronjob="0 */12 * * * $croncmd";;
3) cronjob="0 */8 * * * $croncmd";;
4) cronjob="0 */6 * * * $croncmd";;
*) echo "Error: entered value is not a number between 1-4."
exit 1;;
esac 

# Add the task to the crontab, with no duplication       
crontab -l | fgrep -i -v "$croncmd" | { cat; echo "$cronjob"; } | crontab -
echo "Successfuly added!"