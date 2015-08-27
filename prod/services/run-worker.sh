#!/bin/bash

# Make sure the docker socket is readable by the app user.
chmod 666 /var/run/docker.sock

# Run the process as the "app" user and redirect stdout/stderr to syslog.
/sbin/setuser app /home/app/worker.py 2>&1 | logger -p user.info
