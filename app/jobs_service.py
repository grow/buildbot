import os
import json
import redis
import subprocess
import time

MAX_RETAINED_BUILDS = 100

redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0))
)


class Error(Exception):
    pass


class NotFoundError(Error):
    pass


class GitFailure(Error):
    pass


class Job(object):
    pass


class Build(object):
    pass


def create_job(git_url):
    job_id = redis_client.incr('jobs:counter')
    redis_client.hset('job:%s:data' % job_id, 'git_url', git_url)
    redis_client.lpush('jobs:all', job_id)
    try:
        update_ref_map(job_id)
    except GitFailure:
        # Ignore git failures so that the job can be created successfully and fail harder later.
        pass
    return job_id


def list_jobs():
    jobs = []
    job_ids = redis_client.lrange('jobs:all', 0, -1)
    for job_id in job_ids:
        try:
            jobs.append(get_job(job_id))
        except NotFoundError:
            pass
    return jobs


def get_job(job_id):
    job_data_key = 'job:%s:data' % job_id
    if not redis_client.hget(job_data_key, 'git_url'):
        raise NotFoundError(job_id)

    job = Job()
    job.id = job_id
    job.git_url = redis_client.hget(job_data_key, 'git_url')
    job.ref_map = json.loads(redis_client.hget(job_data_key, 'ref_map') or '{}')
    return job


def run_job(job_id):
    success = True
    diff_ref_map = update_ref_map(job_id)
    build_ids = []
    if diff_ref_map:
        for ref in diff_ref_map:
            build_id = enqueue_build(job_id=job_id, ref=ref, commit_sha=diff_ref_map[ref]['sha'])
            build_ids.append(build_id)
    return build_ids


def update_ref_map(job_id):
    job = get_job(job_id)
    new_ref_map = get_ref_map(job.git_url)
    old_ref_map = job.ref_map
    diff_ref_map = ref_map_diff(old_ref_map, new_ref_map)

    # Update the job's ref map.
    redis_client.hset('job:%s:data' % job_id, 'ref_map', json.dumps(new_ref_map))

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


def enqueue_build(job_id, ref, commit_sha):
    job = get_job(job_id)
    build_id = redis_client.incr('build:counter')
    build_data_key = 'build:%s:data' % build_id

    # Set all the build data into a build:123:data key which can be consumed later.
    redis_client.hset(build_data_key, 'status', 'pending')
    redis_client.hset(build_data_key, 'git_url', job.git_url)
    redis_client.hset(build_data_key, 'ref', ref)
    redis_client.hset(build_data_key, 'commit_sha', commit_sha)

    # Push the build ID into builds:runnable so it can be consumed by a worker.
    redis_client.lpush('builds:runnable', build_id)

    # Cleanup old builds that have exceeded MAX_RETAINED_BUILDS.
    builds_to_delete = redis_client.lrange('builds:recent', MAX_RETAINED_BUILDS, -1)
    redis_client.ltrim('builds:recent', 0, MAX_RETAINED_BUILDS)
    for build_id in builds_to_delete:
        redis_client.delete(*['build:%s:data' % build_id for build_id in builds_to_delete])

    return build_id


def pop_next_build():
    build_id = redis_client.rpoplpush('builds:runnable', 'builds:recent')
    if not build_id:
        return
    return get_build(build_id)


def run_build(build_id):
    build = get_build(build_id)

    build_data_key = 'build:%s:data' % build_id
    redis_client.hset(build_data_key, 'status', 'running')

    success = True
    try:
        command = [
            'docker',
            'run',
            '--rm',
            '--workdir=/tmp',
            '-i',
            'grow/baseimage',
            'bash',
            '-c',
            """
            git clone %s growdata && grow build growdata
            """ % build.git_url
        ]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        redis_client.hset(build_data_key, 'status', 'success')

        # TODO: probably better to store the output outside redis because it is potentially large.
        redis_client.hset(build_data_key, 'output', output)
    except subprocess.CalledProcessError, e:
        success = False
        redis_client.hset(build_data_key, 'status', 'failed')
        output = 'Build failed: %s' % e.output
    except:
        redis_client.hset(build_data_key, 'status', 'failed')
        raise
    return success


def list_builds():
    builds = []
    build_ids = redis_client.lrange('builds:runnable', 0, -1)
    build_ids += redis_client.lrange('builds:recent', 0, -1)
    for build_id in build_ids:
        try:
            builds.append(get_build(build_id))
        except NotFoundError:
            # Cleanup bad IDs if they existed in the list but the data has been deleted.
            redis_client.lrem('builds:runnable', 0, build_id)
            redis_client.lrem('builds:recent', 0, build_id)
    return builds


def get_build(build_id):
    build_data_key = 'build:%s:data' % build_id
    if not redis_client.hget(build_data_key, 'status'):
        raise NotFoundError(build_id)

    build = Build()
    build.id = build_id
    build.status = redis_client.hget(build_data_key, 'status')
    build.git_url = redis_client.hget(build_data_key, 'git_url')
    build.ref = redis_client.hget(build_data_key, 'ref')
    build.commit_sha = redis_client.hget(build_data_key, 'commit_sha')
    return build
