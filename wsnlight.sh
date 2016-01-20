#!/bin/bash

while [ ! "$(ps -ejH | grep olad)" ]; do
    sleep 1
done
sleep 3     # ensure olad is really started

echo "Starting WSN light..."
./wsnlight.py

exit $?


