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
                self.response.write('SYNC FAILED.\n')
            else:
                diff_ref_maps = result['diff_ref_maps']
                if diff_ref_maps:
                    self.response.write('Git refs changed:\n')
                    for ref, data in diff_ref_maps.iteritems():
                        self.response.write('{}  {}\n'.format(data['sha'], ref))
                    self.response.write('Triggering builds...\n')
                    services.RepoService.trigger_builds(repo=repo, diff_ref_maps=diff_ref_maps)
                    self.response.write('%s builds triggered.\n' % len(diff_ref_maps))
                else:
                    self.response.write('No diffs found.\n')
            self.response.write('---\n')

app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/api/v1/repos/sync', ApiSyncHandler),
], debug=True)
