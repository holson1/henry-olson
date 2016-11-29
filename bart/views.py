from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import json
import logging
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

    def __init__(self, token):
        self.token = token

class CommandError(Error):
    pass

log = logging.getLogger('bart')

# Get info from the bart API
@csrf_exempt
def bart_api_request(request):
    try:
        log.debug("bart_api_request called")
        #token = request.POST["token"]
        token = request.POST.get("token", "")
        token_valid = validate_token(token)

        log.debug("valid slack token")
        api_key = "QJ49-P29I-9JGT-DWE9"

        command_text = ""
        commands = []

        # check for command text
        if not("text" in request.POST):
            raise CommandError

        # etd/sched split
        payload_text = request.POST.get("text")
        valid_command = parse_command(payload_text)
        print "valid command: ", valid_command
        log.debug("valid command entered")

        #link = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig=24th&key=QJ49-P29I-9JGT-DWE9"
        #link = "http://api.bart.gov/api/sched.aspx?cmd=depart&orig=24th&dest=mont&key=QJ49-P29I-9JGT-DWE9"

        # build bart api link
        link = valid_command["link"]
        if link == "":
            response_dict = getattr(parsers, valid_command["parser"])()
        else:
            for param in valid_command["params"]:
                link = link + param["name"] + "=" + param["value"] + "&"
            if "optionals" in valid_command:
                for optional_param in valid_command["optionals"]:
                    if not optional_param["value"] == "":
                        link = link + optional_param["name"] + "=" + optional_param["value"] + "&"
            if "presets" in valid_command:
                for preset in valid_command["presets"]:
                    link = link + preset["name"] + "=" + preset["value"] + "&"
            link = link + "key=" + api_key

            print "link: ", link

            xml_response = requests.get(link)
            response_dict = getattr(parsers, valid_command["parser"])(xml_response.content)
        return JsonResponse(response_dict)
    except TokenError:
        print "token error"
        return HttpResponse("A valid slack token was not provided as part of the request.")
    except CommandError:
        print "command error"
        return HttpResponse("Invalid command")

# check the Slack token
@csrf_exempt
def validate_token(token):
    valid = False
    if token == "19lVoTg9TKAE5wUn45zQkh6t":
        valid = True
    else:
        raise TokenError(token)

@csrf_exempt
def parse_command(payload_text):
    # get list of valid commands...simple for now but we may want to store it and get its
    valid_commands = {  "etd": 
                            {"link": "http://api.bart.gov/api/etd.aspx?", "parser": "etd_parse", 
                                "params": [
                                    {"name": "cmd", "type": "", "value": ""}, 
                                    {"name": "orig", "type": "station", "value": ""}
                                ],
                                "optionals": [
                                    {"name": "dir", "type": "dir", "value": ""}
                                ]
                            },
                        "depart": 
                            {"link": "http://api.bart.gov/api/sched.aspx?", "parser": "depart_parse", 
                                "params": [
                                    {"name": "cmd", "type": "", "value": ""}, 
                                    {"name": "orig", "type": "station", "value": ""}, 
                                    {"name": "dest", "type": "station", "value": ""}
                                ],
                                "presets": [
                                    {"name": "b", "value": "0"}
                                ]
                            },
                        "help":
                            {"link": "", "parser": "display_help", 
                                "params": [
                                    {"name": "cmd", "type": "", "value": ""}
                                ]
                            }
                    }
    
    
    found_matching_command = False

    if payload_text == "":
        raise CommandError

    parameters = payload_text.split()
    command = parameters[0]
    if command in valid_commands:
        valid_command = valid_commands.get(command, None)
        found_matching_command = True
        num_params = len(parameters)
        expected_params = len(valid_command["params"])
        expected_optionals = 0
        if "optionals" in valid_command:
            expected_optionals = len(valid_command["optionals"])

        # make sure the # of parameters entered matches up with what the command expects
        if num_params >= expected_params and num_params <= expected_params + expected_optionals:
            # map command parameters to command_type
            print "valid number of commands"
            i = 0

            # standard parameters, all of which must be entered
            for param in valid_command["params"]:
                print parameters[i]
                print param
                # check that any stations entered are valid
                validate_param(param["type"], parameters[i])
                param["value"] = parameters[i]
                i += 1
            
            # optional parameters
            if expected_optionals > 0:
                for optional_param in valid_command["optionals"]:
                    while i < num_params:
                        validate_param(optional_param["type"], parameters[i])
                        optional_param["value"] = parameters[i]
                        i += 1
            return valid_command
        else:
            print "invalid number of args"
            raise CommandError
    else:
        print "invalid command. valid commands: etd, depart"
        raise CommandError

# validate params which require specific values
@csrf_exempt
def validate_param(type, value):
    # TODO: get this from the model, which will in turn get it from an API call
    valid_stations = ["24th", "mont", "frmt", "16th", "sfia"]
    valid_dirs = ["n", "s"]

    print type
    print value

    if type == "":
        pass

    if type == "station":
        if value not in valid_stations:
            print "invalid station"
            raise CommandError
    
    if type == "dir":
        if value not in valid_dirs:
            print "invalid dir"
            raise CommandError