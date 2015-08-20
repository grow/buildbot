import services
import unittest


class RepoServiceTestCase(unittest.TestCase):

  def test_(self):
      # Same SHA.
      old = {'refs/heads/master': {'sha': 'AAA'}}
      new = {'refs/heads/master': {'sha': 'AAA'}}
      diff = services.RepoService.find_ref_diffs(old, new)
      self.assertEqual({}, diff)

      # Diff SHA.
      old = {'refs/heads/master': {'sha': 'AAA'}}
      new = {'refs/heads/master': {'sha': 'ABB'}}
      diff = services.RepoService.find_ref_diffs(old, new)
      self.assertEqual({'refs/heads/master': {'sha': 'ABB'}}, diff)

      # Added SHA.
      old = {'refs/heads/master': {'sha': 'AAA'}}
      new = {'refs/heads/master': {'sha': 'AAA'}, 'refs/heads/branch': {'sha': 'BBB'}}
      diff = services.RepoService.find_ref_diffs(old, new)
      self.assertEqual({'refs/heads/branch': {'sha': 'BBB'}}, diff)


if __name__ == '__main__':
    unittest.main()
