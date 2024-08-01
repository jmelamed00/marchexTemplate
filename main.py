from subRoutines import *
import pandas as pd

start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}
ga4URL = 'https://edgeapi.marchex.io/marketingedge/v5/api/IntegrationConfigurations/googleAnalytics4'

# Collect all Marketing Edge Entities from APIs
entities = useThreadsToCollectEntities(header)
for key in entities:
    if key == 'billinggroups':
        continue
    print(entities['billinggroups'][0]['billing_group_name'] + ' has ' + str(len(entities[key])) + ' ' + key + '.')

# Setup output storage
goodData = []
failData = []

# Before reading the file with the data to process, do $Something.
# $Something here is collect all the GA4 Configs for this org.
response = requests.get(ga4URL + '?pageSize=5000', headers=header)
if response.status_code != 200:
    print('Failed to Collect GA4 Configurations.')
    exit(1)
responseText = json.loads(response.text)
ga4Ints = responseText['results']
print('There are ' + str(len(ga4Ints)) + ' GA4 Integrations.')

# Read in each row from the file.
for index, row in inputFile.iterrows():
    print('Read some data from the ' + str(index) + ' row.')

if len(goodData):
    pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
if len(failData):
    pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)
