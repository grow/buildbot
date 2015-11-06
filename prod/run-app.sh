#!/bin/bash

# Init gerrit credentials once on load.
# TODO(fotinakis): kill this because it's insecure in the long run, do per-job auth credentials.
/sbin/setuser app bash /home/app/gerrit-auth.sh

# Run the process as the "app" user and redirect stdout/stderr to syslog.
cd /home/app
/sbin/setuser app twistd -n web --port 8000 --wsgi main.app 2>&1 | logger -p user.info
