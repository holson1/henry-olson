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
def bart_api_request(request):
    try:
        token = request.POST['token']
        token_valid = validate_token(token)

        api_key = "QJ49-P29I-9JGT-DWE9"

        command_text = ""
        commands = []

        # check for command text
        if not('text' in request.POST):
            raise CommandError

        # etd/sched split
        command_text = request.POST.get('text')
        valid = parse_commands(command_text)

        #link = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig=24th&key=QJ49-P29I-9JGT-DWE9"
        link = "http://api.bart.gov/api/sched.aspx?cmd=depart&orig=24th&dest=mont&key=QJ49-P29I-9JGT-DWE9"
        xml_response = requests.get(link)
        #responseDict = parsers.etdParse(xmlResponse.content)
        response_dict = parsers.depart_parse(xml_response.content)
        return JsonResponse(response_dict)
    except TokenError:
        print "token error"
        return HttpResponse("The token was invalid")
    except CommandError:
        print "command error"
        return HttpResponse("Invalid command")

# check the Slack token
def validate_token(token):
    valid = False
    if token == "19lVoTg9TKAE5wUn45zQkh6t":
        valid = True
    else:
        raise TokenError

def parse_commands(command_text):
    # get list of valid commands...simple for now but we may want to store it and get it
    valid_commands = [{'name': 'etd', 'link': 'etd', 'params': [{'orig': ''}]},
                      {'name': 'depart', 'link': 'sched', 'params': [{'orig': ''}, {'dest': ''}]}]
    valid_stations = ['24th', 'mont', 'frmt', '16th']
    
    found_matching_command = False
    valid_params = False

    if command_text == "":
        raise CommandError

    commands = command_text.split()
    for command_type in valid_commands:
        if commands[0] == command_type['name']:
            found_matching_command = True
            commands.pop(0)
            if len(commands) == len(command_type['params']):
                # map command parameters to command_type
                print "valid so far"
                valid_params = True
                break
            else:
                print "invalid number of args"
                raise CommandError

    if found_matching_command and valid_params:
        return True
    else:
        raise CommandError