FROM phusion/baseimage:0.9.17
MAINTAINER Grow SDK Authors <hello@grow.io>

# Default command to run when this container is run (use baseimage-docker's init process).
# DO NOT CHANGE. See: http://phusion.github.io/baseimage-docker/
CMD ["/sbin/my_init"]

# Create the "app" user for running services.
RUN addgroup --gid 9999 app
RUN adduser --uid 9999 --gid 9999 --disabled-password --gecos "Application" app
RUN usermod -L app
RUN mkdir -p /home/app/.ssh
RUN chmod 700 /home/app/.ssh
RUN chown app:app /home/app/.ssh

# Update system.
RUN apt-get update
RUN apt-get upgrade -y

# Set environment variables.
ENV TERM=xterm

# Install system utils and dependencies.
RUN apt-get install -y --no-install-recommends git curl htop

# Install docker inside docker. This requires that this container is run in --privileged mode.
RUN curl -sSL https://get.docker.com/ | sh
# RUN chmod +x /etc/my_init.d/start-logger.sh

# Let the "app" user run docker commands.
RUN usermod -aG docker app

# Add all the boot scripts.
ADD boot-scripts/* /etc/my_init.d/
RUN chmod +x /etc/my_init.d/*

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
