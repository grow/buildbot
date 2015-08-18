import subprocess
import webapp2
import models


class MainService(object):

    @staticmethod
    def repo_ref_key(repo, sha):
        return '{}:{}'.format()

    @staticmethod
    def list_repos():
        return list(models.Repo.query())

    @staticmethod
    def sync_repo(repo):
        success = True
        try:
            command = ['git', 'ls-remote', '--heads', repo.git_url]
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)

            ref_map = {}
            for line in output.splitlines():
                commit_sha, ref = line.split()
                ref_map[ref] = commit_sha

            repo.refs_to_shas = ref_map
            repo.put()
        except subprocess.CalledProcessError, e:
            success = False
            output = e.output

        return {
            'success': success,
            'output': output,
        }


class MainPageHandler(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        repos = MainService.list_repos() or []
        self.response.write('repos ({}):\n'.format(len(repos)))
        for repo in repos:
            self.response.write('repo: {}\n'.format(str(repo)))


class ApiSyncHandler(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        repos = MainService.list_repos() or []
        self.response.write('syncing repos ({})...\n\n'.format(len(repos)))
        for repo in repos:
            self.response.write('syncing repo: {}\n'.format(repo.git_url))
            result = MainService.sync_repo(repo=repo)

            if not result['success']:
                self.response.write('FAILED.\n')
            for ref, sha in repo.refs_to_shas.iteritems():
                self.response.write('{}  {}\n'.format(sha, ref))

            self.response.write('---\n')


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/api/sync', ApiSyncHandler),
], debug=True)
