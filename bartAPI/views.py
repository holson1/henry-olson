from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import json
from . import parsers

# Get info from the bart API
def bartAPIRequest(request):
    apiKey = "QJ49-P29I-9JGT-DWE9"
    link = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig=24th&key=QJ49-P29I-9JGT-DWE9"

    xmlResponse = requests.get(link)
    responseDict = parsers.etdParse(xmlResponse.content)

    return JsonResponse(responseDict)