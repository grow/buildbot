# Dockerfile extending the generic Python image with application files for a
# single application.
FROM gcr.io/google_appengine/python-compat
MAINTAINER Grow SDK Authors <hello@grow.io>

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends git

ADD . /app
