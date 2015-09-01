#!/usr/bin/env python

import time
import jobs_service

def main():
  # Run continuously for 60 seconds, with a 10 second backoff after each run.
  start = time.time()
  while time.time() - start < 60:
    print 'Syncing all jobs...'
    jobs_service.sync_all_jobs()
    print 'Success, going to sleep...'
    time.sleep(10)


if __name__ == '__main__':
  main()
