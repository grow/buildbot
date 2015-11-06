#!/bin/sh

# Note: it is important that nginx is configured to not daemonize itself for this init script to
# work correctly. See: https://github.com/phusion/baseimage-docker#adding-additional-daemons
exec nginx -g 'daemon off;'
