import lxml
from lxml import etree
import time

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