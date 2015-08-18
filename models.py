from google.appengine.ext import ndb


class GitRepo(ndb.Model):
    """Models a git repository."""
    git_url = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
