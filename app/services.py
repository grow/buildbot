import json
import models
import subprocess
from google.appengine.api import taskqueue


class RepoService(object):

    @staticmethod
    def repo_ref_key(repo, sha):
        return '{}:{}'.format()

    @staticmethod
    def list_repos():
        return list(models.Repo.query())

    @staticmethod
    def sync_repo(repo):
        diff_ref_maps = {}
        success = True
        try:
            command = ['git', 'ls-remote', '--heads', repo.git_url]
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)

            ref_map = {}
            for line in output.splitlines():
                commit_sha, ref = line.split()
                ref_map[ref] = {'sha': commit_sha}

            diff_ref_maps = RepoService.find_ref_diffs(repo.ref_map, new_ref_map=ref_map)
            repo.ref_map = ref_map
            repo.put()
        except subprocess.CalledProcessError, e:
            success = False
            output = e.output

        return {
            'success': success,
            'output': output,
            'diff_ref_maps': diff_ref_maps,
        }

    @staticmethod
    def trigger_builds(repo, diff_ref_maps):
        for ref in diff_ref_maps:
            RepoService.trigger_build(repo=repo, ref=ref, commit_sha=diff_ref_maps[ref]['sha'])

    @staticmethod
    def trigger_build(repo, ref, commit_sha):
        queue = taskqueue.Queue('builds')
        payload_data = {'git_url': repo.git_url, 'ref': ref, 'commit_sha': commit_sha}
        queue.add(taskqueue.Task(payload=json.dumps(payload_data), method='PULL'))

    @staticmethod
    def find_ref_diffs(old_ref_map, new_ref_map):
        updated_items = {}
        for key in new_ref_map:
          # Add refs if the SHA has changed.
          if key in old_ref_map and new_ref_map[key]['sha'] != old_ref_map[key]['sha']:
            updated_items[key] = new_ref_map[key]
          # Add new refs we haven't seen before.
          if key not in old_ref_map:
            updated_items[key] = new_ref_map[key]
        return updated_items
