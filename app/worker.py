#!/usr/bin/env python

import flask
import jobs_service
from flask import request

app = flask.Flask(__name__)


@app.route('/')
def index():
    jobs = jobs_service.list_jobs()
    return flask.render_template('index.html', jobs=jobs, num_jobs=len(jobs))


@app.route('/api/jobs', methods=['POST'])
def create_job():
    git_url = request.args.get('git_url')
    assert git_url
    job_id = jobs_service.create_job(git_url=git_url)
    return flask.jsonify({'success': True, 'job_id': job_id})


@app.route('/api/jobs/<int:job_id>/run', methods=['GET', 'POST'])
def run_job(job_id):
    result = jobs_service.run_builds(job_id)
    return flask.jsonify({'success': True, 'output': result['output']})


if __name__ == '__main__':
    app.run(debug=True)
