#!/usr/bin/env python

import os
import webapp2
from webapp2_extras import jinja2
from app import services


WEBAPP_CONFIG = {
    'webapp2_extras.jinja2': {
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    }
}


class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)


class MainPageHandler(BaseHandler):

    def get(self):
        repos = services.RepoService.list_repos()
        self.render_response('index.html', repos=repos)


class ReposHandler(BaseHandler):

    def post(self):
        git_urls = self.request.get('git_url', allow_multiple=True)
        for git_url in git_urls:
            services.RepoService.add_repo(git_url=git_url)
        self.render_response('repos_added.html')


class ReposSyncHandler(BaseHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        repo_ids = self.request.get('id', allow_multiple=True)
        if repo_ids:
            repos = services.RepoService.get_repos(ids=repo_ids)
        else:
            repos = services.RepoService.list_repos()

        self.response.write('syncing repos ({})...\n\n'.format(len(repos)))
        for repo in repos:
            self.response.write('syncing repo: {}\n'.format(repo.git_url))
            result = services.RepoService.sync_repo(repo=repo)

            if not result['success']:
                self.response.write('SYNC FAILED.\n')
            else:
                diff_ref_maps = result['diff_ref_maps']
                if diff_ref_maps:
                    self.response.write('Git refs changed:\n')
                    for ref, data in diff_ref_maps.iteritems():
                        self.response.write(
                            '{}  {}\n'.format(data['sha'], ref))
                    self.response.write('Triggering builds...\n')
                    services.RepoService.trigger_builds(repo=repo, diff_ref_maps=diff_ref_maps)
                    self.response.write(
                        '%s builds triggered.\n' % len(diff_ref_maps))
                else:
                    self.response.write('No updated refs found.\n')
            self.response.write('---\n')


class BuildsTriggerHandler(BaseHandler):

    def get(self):
        repo_id = self.request.get('repo_id')
        ref = self.request.get('ref')
        commit_sha = self.request.get('sha')

        repo = services.RepoService.get_repos(ids=[repo_id])[0]
        services.RepoService.trigger_build(repo=repo, ref=ref, commit_sha=commit_sha)

        self.render_response('build_triggered.html')


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/api/v1/repos', ReposHandler),
    ('/api/v1/repos/sync', ReposSyncHandler),
    ('/api/v1/builds/trigger', BuildsTriggerHandler),
], debug=True, config=WEBAPP_CONFIG)
