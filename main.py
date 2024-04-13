from subRoutines import *
import pandas as pd

start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}

# Collect all Marketing Edge Entities from APIs
entities = useThreadsToCollectEntities(header)
for key in entities:
    if key == 'billinggroups':
        continue
    print(entities['billinggroups'][0]['billing_group_name'] + ' has ' + str(len(entities[key])) + ' ' + key + '.')

# Read data from a file that lives in the same directory as this code.
inputFile = pd.read_excel(r'inputFile.xlsx', sheet_name='Sheet1')

# Setup output storage
goodData = []
failData = []

# Read in each row from the file.
for index, row in inputFile.iterrows():

    foundGroup = False
    for group in entities['Groups']:
        if group['name'] == row['Campaign Name']:
            foundGroup = True
            break

    if not foundGroup:
        failData.append({'Campaign Name': row['Campaign Name'], 'Could not find this group: ': row['Campaign Name']})
        continue

if len(goodData):
    pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
if len(failData):
    pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)
