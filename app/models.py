from google.appengine.ext import ndb

class Repo(ndb.Model):
    git_url = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    ref_map = ndb.JsonProperty(default={})

