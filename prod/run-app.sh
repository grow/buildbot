#!/bin/bash

# Run the process as the "app" user and redirect stdout/stderr to syslog.
cd /home/app
/sbin/setuser app twistd -n web --port 8080 --wsgi main.app 2>&1 | logger -p user.info
