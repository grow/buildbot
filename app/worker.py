#!/usr/bin/env python

import time
import os
import signal
import jobs_service

heard_interrupt = False


def main():
  print 'Waiting for builds...'
  while not heard_interrupt:
    build = jobs_service.pop_next_build()
    if not build:
      time.sleep(2)
      continue
    print 'Running build: %s %s %s %s' % (build.id, build.git_url, build.ref, build.commit_sha)
    result = jobs_service.run_build(build.id)
    print 'Build %s: %s' % (build.id, 'success' if result else 'failed')


def sigint_handler(_, frame):
  print 'Shutting down (interrupt again to kill)...'
  global heard_interrupt
  if heard_interrupt:
    os.kill(os.getpid(), signal.SIGTERM)
  heard_interrupt = True
signal.signal(signal.SIGINT, sigint_handler)

if __name__ == '__main__':
  main()
