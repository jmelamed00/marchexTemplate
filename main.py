from subRoutines import *
import pandas as pd

start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}
groupURL = 'https://edgeapi.marchex.io/marketingedge/v5/api/Groups/'

# Collect all Marketing Edge Entities from APIs
entities = useThreadsToCollectEntities(header)
for key in entities:
    if key == 'billinggroups':
        continue
    print(entities['billinggroups'][0]['billing_group_name'] + ' has ' + str(len(entities[key])) + ' ' + key + '.')


# Read data from a file that lives in the same directory as this code.
inputFile = pd.read_excel(r'input1.xlsx', sheet_name='Sheet1')

# Setup output storage
goodData = []
failData = []

# Read in each row from the file.
for index, row in inputFile.iterrows():




    # Now that we've found the group's ID, use it to update the dni_type of this group to OneToOne
    params = {'dni_type': 'None'}
    response = requests.put(groupURL + str(group_id), headers=header, json=params)
    if response.status_code != 200:
        failData.append({'Campaign': row['campaign name'], 'Failure': 'Could not update dni_type', 'Reason': response.reason})
    else:
        goodData.append({'Campaign': row['campaign name'], 'Success': 'Flipped dni_type to static'})

if len(goodData):
    pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
if len(failData):
    pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)
