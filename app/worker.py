#!/usr/bin/env python

import time
import jobs_service


def main():
    print 'Waiting for builds...'
    while True:
        build = jobs_service.pop_next_build()
        if not build:
            time.sleep(2)
            continue
        print 'Running build: %s %s %s %s' % (build.id, build.git_url, build.ref, build.commit_sha)
        result = jobs_service.run_build(build.id)
        print 'Build %s: %s' % (build.id, 'success' if result else 'failed')

if __name__ == '__main__':
    main()
