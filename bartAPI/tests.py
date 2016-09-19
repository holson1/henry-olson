from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
import json

from .views import bartAPIRequest

# test the post from slack
class SlackPost(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='henry', email='henry@test.com', password='top_secr3t')

    def test_details(self):
        # create the test data
        testDepart = { "token" : "19lVoTg9TKAE5wUn45zQkh6t",
        "team_id" : "T0001",
        "team_domain" : "example",
        "channel_id" : "C2147483705",
        "channel_name" : "test",
        "user_id" : "U2147483697",
        "user_name" : "Steve",
        "command" : "/bart",
        "text" : "depart 24th frmt"
        "response_url" : "http://api.bart.gov/api/" }

        testEtd = { "token" : "19lVoTg9TKAE5wUn45zQkh6t",
        "team_id" : "T0001",
        "team_domain" : "example",
        "channel_id" : "C2147483705",
        "channel_name" : "test",
        "user_id" : "U2147483697",
        "user_name" : "Steve",
        "command" : "/bart",
        "text" : "etd mont",
        "response_url" : "http://api.bart.gov/api/" }

        dataSet = []
        dataSet.append(testDepart)
        dataSet.append(testEtd)

        for dataDict in dataSet:   
            # Create a POST Request
            request = self.factory.post('/', dataDict)

            request.user = AnonymousUser()
            print "--------"
            #print request.POST['text']

            #test that the token matched
            # self.assertEqual(request.POST['token'], "19lVoTg9TKAE5wUn45zQkh6t")

            response = bartAPIRequest(request)
            print response
            self.assertEqual(response.status_code, 200)
        
