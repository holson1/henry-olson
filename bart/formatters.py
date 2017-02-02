import lxml
from lxml import etree
import time
from bart.models import Line, Station
from django.db.models import Q

# display the help text
def display_help():
    slack_response = {'text': '*Thanks for using Bart Trip Planner!*\n*List of available commands:*', 'attachments': [
        {'title': '/bart [station]', 'color': '#ff0000', 'text': 'returns the estimated time of departure for trains at the entered [station]'},
        {'title': '/bart [origin] [destination]', 'color': '#0099cc', 'text': 'returns the closest times for trains departing the [origin] station and heading to the [destination] station'},
        {'text': 'Visit http://henry-olson.com/bart for more information and advanced usage.'}
    ]}

    slack_response['footer'] = "bart slack app"
    slack_response['ts'] = time.time()

    return slack_response


# format the XML response for the etd command
def etd_format(xml):
    tree = etree.fromstring(xml)
    #time = tree.xpath("/root/time/text()")

    slack_response = {"text": "", "attachments": []}

    origin_station = tree.find('./station')
    origin_station_name = origin_station.findtext('./name')
    slack_response['text'] = "*Estimated Departure Times for %s*" % (origin_station_name)

    etd_list = origin_station.findall('etd')
    i = 0
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
            if minutes == "Leaving":
                display_string = "%s car train departing now" % (car_length)

            field = {"value": display_string, "short": "false"}
            attachment['fields'].append(field)
            attachment['color'] = color

        slack_response['attachments'].append(attachment)

        # if this is the very last etd list...
        if i == len(etd_list) - 1:
            spacer = {
                "text": " ",
                "color": "#dddddd",
                "footer": "bart slack integration",
                "ts": time.time()
            }
            slack_response['attachments'].append(spacer)
        
        i += 1
    return slack_response

# format the xml response for the sched - depart command
def depart_format(xml):
    tree = etree.fromstring(xml)

    slack_response = {"text": "", "attachments": []}

    origin = get_station_name(tree.findtext('./origin'))
    destination = get_station_name(tree.findtext('./destination'))

    slack_response['text'] = "*Trips from %s to %s :*" % (origin, destination)

    request = tree.find('./schedule/request')
    trips = request.findall('trip')
    i = 0

    for trip in trips:
        legs = trip.findall('leg')
        j = 0
        for leg in legs:
            attachment = {}
            attachment['fields'] = []
            line_color = ""

            time_depart = leg.get('origTimeMin')
            time_arrive = leg.get('destTimeMin')
            head_station = get_station_name(leg.get('trainHeadStation'))
            leg_origin = get_station_name(leg.get('origin'))
            leg_destination = get_station_name(leg.get('destination'))


            lines = Line.objects.filter(Q(stations__name__icontains=leg_destination))
            lines = lines.filter(Q(stations__name__icontains=leg_origin))
            # this isn't right... we might have a head station not in the line name
            lines = lines.filter(Q(stations__name__icontains=head_station))

            print "HEAD STATION: " + head_station
            for line in lines:
                print line.name
                # only grab the first color
                if line_color == "":
                    line_color = line.hex_color
                
            print "---"

            # the spacer is used to denote a transfer or separate trips clearly
            spacer = {}
            # if there are multiple legs, use the spacer to indicate a transfer station
            if len(legs) > 1 and (j < len(legs) - 1):
                leg_destination = "_*TRANSFER*_ at " + leg_destination
                #spacer['text'] = "Transfer at %s" % (leg_destination)
            else:
                spacer['text'] = " "
                spacer['color'] = "#dddddd"
            
            # if this is the very last spacer...
            if (i == len(trips) - 1 and j == len(legs) - 1):
                spacer['footer'] = "bart slack integration"
                spacer['ts'] = time.time()
            
            # main attachment
            title_string = "%s line" % (head_station)
            display_string = "%s %s  :arrow_right:  %s %s" % (time_depart, leg_origin, time_arrive, leg_destination)
            field = {"title": title_string, "value": display_string, "short": "false"}

            attachment['fields'].append(field)
            attachment['color'] = line_color
            attachment['mrkdwn_in'] = ['fields']
        
            slack_response['attachments'].append(attachment)
            slack_response['attachments'].append(spacer)

            j += 1
        i += 1
    return slack_response

# returns the full station name when provided a key (unfortunately, the only thing the API tends to return)
def get_station_name(key):
    name = key
    matches = Station.objects.filter(key__icontains=key)
    for match in matches:
        name = match.name
        break
    return name