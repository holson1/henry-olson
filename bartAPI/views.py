from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import json
from . import parsers
from django.views.decorators.csrf import csrf_exempt

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
@csrf_exempt
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
        payload_text = request.POST.get('text')
        valid_command = parse_command(payload_text)
        print "valid command: ", valid_command

        #link = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig=24th&key=QJ49-P29I-9JGT-DWE9"
        #link = "http://api.bart.gov/api/sched.aspx?cmd=depart&orig=24th&dest=mont&key=QJ49-P29I-9JGT-DWE9"

        # build bart api link
        link = valid_command['link']
        if link == '':
            response_dict = getattr(parsers, valid_command['parser'])()
        else:
            for param in valid_command['params']:
                link = link + param['name'] + "=" + param['value'] + "&"
            link = link + "key=" + api_key

            print "link: ", link

            xml_response = requests.get(link)
            response_dict = getattr(parsers, valid_command['parser'])(xml_response.content)
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

def parse_command(payload_text):
    # get list of valid commands...simple for now but we may want to store it and get its
    valid_commands = {  'etd': 
                            {'link': 'http://api.bart.gov/api/etd.aspx?', 'parser': 'etd_parse', 'params': [
                                {'name': 'cmd', 'type': '', 'value': ''}, 
                                {'name': 'orig', 'type': 'station', 'value': ''}]
                            },
                        'depart': 
                            {'link': 'http://api.bart.gov/api/sched.aspx?', 'parser': 'depart_parse', 'params': [
                                {'name': 'cmd', 'type': '', 'value': ''}, 
                                {'name': 'orig', 'type': 'station', 'value': ''}, 
                                {'name': 'dest', 'type': 'station', 'value': ''}]
                            },
                        'help':
                            {'link': '', 'parser': 'display_help', 'params': [
                                {'name': 'cmd', 'type': '', 'value': ''}]
                            }
                    }
    valid_stations = ['24th', 'mont', 'frmt', '16th', 'sfia']
    
    found_matching_command = False

    if payload_text == "":
        raise CommandError

    parameters = payload_text.split()
    command = parameters[0]
    if command in valid_commands:
        valid_command = valid_commands.get(command, None)
        found_matching_command = True
        if len(parameters) == len(valid_command['params']):
            # map command parameters to command_type
            print "valid number of commands"
            i = 0
            for param in valid_command['params']:
                # check that any stations entered are valid
                if param['type'] == "station" and parameters[i] not in valid_stations:
                    print "invalid station"
                    raise CommandError
                param['value'] = parameters[i]
                i += 1
            return valid_command
        else:
            print "invalid number of args"
            raise CommandError
    else:
        print "invalid command. valid commands: etd, depart"
        raise CommandError