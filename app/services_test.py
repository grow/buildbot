import services
import unittest


class TestMainService(unittest.TestCase):

  def test_find_ref_diffs(self):
      old = {'refs/heads/master': {'sha': 'AAA'}}
      new = {'refs/heads/master': {'sha': 'AAA'}}
      diff = main.MainService.find_ref_diffs(old, new)
      self.assertEqual({}, diff)

if __name__ == '__main__':
    unittest.main()
