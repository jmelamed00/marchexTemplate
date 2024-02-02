from subRoutines import *
import pandas as pd

start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}

# Collect all Marketing Edge Entities from APIs
entities = useThreadsToCollectEntities(header)
print('All Entities collected.')

# Read data from a file that lives in the same directory as this code.
inputFile = pd.read_excel(r'testingJM1.xlsx', sheet_name='Campaigns')

# URLs to delete a number. Both require IDs appended.
numberURL = 'https://edgeapi.marchex.io/marketingedge/v5/api/numbers/'
groupURL = 'https://edgeapi.marchex.io/marketingedge/v5/api/Groups/'

# Setup output storage
goodData = []
failData = []

# Read in each row from the file.
# Find the existing Channel Campaign by matching the name from the File.
# Read in columns T - X. If any of those are "Yes"....
# For each of those columns that are yes:
# Create a common payload.
# Specify the number name and rewrite rules from the PG.
# Create each number in the existing campaign.
# QED

# Read in each row from the file.
for index, row in inputFile.iterrows():
    DM = True if str(row['DM']) == 'Yes' else False
    EM = True if str(row['EM']) == 'Yes' else False
    SM = True if str(row['SM']) == 'Yes' else False
    DMS = True if str(row['DMS']) == 'Yes' else False
    LP = True if str(row['Website / LP']) == 'Yes' else False

    foundGroup = False
    for group in entities['Groups']:
        if group['name'] == row['Campaign Name']:
            foundGroup = True
            break

    if not foundGroup:
        failData.append({'Campaign Name': row['Campaign Name'], 'Could not find this group: ': row['Campaign Name']})
        continue

    payload = {
        "replacement_configuration": {
            "replace_all_numbers": True,
            "tracking_sources": [
                {
                    "referrer_domain": "Any",
                    "url_triggers": [],
                    "page_trigger_operator": "AND"
                }
            ]
        },
        "phone_number_request": {
            "number_type": "Standard",
            "match_type": "LocalToNumber",
            "local_to_number": row['termination_number']
        },
        "sms_routes": {"route_type": "None"},
        "call_routes": {
            "route_type": "Basic",
            "route": {
                "termination_number": row['termination_number'],
                "default": "True",
                "features": {
                    "call_record": {
                        "enabled": row['Call Recording'],
                        "record": row['Call Recording Notification'],
                        # "notification_file": row['Call Recording Notification File'],
                        "notification_file": "",
                        "redaction_enabled": row['PCI_Redacation'],
                        "call_summary_enabled": True,
                        "transcription_settings": {
                            "transcript_enabled": row['transcript_enabled'],
                            "call_scoring_enabled": True
                        }
                    }
                }
            }
        }
    }
    if DM:
        payload['name'] = "DM"
        payload['replacement_configuration']['tracking_sources'][0]['page_variable_triggers'] = ["page_var_source=epsilon", "page_var_medium=DM"]
        response = requests.post(groupURL + str(group['id']) + '/numbers', data=json.dumps(payload), headers=header)
        if response.status_code != 200:
            failData.append({'Campaign Name: ': row['Campaign Name'], 'Channel': 'DM', 'Reason': response.text})
        else:
            goodData.append({'Campaign Name: ': row['Campaign Name'], 'Success': 'DM'})
    if EM:
        payload['name'] = "EM"
        payload['replacement_configuration']['tracking_sources'][0]['page_variable_triggers'] = ["page_var_source=epsilon", "page_var_medium=EM"]
        response = requests.post(groupURL + str(group['id']) + '/numbers', data=payload, headers=header)
        if response.status_code != 200:
            failData.append({'Campaign Name: ': row['Campaign Name'], 'Channel': 'EM', 'Reason': response.text})
        else:
            goodData.append({'Campaign Name: ': row['Campaign Name'], 'Success': 'EM'})
    if SM:
        payload["name"] = "SM"
        payload["replacement_configuration"]["tracking_sources"][0]["page_variable_triggers"] = ["page_var_source=epsilon", "page_var_medium=SM"]
        print(payload)
        response = requests.post(groupURL + str(group['id']) + '/numbers', data=json.dumps(payload), headers=header)
        if response.status_code != 200:
            failData.append({'Campaign Name: ': row['Campaign Name'], 'Channel': 'SM', 'Reason': response.text})
        else:
            goodData.append({'Campaign Name: ': row['Campaign Name'], 'Success': 'SM'})
    if DMS:
        payload["name"] = "DMS"
        payload["replacement_configuration"]["tracking_sources"][0]["page_variable_triggers"] = ["page_var_source=epsilon", "page_var_medium=DMS"]
        response = requests.post(groupURL + str(group['id']) + '/numbers', data=json.dumps(payload), headers=header)
        if response.status_code != 200:
            failData.append({'Campaign Name: ': row['Campaign Name'], 'Channel': 'DMS', 'Reason': response.text})
        else:
            goodData.append({'Campaign Name: ': row['Campaign Name'], 'Success': 'DMS'})
    if LP:
        payload["name"] = "LP"
        payload["replacement_configuration"]["tracking_sources"][0]["page_variable_triggers"] = ["page_var_source=epsilon", "page_var_medium=LP"]
        response = requests.post(groupURL + str(group['id']) + '/numbers', data=json.dumps(payload), headers=header)
        if response.status_code != 200:
            failData.append({'Campaign Name: ': row['Campaign Name'], 'Channel': 'LP', 'Reason': response.text})
        else:
            goodData.append({'Campaign Name: ': row['Campaign Name'], 'Success': 'LP'})

pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)
