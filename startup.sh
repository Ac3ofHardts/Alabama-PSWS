#!/bin/bash

#handler()
#{
#	echo 'Handling'
#	echo $PSWS_PID
#	kill -s SIGINT $PSWS_PID
#	kill -s SIGINT $watch_PID
#}

set -e
source /var/www/Alabama-PSWS/venv/bin/activate


PSWS/manage.py runserver 0:8080 &
PSWS_PID=$!
echo $!
python3 crobbins_watch.py /home &
watch_PID=$!
echo $!

read var
echo 'Killing after read'
kill $PSWS_PID
kill $watch_PID

trap handler SIGINT
#trap 'kill $(jobs -pr)' SIGINT SIGTERM EXIT
