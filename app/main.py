#!/usr/bin/env python

import webapp2
from app import services

class MainPageHandler(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        repos = services.RepoService.list_repos() or []
        self.response.write('repos ({}):\n'.format(len(repos)))
        for repo in repos:
            self.response.write('repo: {}\n'.format(str(repo)))


class ApiSyncHandler(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        repos = services.RepoService.list_repos() or []
        self.response.write('syncing repos ({})...\n\n'.format(len(repos)))
        for repo in repos:
            self.response.write('syncing repo: {}\n'.format(repo.git_url))
            result = services.RepoService.sync_repo(repo=repo)

            if not result['success']:
                self.response.write('FAILED.\n')
            for ref, data in repo.ref_map.iteritems():
                self.response.write('{}  {}\n'.format(data['sha'], ref))

            self.response.write('---\n')


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/api/sync', ApiSyncHandler),
], debug=True)
