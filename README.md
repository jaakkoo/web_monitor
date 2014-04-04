Web Monitor
===========
Web Monitor for monitoring web pages.

## Installation
I suggest using virtual environments so that the application dependencies don't get installed system wide:
Create Virtual Environment:
virtualenv --no-site-packages web_monitor

### To Activate
source web_monitor/bin/activate

## Install dependencies
pip install -r requirements.txt

## Usage: web_monitor.py [opts]
```
Options:
  -h, --help            show this help message and exit
  -f FREQUENCY, --frequency=FREQUENCY
                        Polling frequency in seconds. How often the
                        application refreshes the status of configured
                        websites. Default is every 60 seconds.
  -w, --web-server      Launch web server to monitor status using browser.
                        Will be running in port 8080.
  -c CONFIG_FILE, --config=CONFIG_FILE
                        Path to config file. If not given, default path will
                        be used.
```

Run unittests:
Type "nosetests" (in the folder where web monitor was unpacked)

Configuring new sites:
Example configuration is located in <web_monitor_root>/conf/default.cfg

Web Server:
Web UI can be accessed with browser from localhost:8080.
