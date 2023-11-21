import requests
import math
import json
from datetime import datetime
import argparse
from threading import Thread


class CustomThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.value = None
        self.header = None
        self.endpoint = 'https://edgeapi.marchex.io/marketingedge/v5/api/'

    def run(self):
        self.value = collectEntities(self.header, self.endpoint)

# Threads are only used to speed up the process of collecting multiple, large Entities.
def useThreadsToCollectEntities(header):
    # Capitalization in the Endpoints list must exactly match the capitalization in the API URLs
    # Endpoints = ['Groups', 'numbers', 'numberpools', 'GroupOwners', 'GroupTypes', 'billinggroups']
    Endpoints = ['Groups', 'numbers', 'numberpools']
    Data = {'endpoints': Endpoints, 'threads': {}, 'entities': {}}

    for endpoint in Data['endpoints']:
        Data['threads'][endpoint] = CustomThread()
        Data['threads'][endpoint].endpoint += endpoint
        Data['threads'][endpoint].header = header
        Data['threads'][endpoint].start()

    for endpoint in Data['endpoints']:
        Data['threads'][endpoint].join()
        Data['entities'][endpoint] = Data['threads'][endpoint].value

    return Data['entities']


def collectEntities(header, url='Not Set'):
    endpointName = url[url.rfind('/') + 1:]

    # These two endpoints don't use pagination. Get 'em & return the first result.
    if endpointName == 'billinggroups' or endpointName == 'GroupTypes':
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            print('Error retrieving first page for ' + endpointName + ' due to: ' + str(response.text) + '.')
            return {}
        return json.loads(response.text)

    # Otherwise our endpoint is paginated. Store the first page of results in our Entities to Return.
    response = requests.get(url + '?pageSize=10000', headers=header)
    if response.status_code != 200:
        print('Error retrieving first page for ' + endpointName + ' due to: ' + str(response.text) + '.')
        return {}
    responseText = json.loads(response.text)
    Entities = responseText['results']

    # Calculate how many pages exist...
    paging = responseText['paging']
    numPages = math.ceil(paging['total'] / paging['pageSize'])
    if numPages > 1:
        print(endpointName + ' has ' + str(numPages) + ' pages and ' + str(paging['total']) + ' records.')
    # ...add 'em to the Entities we're returning.
    i = 1
    while i <= numPages:
        i += 1
        urlNextPage = url + '?pageSize=10000&pageNumber=' + str(i)
        response = requests.get(urlNextPage, headers=header)
        if response.status_code != 200:
            print('Error retrieving page ' + str(i) + ' from ' + endpointName + ' due to: ' + str(response.text) + '.')
            continue
        Entities.extend(json.loads(response.text)['results'])
    return Entities


def processArguments():
    arguments = {}
    parser = argparse.ArgumentParser(description='Supply Inputs: --token, --key, (optional): --start, --end')
    parser.add_argument('--token', nargs=1)
    parser.add_argument('--key', nargs=1)
    parser.add_argument('--start', nargs='?', default='')
    parser.add_argument('--end', nargs='?', default='')

    args = parser.parse_args()
    arguments['token'] = args.token[0]
    arguments['key'] = args.key[0]

    # If no value was passed for start date save De Luca's as the "early enough" start date.
    if args.start == '':
        arguments['start'] = datetime.strptime('2008-10-08', '%Y-%m-%d')
    else:
        arguments['start'] = datetime.strptime(args.start, '%Y-%m-%d')

    # If no value was passed for end date save today's date.
    if args.end == '':
        arguments['end'] = datetime.now()
    else:
        arguments['end'] = datetime.strptime(args.end, '%Y-%m-%d')
    return arguments


def getCallDetails(callID, header):
    url = 'https://edgeapi.marchex.io/marketingedge/v5/api/calls/' + callID

    response = requests.get(url, headers=header)
    if response.status_code != 200:
        print('Failed retrieving callID{' + callID + '} Response Status: ' + str(response.status_code))
        exit()
    responseText = json.loads(response.text)

    return responseText['results']
