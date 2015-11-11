import git
import md5
import os


class Error(Exception):
  pass


class ConflictError(Error):
  pass


class IntegrationError(Error):
  pass


def get_workspace_root():
  if not os.path.isdir('/data'):
    # Handle non-docker environments. :|
    return '/tmp/grow/workspaces/'
  return '/data/grow/workspaces/'


def get_work_dir(job_id):
  return get_workspace_root() + str(job_id)


def get_repo(job_id):
  path = get_work_dir(job_id)
  repo = git.Repo(path)
  if repo is None:
    raise Error('Repo in {} not found'.format(path))
  return repo


def clone_repo(job_id, url, branch):
  work_dir = get_work_dir(job_id)
  if not os.path.exists(work_dir):
    repo = git.Repo.clone_from(url, work_dir, depth=50)
  else:
    repo = git.Repo(work_dir)
  try:
    repo.git.checkout(b=branch)
  except git.GitCommandError as e:
    if 'already exists' in str(e):
      repo.git.checkout(branch)
  return repo


def init_repo(job_id, url, branch):
  repo = clone_repo(job_id, url, branch)
  origin = repo.remotes.origin
  origin.fetch()
  origin.pull()
  return repo


def update(repo, branch, path, content, sha, message=None, committer=None, author=None):
  # TODO: Verify workspace file sha against one provided by user.
  local_branch = 'tmp'
  origin = repo.remotes.origin
  origin.pull()
  try:
    repo.create_head(
        local_branch, origin.refs[branch]).set_tracking_branch(origin.refs[branch])
  except OSError as e:
    if 'does already exist, pointing to' in str(e):
      raise ConflictError(e)
  path = path.lstrip('/')
  path = os.path.join(repo.working_tree_dir, path)
  if not os.path.exists(os.path.dirname(path)):
    os.makedirs(os.path.dirname(path))
  with open(path, 'w') as f:
    f.write(content.encode('utf-8'))
  repo.index.add([path])
  author = git.Actor(author['name'], author['email']) if author else None
  committer = git.Actor(committer['name'], committer['email']) if committer else None
  repo.index.commit(message, author=author, committer=committer)
  push_info = origin.push()
  repo.delete_head(local_branch)
  if 'rejected' in push_info[0].summary:
    raise IntegrationError(push_info[0].summary)
  return repo.remotes.origin.url
