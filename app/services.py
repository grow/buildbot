import models
import subprocess


class RepoService(object):

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
                ref_map[ref] = {'sha': commit_sha}

            repo.ref_map = ref_map
            repo.put()
        except subprocess.CalledProcessError, e:
            success = False
            output = e.output

        return {
            'success': success,
            'output': output,
        }

    @staticmethod
    def find_ref_diffs(old_ref_map, new_ref_map):
        updated_items = []
        for key in new_ref_map:
          # Add refs if the SHA has changed.
          if key in old_ref_map and new_ref_map[key]['sha'] != old_ref_map[key]['sha']:
            updated_items.append({key: new_ref_map[key]})
          # Add new refs we haven't seen before.
          if key not in old_ref_map:
            updated_items.append({key: new_ref_map[key]})
