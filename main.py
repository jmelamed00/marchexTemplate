from subRoutines import *
import pandas as pd
import requests

start_time = str(datetime.today().strftime('%H-%M-%S'))

args = processArguments()
header = {'Authorization': 'Bearer ' + args['token'], 'content-type': 'application/json'}

# Read data from a file that lives in the same directory as this code.
inputFile = pd.read_excel(r'eLocal1.xlsx', sheet_name='Sheet1')
universalURL = 'https://api.mps.ai/v1/provider/mpsuniversal'

# Setup output storage
goodData = []
failData = []

# Read in each row from the file.
for index, row in inputFile.iterrows():
    payload = {
        'RecordingURL': row['Call Dual Channel Recording URL'],
        'CallingNumber': row['CallingNumber'],
        'CalledNumber': '5108675309',
        'CallStart': row['CallStart'],
        'CallEnd': row['CallEnd'],
        'Duration': row['Call Duration'],
        'CallId': row['Call SID'],
        'Direction': 'IN',
        'Buyer ID': row['Buyer ID '],
        'Affiliate ID': row['Affiliate ID '],
        'Buyer Duration Based': row['Buyer Duration Based'],
        'Who Hung Up': row['Who Hung Up'],
        'Verification': row['Verification'],
        'eLocal Call DNA': row['Call Classification'],
        'Call Value': row['Call Value'],
        'Original Call Value': row['Original Call Value'],
        'Call Price': row['Call Price'],
        'Last CDRQ Status': row['Last CDRQ Status']
    }
    print(payload)
    response = requests.post(universalURL, headers=header)
    if response.status_code != 200:
        failData.append({'Row', row['Call SID'], 'Failure', response.text})
    else:
        goodData.append({'Row', row['Call SID'], 'Success', 'Joel Rocks'})

if len(goodData):
    pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
if len(failData):
    pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)
