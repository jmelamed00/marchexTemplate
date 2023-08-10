from subRoutines import *
import pandas as pd

start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}

# Collect all Marketing Edge Entities from APIs
#
entities = useThreadsToCollectEntities(header)
print('All Entities collected. Now writing one row for each Active or Pending Number or Pool....')
count = 0
data = []
# Write information stored in data to an Excel file:
pd.DataFrame(data).to_excel('Result_'+entities['billinggroups'][0]['billing_group_name']+'_start_'+start_time+'.xlsx', index=False)


# Read data to process from a file
#
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
pd.DataFrame(failData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
