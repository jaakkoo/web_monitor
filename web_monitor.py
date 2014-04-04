__author__ = 'Jaakko Aro'

import sys
import os
import ConfigParser
import threading
import logging
import time
from monitor_app import MonitoredPage
from monitor_app import NoResponse
from logging import config
from web_server import run_server
from optparse import OptionParser


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'wm_format': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'wm_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*2,  # 2MB
            'backupCount': 1,
            'filename': 'web_monitor.log',
            'formatter': 'wm_format'
        }
    },
    'loggers': {
        'web_monitor': {
            'handlers': ['wm_handler'],
            'level': 'INFO',
        }
    }
}

config.dictConfig(LOGGING)
logger = logging.getLogger('web_monitor')


class InitializationException(Exception):
    pass


def get_options():
    usage = 'usage: %prog [opts]'
    parser = OptionParser(usage=usage)
    parser.add_option('-f', '--frequency', dest='frequency', default='60', type='float',
                      help='Polling frequency in seconds. How often the application refreshes the status of configured '
                           'websites. Default is every 60 seconds.')
    parser.add_option('-w', '--web-server', action='store_true', dest='web_server', default=False,
                      help='Launch web server to monitor status using browser. Will be running in port 8080.')
    parser.add_option('-c', '--config', dest='config_file', default='conf/default.cfg',
                      help='Path to config file. If not given, default path will be used.')
    options, args = parser.parse_args()
    return options


def get_config(config_file_path):
    parser = ConfigParser.SafeConfigParser()
    try:
        parser.read(config_file_path)
        return parser
    except IOError:
        raise InitializationException('Config file %s not found.' % config_file_path)
    except ConfigParser.Error:
        raise InitializationException('Config file %s not formed correctly.' % config_file_path)


def launch_web_server(monitored_pages):
    t = threading.Thread(target=run_server, args=[monitored_pages])
    t.daemon = True
    t.start()


def monitor_page(monitored_page, frequency):
    t = threading.Timer(frequency, monitor_page, args=[monitored_page, frequency])
    t.daemon = True
    t.start()
    monitored_page.refresh_status()
    return t


def main(options, config):
    monitored_pages = list()
    page_monitors = list()
    if options.web_server:
        launch_web_server(monitored_pages)

    for section in config.sections():
        page = MonitoredPage(section,
                             config.get(section, 'url'),
                             float(config.get(section, 'maximum_response_time')),
                             config.get(section, 'should_contain'))
        monitored_pages.append(page)
        page_monitors.append(monitor_page(page, float(options.frequency)))

    try:
        while True:
            for page in monitored_pages:
                try:
                    printable_status = str(page)
                    if page.get_status():
                        logger.info(printable_status)
                    else:
                        logger.warning(printable_status)
                except NoResponse:
                    logger.error(printable_status)
            time.sleep(options.frequency)
    except KeyboardInterrupt:
        logger.info('Ctrl-C caught, exiting.')
        map(lambda x: x.cancel(), page_monitors)
        map(lambda x: x.join(), page_monitors)
        return 0

if __name__ == '__main__':
    try:
        options = get_options()
        config = get_config(options.config_file)
    except InitializationException, e:
        print 'Launching the application failed with following error: "%s"' % str(e)
        sys.exit(1)
    print 'CTRL-C to exit'
    print 'Logfile at %s' % os.path.join(os.getcwd(), 'web_monitor.log')
    sys.exit(main(options, config))
