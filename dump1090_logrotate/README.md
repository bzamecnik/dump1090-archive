# dump1090-logrotate

This module reads ADS-B messages from dump1090 over the 30003 port and stores
them to compressed CSV files which are partitioned by time (eg. hours).

Usage:

$ python dump1090_logrotate.py -h localhost -p 30003 -o logs/dump1090 -i hour

Stores files file like:
logs/dump1090-2016-10-03-17-00-00-1475514000.csv.gz
logs/dump1090-2016-10-03-18-00-00-1475517600.csv.gz
...

While killed via SIGTERM (CTRL-C or the kill command) it gracefully closes the
output files and tries to prevent data loss.

After a restart the file from the same date partition is not overwritten but
a different suffix is added to prevent such collision.

A systemd init script (suitable for Rasbian) is provided.

## Installing on Rasbian

- assuming home directory `/home/pi`
- install Miniconda with Python 3 to `~/miniconda3`

```
cd
git clone https://github.com/bzamecnik/dump1090-archive.git
sudo cp dump1090-archive/dump1090_logrotate/systemd/dump1090-logrotate.service \
  /lib/systemd/system/dump1090-logrotate.service
sudo systemctl daemon-reload
sudo systemctl start dump1090-logrotate.service

# other commands:

sudo systemctl status dump1090-logrotate.service
sudo systemctl restart dump1090-logrotate.service
sudo systemctl stop dump1090-logrotate.service
```

- data will be collected to `~/data/dump1090-messages/`
- log file: `dump1090-logrotate.log`
