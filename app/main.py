#!/usr/bin/env python

import flask
import jobs_service
from flask import request

app = flask.Flask(__name__)


@app.route('/')
def index():
  jobs = jobs_service.list_jobs()
  builds = jobs_service.list_builds(limit=20)
  return flask.render_template('index.html', builds=builds, jobs=jobs)


@app.route('/builds')
def builds():
  builds = jobs_service.list_builds()
  return flask.render_template('builds.html', builds=builds)


@app.route('/jobs')
def jobs():
  jobs = jobs_service.list_jobs()
  return flask.render_template('jobs.html', jobs=jobs)


@app.route('/builds/<int:build_id>')
def build(build_id):
  build = jobs_service.get_build(build_id)
  return flask.render_template('build.html', build=build)

# API.

@app.route('/api/jobs', methods=['POST'])
def create_job():
  git_url = request.args.get('git_url')
  assert git_url
  job_id = jobs_service.create_job(git_url=git_url)
  return flask.jsonify({'success': True, 'job_id': job_id})


@app.route('/api/jobs/<int:job_id>/run', methods=['GET', 'POST'])
def run_job(job_id):
  ref = request.args.get('ref')
  commit_sha = request.args.get('commit_sha')
  if ref and commit_sha:
    # Trigger build of single ref and commit SHA.
    build_id = jobs_service.enqueue_build(job_id, ref, commit_sha)
    return flask.jsonify({'success': True, 'build_id': build_id, 'message': 'Build enqueued.'})
  else:
    # Update refs and trigger all builds.
    build_ids = jobs_service.run_job(job_id)
    if build_ids:
      message = 'Refs changed, enqueued %s builds.' % len(build_ids)
    else:
      message = 'No refs changed, nothing to build.'
    return flask.jsonify({'success': True, 'message': message})


if __name__ == '__main__':
  app.run(debug=True)
