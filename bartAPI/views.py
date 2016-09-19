from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import json
from . import parsers

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class TokenError(Error):
    """Exception raised for errors in validating the token.

    Attributes:
        token -- the faulty token
        message -- explanation of the error
    """

    def __init__(self, token, message):
        self.token = token
        self.message = message

class CommandError(Error):
    pass

# Get info from the bart API
def bartAPIRequest(request):
    try:
        token = request.POST['token']
        tokenValid = validateToken(token)

        apiKey = "QJ49-P29I-9JGT-DWE9"

        commandText = ""
        # check for command text
        if not('text' in request.POST):
            print "test"
            raise CommandError
        else:
            print "hey"
            # etd/sched split
            commandText = request.POST.get('text')


        #link = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig=24th&key=QJ49-P29I-9JGT-DWE9"
        link = "http://api.bart.gov/api/sched.aspx?cmd=depart&orig=24th&dest=mont&key=QJ49-P29I-9JGT-DWE9"
        xmlResponse = requests.get(link)
        #responseDict = parsers.etdParse(xmlResponse.content)
        responseDict = parsers.departParse(xmlResponse.content)
        return JsonResponse(responseDict)
    except TokenError:
        print "token error"
        return HttpResponse("The token was invalid")
    except CommandError:
        print "command error"
        return HttpResponse("Invalid command")

# check the Slack token
def validateToken(token):
    valid = False
    if token == "19lVoTg9TKAE5wUn45zQkh6t":
        valid = True
    else:
        raise TokenError