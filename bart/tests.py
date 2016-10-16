from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
import json

from .views import bart_api_request

# test the post from slack
class SlackPost(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='henry', email='henry@test.com', password='top_secr3t')

    def test_details(self):
        # create the test data
        test_depart = { "token" : "19lVoTg9TKAE5wUn45zQkh6t",
        "team_id" : "T0001",
        "team_domain" : "example",
        "channel_id" : "C2147483705",
        "channel_name" : "test",
        "user_id" : "U2147483697",
        "user_name" : "Steve",
        "command" : "/bart",
        "text" : "depart 24th frmt",
        "response_url" : "http://api.bart.gov/api/" }

        test_etd = { "token" : "19lVoTg9TKAE5wUn45zQkh6t",
        "team_id" : "T0001",
        "team_domain" : "example",
        "channel_id" : "C2147483705",
        "channel_name" : "test",
        "user_id" : "U2147483697",
        "user_name" : "Steve",
        "command" : "/bart",
        "text" : "etd mont",
        "response_url" : "http://api.bart.gov/api/" }

        data_list = []
        data_list.append(test_depart)
        data_list.append(test_etd)

        for data_dict in data_list:   
            # Create a POST Request
            request = self.factory.post('/', data_dict)

            request.user = AnonymousUser()
            print "--------"
            #print request.POST['text']

            #test that the token matched
            # self.assertEqual(request.POST['token'], "19lVoTg9TKAE5wUn45zQkh6t")

            response = bart_api_request(request)
            print response
            self.assertEqual(response.status_code, 200)