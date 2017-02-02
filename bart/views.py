from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import json
import logging
import os
import lxml
from lxml import etree
from datetime import datetime
from . import formatters
from django.views.decorators.csrf import csrf_exempt
from bart.models import Command, Parameter, Station, StationAlias
from django.db.models import Q

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
    def __init__(self, command, response):
        self.command = command
        self.response = "Invalid command: " + response
    

log = logging.getLogger('bart')

# can be global...why not
api_key = "QJ49-P29I-9JGT-DWE9"

# display the landing page for Bart Trip Planner
def bart_landing(request):
    log.debug("landing page called")
    return render(request, "bart/index.html")

# Get info from the bart API
@csrf_exempt
def bart_api_request(request):
    try:

        token = request.POST.get("token", "")
        token_valid = validate_token(token)
        log.debug("valid slack token")

        # check for slack command text...if nothing arrives, that's not a great sign
        if not("text" in request.POST):
            raise CommandError("", "No command was received")

        # parse the entered command and return information on the link to hit and the parser to call
        payload_text = request.POST.get("text")
        action_dict = parse_command(payload_text)
        log.debug("valid command entered")

        link = action_dict["link"]
        formatter = action_dict["formatter"]

        if link == "":
            response_dict = getattr(formatters, formatter)()
        else:
            link = link + "key=" + api_key
            xml_response = requests.get(link)
            response_dict = getattr(formatters, formatter)(xml_response.content)

        return JsonResponse(response_dict)
    except TokenError:
        print "token error"
        return HttpResponse("A valid slack token was not provided as part of the request.")
    except CommandError as ce:
        print "command error"
        return HttpResponse(ce.response)

# check the Slack token
def validate_token(token):
    valid = False
    if token == os.environ.get('BART_SLACK_TOKEN'):
        valid = True
    else:
        raise TokenError(token)


def parse_command(payload_text):
    action_dict = {"link": "", "formatter": ""}
    link = ""
    found_matching_command = False

    parameters = payload_text.split()
    command = ""
    if len(parameters) > 0:
        command = parameters[0]
    
    # current: filter to the matching command and any blank entries
    # alternate: filter first for the matching command, and if there is none, grab the blank entries (not sure this would be faster)
    command_set = Command.objects.filter(Q(name=command) | Q(name='')).order_by('-name').prefetch_related('parameter_set')
    for p_command in command_set:

        required = len(p_command.parameter_set.filter(required=True))
        optional = len(p_command.parameter_set.filter(required=False))

        # if we have the right number of params
        if len(parameters) >= required and len(parameters) <= required + optional:
            
            expected_parameters = p_command.parameter_set.all().order_by('order')

            link = p_command.link
            # add command
            if link != "":
                link += "cmd=" + p_command.api_cmd + "&"

            # run checks on stations/dirs
            i = 0
            for param in parameters:
            
                # we can throw the command out since we already add it above (and it may not be there all the time)
                if expected_parameters[i].param_type == "command":
                    i +=1
                    continue

                # check to make sure the other parameters are valid
                param = validate_param(expected_parameters[i].param_type, param)
                link += expected_parameters[i].name + "=" + param + "&"
                i += 1


            found_matching_command = True
            action_dict["link"] = link
            action_dict["formatter"] = p_command.formatter

        if found_matching_command:
            return action_dict
    
    if not found_matching_command:
        raise CommandError("", "'" + payload_text + "' is not a valid command. Type '/bart help' to see a list of valid commands.")

# validate params which require specific values
def validate_param(param_type, value):
    # Uncomment this if we need to pull/populate the stations for whatever reason
    #get_all_stations()

    valid_dirs = ["n", "s"]

    if param_type == "" or param_type == "command" or param_type == "num_trains":
        return value

    # check both the direct station matches and the aliases
    if param_type == "station":
        key_matches = Station.objects.filter(Q(key__icontains=value))
        station_matches = Station.objects.filter(Q(name__icontains=value))
        alias_matches = StationAlias.objects.filter(alias__icontains=value)
        if len(key_matches) > 0:
            for station in key_matches:
                return station.key
        if len(station_matches) > 0:
            for station in station_matches:
                return station.key
        elif len(alias_matches) > 0:
            for alias in alias_matches:
                return alias.station.key
        else:
            print "invalid station"
            raise CommandError("", "'" + value + "' is not a valid station name.")
    
    if param_type == "dir":
        if value in valid_dirs:
            return value
        else:
            print "invalid dir"
            raise CommandError("", "'" + value + "' is not a valid direction. Use 'n' or 's'.")

# populate stations list
def get_all_stations():
    link = "http://api.bart.gov/api/stn.aspx?cmd=stns&key=" + api_key
    xml_response = requests.get(link)
    tree = etree.fromstring(xml_response.content)
    stations = tree.findall('./stations/station')
    for station in stations:
        name =  station.findtext('./name')
        abbr = station.findtext('./abbr').upper()
        station_instance = Station.objects.create(name=name, key=abbr)