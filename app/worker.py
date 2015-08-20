#!/usr/bin/env python

import os
import logging
from apiclient.discovery import build
from apiclient import errors

PROJECT_NAME = os.getenv('PROJECT_NAME')
TASKQUEUE_NAME = os.getenv('TASKQUEUE_NAME', 'builds')
TASKQUEUE_LEASE_SECONDS = os.getenv('TASKQUEUE_LEASE_SECONDS', 300)
TASKQUEUE_BATCH_SIZE = os.getenv('TASKQUEUE_BATCH_SIZE', 10)
assert PROJECT_NAME
assert TASKQUEUE_NAME

def main():
  task_api = build('taskqueue', 'v1beta2')

  try:
    lease_request = task_api.tasks().lease(
        project=PROJECT_NAME,
        taskqueue=TASKQUEUE_NAME,
        leaseSecs=TASKQUEUE_LEASE_SECONDS,
        numTasks=TASKQUEUE_BATCH_SIZE,
        # body={},
    )
    result = lease_request.execute()
    print '------------'
    print repr(result)
    return result
  except errors.HttpError, e:
    logging.error('Error during lease request: %s' % str(e))
    return None


if __name__ == '__main__':
  main()