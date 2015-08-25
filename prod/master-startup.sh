#!/bin/bash

# This is the startup script for the buildbot-master host GCE instance, not the docker containers.

### TODO: add sed for /etc/default/kubelet to add --allow_privileged=true.

# Mount the buildbot-data disk at /data if it is not already mounted.
/usr/share/google/safe_format_and_mount -m "mkfs.ext4 -F" /dev/disk/by-id/google-buildbot-data /data
