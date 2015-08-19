#!/usr/bin/env python

import os
from apiclient.discovery import build
from apiclient import errors

PROJECT_NAME = os.getenv('PROJECT_NAME')
TASK_QUEUE_NAME = os.getenv('QUEUE_NAME')
TASK_LEASE_SECONDS = os.getenv('TASK_LEASE_SECONDS', 300)
TASK_BATCH_SIZE = os.getenv('TASK_BATCH_SIZE', 10)
assert PROJECT_NAME
assert TASK_QUEUE_NAME

def main():
  task_api = build('taskqueue', 'v1beta2')

  try:
    lease_request = task_api.tasks().lease(
        project=PROJECT_NAME,
        taskqueue=TASK_QUEUE_NAME,
        leaseSecs=TASK_LEASE_SECONDS,
        numTasks=TASK_BATCH_SIZE,
        # body={},
    )
    result = lease_request.execute()
    print '------------'
    print repr(result)
    return result
  except errors.HttpError, e:
    logger.error('Error during lease request: %s' % str(e))
    return None


if __name__ == '__main__':
  main()