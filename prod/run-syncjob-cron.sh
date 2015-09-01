#!/bin/bash

# Run the process as the "app" user and redirect stdout/stderr to syslog.
/sbin/setuser app /home/app/cron.py 2>&1 | logger -p user.info
