#!/bin/sh
HOST=localhost
PORT=30003
INTERVAL=hour
OUTPUT_PREFIX=data/dump1090-messages/dump1090-$(hostname)
LOG_FILE=dump1090-logrotate.log
# replace the shell's process
# store stdout & stderr to a log file
# buffer the python's output
exec /home/pi/miniconda3/bin/python3 -u dump1090-archive/dump1090_logrotate/dump1090_logrotate.py \
  -h $HOST \
  -p $PORT \
  -i $INTERVAL \
  -o ${OUTPUT_PREFIX} \
  2>&1 >> ${LOG_FILE}
