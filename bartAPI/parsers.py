import lxml
from lxml import etree
import time

# parse the XML response for the etd command
def etdParse(xml):
    tree = etree.fromstring(xml)
    #time = tree.xpath("/root/time/text()")

    slackResponse = {"text": "", "attachments": []}

    originStation = tree.find('./station')
    originStationName = originStation.findtext('./name')
    slackResponse['text'] = "Estimated Departure Times for %s" % (originStationName)

    etdList = originStation.findall('etd')
    for etd in etdList:
        attachment = {"title": ""}
        destination = etd.findtext('./destination')

        attachment['title'] = destination
        attachment['fields'] = []

        estimateList = etd.findall('estimate')
        for estimate in estimateList:
            minutes = estimate.findtext('./minutes')
            color = estimate.findtext('./hexcolor')
            carLength = estimate.findtext('./length')
            
            displayString = "%s car train departing in %s minutes" % (carLength, minutes)

            field = {"value": displayString, "short": "false"}

            attachment['fields'].append(field)
            attachment['color'] = color
            

        slackResponse['attachments'].append(attachment)

    slackResponse['footer'] = "bart slack app"
    slackResponse['ts'] = time.time()

    return slackResponse

# parse the xml response for the sched - depart command
def departParse(xml):
    tree = etree.fromstring(xml)

    slackResponse = {"text": "", "attachments": []}

    origin = tree.findtext('./origin')
    destination = tree.findtext('./destination')

    slackResponse['text'] = "Trips from %s to %s :" % (origin, destination)

    request = tree.find('./schedule/request')
    trips = request.findall('trip')
    for trip in trips:

        attachment = {}
        attachment['fields'] = []

        legs = trip.findall('leg')

        # only display fields as short if there is more than one leg
        short = "false"
        if len(legs) > 1:
            short = "true"

        for leg in legs:
            timeDepart = leg.get('origTimeMin')
            timeArrive = leg.get('destTimeMin')
            headStation = leg.get('trainHeadStation')
            legOrigin = leg.get('origin')
            legDestination = leg.get('destination')

            titleString = "%s line" % (headStation)
            displayString = "%s %s depart -&gt; %s %s arrive" % (timeDepart, legOrigin, timeArrive, legDestination)
            field = {"title": titleString, "value": displayString, "short": short}

            attachment['fields'].append(field)
        
        slackResponse['attachments'].append(attachment)
    
    slackResponse['footer'] = "bart slack app"
    slackResponse['ts'] = time.time()

    return slackResponse