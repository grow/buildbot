import os
import json
import redis
import subprocess
import time


redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0))
)


class Error(Exception):
    pass


class JobNotFoundError(Error):
    pass


class GitFailure(Error):
    pass


class Job(object):
    pass


def create_job(git_url):
    job_id = redis_client.incr('jobs:counter')
    redis_client.set('job:%s:git_url' % job_id, git_url)
    redis_client.zadd('jobs:all', time.time(), job_id)
    try:
        update_ref_map(job_id)
    except GitFailure:
        # Ignore git failures so that the job can be created successfully and fail harder later.
        pass
    return job_id


def list_jobs():
    jobs = []
    job_ids = redis_client.zrangebyscore('jobs:all', '-inf', '+inf')
    for job_id in job_ids:
        try:
            jobs.append(get_job(job_id))
        except JobNotFoundError:
            pass
    return jobs


def get_job(job_id):
    score = redis_client.zscore('jobs:all', job_id)
    if not score:
        raise JobNotFoundError(job_id)

    job = Job()
    job.id = job_id
    job.git_url = redis_client.get('job:%s:git_url' % job_id)
    job.ref_map = json.loads(redis_client.get('job:%s:ref_map' % job_id) or '{}')
    return job


def run_builds(job_id):
    success = True
    diff_ref_map = update_ref_map(job_id)
    if not diff_ref_map:
        output = 'No refs changed, nothing new to build.'
    else:
        output = ''
        pass
    return {'success': success, 'output': output}


def run_build(job_id, ref, commit_sha):
    pass


def update_ref_map(job_id):
    job = get_job(job_id)
    new_ref_map = get_ref_map(job.git_url)
    old_ref_map = job.ref_map
    diff_ref_map = ref_map_diff(old_ref_map, new_ref_map)

    # Update the job's ref map.
    redis_client.set('job:%s:ref_map' % job_id, json.dumps(new_ref_map))

    return diff_ref_map


def get_ref_map(git_url):
    try:
        command = ['git', 'ls-remote', '--heads', git_url]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)

        ref_map = {}
        for line in output.splitlines():
            commit_sha, ref = line.split()
            ref_map[ref] = {'sha': commit_sha}
    except subprocess.CalledProcessError, e:
        raise GitFailure(e.output)
    return ref_map


def ref_map_diff(old_ref_map, new_ref_map):
    diff_ref_map = {}
    for ref in new_ref_map:
        # Add refs if the SHA has changed.
        if ref in old_ref_map and new_ref_map[ref]['sha'] != old_ref_map[ref]['sha']:
            diff_ref_map[ref] = new_ref_map[ref]
        # Add new refs we haven't seen before.
        if ref not in old_ref_map:
            diff_ref_map[ref] = new_ref_map[ref]
    return diff_ref_map
