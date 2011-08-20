from django.test.testcases import TestCase



class TestLinkedInOAuth(TestCase):
    def test_authenticate(self):
        resp = self.client.get('/auth/linkedin/authenticate/')
        print resp