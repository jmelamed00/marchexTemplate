from subRoutines import *
import pandas as pd

start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}

# Collect all Marketing Edge Entities from APIs
entities = useThreadsToCollectEntities(header)
print('All Entities collected.')

# Read data from a file that lives in the same directory as this code.
data = pd.read_excel(r'updateGroups.xlsx', sheet_name='Sheet1')

# Setup output storage
goodData = []
failData = []
idICareAbout = 0
for index, row in data.iterrows():
    campaignName = row['Campaign Name']

    for group in entities['Groups']:
        if group['name'] == campaignName:
            idICareAbout = group['id']

    if idICareAbout % 2 == 0:
        goodData.append({'Campaign Name': str(row['Campaign Name'])})
    else:
        failData.append({'Campaign Name': str(row['Campaign Name'])})

pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)
