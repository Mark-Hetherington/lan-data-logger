#!/usr/bin/env python

import logging
import logging.handlers
import argparse
import os
import json
import cgi
#from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import datetime
import config

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="Data Logger")
parser.add_argument("-c", "--config", help="config file path (optional)")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.config:
        config.CONF_FILENAME = args.config

def read_configs(CONF_FILE):
        '''Try to read configuration from a set of files'''
        paths = [CONF_FILE, os.path.expanduser('~/.datalogger.conf'), '/etc/datalogger.conf']
        for path in paths:
            content = None
            try:
                f = open(path, 'r')
                content = f.read()
            except:
                pass
            if content:
                loaded_config = json.loads(content)
                f.close()
                return loaded_config

        return None

config.settings = read_configs(config.CONF_FILENAME)

if config.settings is None: raise ValueError('No configuration found.')

from processors.CurrentCostProcessor import CurrentCostProcessor
import sys
import urlparse




# Deafults
LOG_FILENAME = "/var/log/data-logger/collector.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"


if 'log' in config.settings and config.settings['log']:
    LOG_FILENAME = config.settings['log']

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)


class MyHandler(BaseHTTPRequestHandler):
    _processors = [CurrentCostProcessor]


    def do_GET(self):
        #try:
            # url = self.path
            if self.command == 'GET':
                o = urlparse.urlparse(self.path)
                query = urlparse.parse_qs(o.query)
            elif self.command == 'POST':
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    query = cgi.parse_multipart(self.rfile, pdict)
                elif ctype == 'application/x-www-form-urlencoded':
                    length = int(self.headers.getheader('content-length'))
                    query = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)

            data = {
                "data": query['data'][0],
                "time": query['timestamp'] if 'timestamp' in query else datetime.datetime.utcnow(),
                #A device without an RTC may still know how long ago data was collected even if it doesn't know the time.
                "offset": query['offset'] if 'offset' in query else 0
            }

            for processor in self._processors:
                the_processor = processor(data)
                if the_processor.handles_format():
                    try:
                        # TODO: Are processors going to output any data?
                        the_processor.process()

                        # TODO: Is there any point writing a success code?
                        self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write('OK')

                        return
                    except:
                        exc_info = sys.exc_info()
                        logger.error("Data parsing error:", exc_info[0], exc_info[1])
                        # move on to next processor.
                        pass

            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write('Queued')

            return

        #except:
        #    exc_info = sys.exc_info()
        #    self.send_error(500,'Internal Server Error: %s' % exc_info[0])




    def do_POST(self):
        self.do_GET()

    def log_message(self, format, *args):
        """Log an arbitrary message.

        This is used by all other logging functions.  Override
        it if you have specific logging wishes.

        The first argument, FORMAT, is a format string for the
        message to be logged.  If the format string contains
        any % escapes requiring parameters, they should be
        specified as subsequent arguments (it's just like
        printf!).

        The client ip address and current date/time are prefixed to every
        message.

        """

        logger.info("%s - - [%s] %s\n" %
                         (self.client_address[0],
                          self.log_date_time_string(),
                          format%args))
# Loop forever, doing something useful hopefully:
#while True:


try:
    server = HTTPServer((config.settings['ip_address'], config.settings['port']), MyHandler)
    print 'started httpserver...'
    # This blocks until a keyboard interrupt... That can't happen when daemonised. We need to create some threads
    # and figure out how to clean ourselves up...
    server.serve_forever()
except KeyboardInterrupt:
    print '^C received, shutting down server'
    server.socket.close()

