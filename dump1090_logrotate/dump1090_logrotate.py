"""
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
"""

import argparse
import arrow
import gzip
import os
import signal
import socket

def dump1090_socket(hostname='localhost', port=30003):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((hostname, int(port)))
        for line in sock.makefile():
            yield line

# http://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
# by Mayank Jaiswal
class GracefulKiller:
    """Prevents losing data when killed by SIGTERM"""
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

class FileRotator():
    def __init__(self, file_prefix='dump1090', interval='hour', compression='gzip'):
        self.file_pattern = file_prefix + '-{}.csv'
        if compression == 'gzip':
            self.file_pattern += '.gz'
        # interval name as in arrow ('second', 'minute', 'hour', 'day', ...)
        self.interval = interval
        self.compression = compression

        self.date_format = 'YYYY-MM-DD-HH-mm-ss'
        self.output_file = None
        self.next_log_time = arrow.get(0)

    def write(self, line):
        if self.compression == 'gzip':
            data = line.encode('utf-8')
        else:
            data = line
        self.current_file().write(data)

    def current_file(self):
        if arrow.utcnow() >= self.next_log_time:
            self.rotate_file()
        return self.output_file

    def update_log_time(self):
        now = arrow.utcnow()
        self.current_log_time = now.floor(self.interval)
        self.next_log_time = now.ceil(self.interval)

    def rotate_file(self):
        self.close()
        self.update_log_time()
        # Timestamp at the end is to prevent overwriting files in case we
        # restart the process. New run will go to another file.
        date_part = (self.current_log_time.format(self.date_format) +
            '-' + arrow.utcnow.format('X'))
        file_name = self.file_pattern.format(date_part)
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        print('writing to:', file_name)
        if self.compression == 'gzip':
            self.output_file = gzip.open(file_name, 'wb')
        else:
            self.output_file = open(file_name, 'w')

    def close(self):
        if self.output_file:
            self.output_file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

dump1090_host = os.getenv('DUMP1090_HOST', 'localhost')
# BaseStation CSV format
dump1090_port = os.getenv('DUMP1090_PORT', '30003')

def main(host, port, output_prefix, interval):
    killer = GracefulKiller()
    with FileRotator(output_prefix, interval) as output_file:
        for line in dump1090_socket(host, port):
            output_file.write(line)
            if killer.kill_now:
                break

def parse_args():
    parser = argparse.ArgumentParser(description='Stores dump1090 CSV outputs to rotated and compressed files.',
        add_help=False)
    parser.add_argument('--help', action='help',
        help='show this help message and exit')
    parser.add_argument('-h', '--host', type=str, default='localhost',
        help='dump1090 hostname')
    parser.add_argument('-p', '--port', type=str, default='30003',
        help='dump1090 port')
    parser.add_argument('-o', '--output', type=str,
        default='dump1090', help='output file prefix')
    parser.add_argument('-i', '--interval', type=str,
        choices=['second', 'minute', 'hour', 'day'], default='hour',
        help='file rotation interval')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args.host, args.port, args.output, args.interval)
