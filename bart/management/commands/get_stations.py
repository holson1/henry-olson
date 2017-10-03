from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from bart.models import Station
from django.conf import settings

import requests
from lxml import etree

class Command(BaseCommand):

    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        link = "http://api.bart.gov/api/stn.aspx?cmd=stns&key=" + settings.BART_API_KEY
        xml_response = requests.get(link)
        tree = etree.fromstring(xml_response.content)
        stations = tree.findall('./stations/station')
        for station in stations:
            name =  station.findtext('./name')
            abbr = station.findtext('./abbr').upper()
            try:
                station = Station.objects.get(key=abbr)
            except ObjectDoesNotExist:
                Station.objects.create(name=name, key=abbr)
