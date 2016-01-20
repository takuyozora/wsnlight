#!/bin/bash

while [ -e /tmp/wsnlight.lock ]; do
    sleep 1     # unable to run vicking when lock (for test)
done

while [ ! "$(ps -ejH | grep olad)" ]; do
    sleep 1
done
sleep 3     # ensure olad is really started

echo "Starting WSN light..."
touch /tmp/wsnlight.lock
./wsnlight.py
rm /tmp/wsnlight.lock

exit $?


