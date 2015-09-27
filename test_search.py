import sys, json, unittest
from api import app, search

# Run with nosetests (or sniffer if you prefer autotest styled testing)
# TODO Very bare bones; needs setup and teardown
# At the moment it just sets up on its own

class SearchTest(unittest.TestCase):
    def test_search_0_1(self):
        tester = app.test_client(self) # segregate this out
        response = tester.get('/search?q=thistle', content_type='application/json') # replace thistle with something in the present neo4j instance
        self.assertEqual(response.status_code, 200)
        #obj = json.loads(response.data)
        #self.assertContains(obj, 'thistle')

if __name__ == '__main__':
    unittest.main()
