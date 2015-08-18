#!/bin/bash -e

if [ -a "package.json" ]; then
  npm install
fi
if [ -a "bower.json" ]; then
  bower install
fi
if [ -a "gulpfile.js" ]; then
  gulp build
fi

/usr/bin/grow deploy -f review
