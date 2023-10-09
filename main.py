from subRoutines import *
import pandas as pd

start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}

# Collect all Marketing Edge Entities from APIs
entities = useThreadsToCollectEntities(header)
print('All Entities collected.')
count = 0

# Read data from a file
data = pd.read_excel(r'C:\Users\jmelamed\PycharmProjects\template\notificationFails.xlsx', sheet_name='Sheet1')

# Setup output storage
goodData = []
failData = []
for index, row in data.iterrows():
    campaignID = row.CampaignId
    campaignName = row.CampaignName

    if campaignID % 2 == 0:
        goodData.append({'Campaign Name': str(row['Campaign Name']), 'Campaign ID': str(row['Campaign ID'])})
    else:
        failData.append({'Campaign Name': str(row['Campaign Name']), 'Campaign ID': str(row['Campaign ID'])})

pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)
