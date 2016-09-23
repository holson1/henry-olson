import lxml
from lxml import etree
import time

# parse the XML response for the etd command
def etd_parse(xml):
    tree = etree.fromstring(xml)
    #time = tree.xpath("/root/time/text()")

    slack_response = {"text": "", "attachments": []}

    origin_station = tree.find('./station')
    origin_station_name = origin_station.findtext('./name')
    slack_response['text'] = "Estimated Departure Times for %s" % (origin_station_name)

    etd_list = origin_station.findall('etd')
    for etd in etd_list:
        attachment = {"title": ""}
        destination = etd.findtext('./destination')

        attachment['title'] = destination
        attachment['fields'] = []

        estimate_list = etd.findall('estimate')
        for estimate in estimate_list:
            minutes = estimate.findtext('./minutes')
            color = estimate.findtext('./hexcolor')
            car_length = estimate.findtext('./length')
            
            display_string = "%s car train departing in %s minutes" % (car_length, minutes)

            field = {"value": display_string, "short": "false"}

            attachment['fields'].append(field)
            attachment['color'] = color
            

        slack_response['attachments'].append(attachment)

    slack_response['footer'] = "bart slack app"
    slack_response['ts'] = time.time()

    return slack_response

# parse the xml response for the sched - depart command
def depart_parse(xml):
    tree = etree.fromstring(xml)

    slack_response = {"text": "", "attachments": []}

    origin = tree.findtext('./origin')
    destination = tree.findtext('./destination')

    slack_response['text'] = "Trips from %s to %s :" % (origin, destination)

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
            time_depart = leg.get('origTimeMin')
            time_arrive = leg.get('destTimeMin')
            head_station = leg.get('trainHeadStation')
            leg_origin = leg.get('origin')
            leg_destination = leg.get('destination')

            title_string = "%s line" % (head_station)
            display_string = "%s %s depart -&gt; %s %s arrive" % (time_depart, leg_origin, time_arrive, leg_destination)
            field = {"title": title_string, "value": display_string, "short": short}

            attachment['fields'].append(field)
        
        slack_response['attachments'].append(attachment)
    
    slack_response['footer'] = "bart slack app"
    slack_response['ts'] = time.time()

    return slack_response