#!/usr/bin/env python

import flask
import urllib2
import jobs_service
import os
from flask import request
from functools import wraps

app = flask.Flask(__name__)


def get_buildbot_password_or_die():
  """Fetches the buildbot password either from GCP metadata or from an environment variable."""
  try:
    url = 'http://metadata.google.internal/computeMetadata/v1/instance/attributes/buildbot-password'
    headers = {'Metadata-Flavor': 'Google'}
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    return response.read()
  except (urllib2.URLError, urllib2.HTTPError):
    # Fall through to the environment variable.
    return os.environ['BUILDBOT_PASSWORD']


def check_auth(username, password):
  return username == 'admin' and password == get_buildbot_password_or_die()


def unauthorized():
  return flask.Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


def auth_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
      return unauthorized()
    return f(*args, **kwargs)
  return decorated


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@auth_required
def catch_all(path):
  return '404', 404


@app.route('/')
@auth_required
def index():
  jobs = jobs_service.list_jobs()
  builds = jobs_service.list_builds(limit=20)
  return flask.render_template('index.html', builds=builds, jobs=jobs)


@app.route('/builds')
@auth_required
def builds():
  builds = jobs_service.list_builds()
  return flask.render_template('builds.html', builds=builds)


@app.route('/jobs')
@auth_required
def jobs():
  jobs = jobs_service.list_jobs()
  return flask.render_template('jobs.html', jobs=jobs)


@app.route('/builds/<int:build_id>')
@auth_required
def build(build_id):
  build = jobs_service.get_build(build_id)
  return flask.render_template('build.html', build=build)


@app.route('/api/jobs', methods=['POST'])
@auth_required
def create_job():
  # TODO: better JSON API parsing and error responses.
  data = request.get_json()
  assert data.get('git_url')
  assert data.get('remote')
  assert data.get('env')
  assert data['env'].get('WEBREVIEW_API_KEY')

  job_id = jobs_service.create_job(
      git_url=data['git_url'],
      remote=data['remote'],
      env=data['env'],
  )
  return flask.jsonify({'success': True, 'job_id': job_id})


@app.route('/api/jobs/<int:job_id>/run', methods=['GET', 'POST'])
@auth_required
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
