from subRoutines import *
import pandas as pd

start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}

# Collect all Marketing Edge Entities from APIs
entities = useThreadsToCollectEntities(header)
print('All Entities collected.')

# URL to access Groups
groupURL = 'https://edgeapi.marchex.io/marketingedge/v5/api/Groups/'
numbersURL = 'https://edgeapi.marchex.io/marketingedge/v5/api/numbers/'

# Hard coded value grabbed from the UI for Kia Service - Aftersales
# snippet_id = '4a692a3e-c6b0-4550-8f99-10d4e2dd2f8e'
# This snippet is from Joel M Demo Org and restricted to Big O domain.
# Nissan snippet id: cecd885958ed41a4b9cd1d10b9167838
# Infinity snippet id: fecc5b5774f1440cacb18c68249339f0
snippet_id = 'fecc5b5774f1440cacb18c68249339f0'
# call_record_notify_file = '51a1de47-681d-4c4e-83f3-4bbf0ca45e6a'
# Setup output storage
goodData = []
failData = []

# Read in each row from the file.
for group in entities['Groups']:

    if group['dni_type'] != 'None' or group['status'] != 'active':
        continue

    # 1. Change group DNI type to Channel
    payload = {'dni_type': 'OneToOne', 'global_snippet_id': snippet_id}
    response = requests.put(groupURL + str(group['id']), json=payload, headers=header)
    if response.status_code != 200:
        failData.append({'Updating Group DNI': group['name'], 'Failure Reason': response.text})
        continue

    # 2. Grab all numbers associated with the group. There should be just the one when I do this for real.
    response = requests.get(groupURL + str(group['id']) + '/numbers', headers=header)
    if response.status_code != 200:
        failData.append({'Getting Groups Numbers': group['name'], 'Failure Reason': response.text})
        continue
    numbers = json.loads(response.text)
    if len(numbers) > 1:
        failData.append({'Group': group['name'], 'Has too many numbers': len(numbers)})

    # 3. Use each static number to create a channel number in the new group. Then delete the static number from the old group.
    for number in numbers:
        payload = {
            'replacement_configuration': {
                'numbers_to_replace': [number['call_routes']['route']['termination_number']],
                'tracking_sources': [
                        {
                            'referrer_domain': 'Any',
                            'url_triggers': [],
                            'page_variable_triggers': [
                                'page_var_source=epsilon',
                                'page_var_medium=lp'
                            ],
                            'url_trigger_operator': 'OR',
                            'page_trigger_operator': 'AND'
                        }
                ],
                'replace_all_numbers': 'False'
            }
            # },
            # 'call_routes': {
            #     'route': {
            #         'features': {
            #             'call_record': {
            #                 'enabled': 'True',
            #                 'notification_file': call_record_notify_file,
            #                 'record': 'True',
            #                 'transcription_settings': {
            #                     'transcript_enabled': 'True',
            #                     'call_scoring_enabled': 'True'
            #                 }
            #             }
            #         }
            #     }
            # }
        }
        response = requests.put(numbersURL + '/' + str(number['id']), headers=header, json=payload)
        if response.status_code != 200:
            failData.append({'Group Name': group['name'], 'Update Number Reason': response.text})
            continue
        goodData.append({'Updated Group': group['name'], 'Number Name': number['name']})

if len(goodData):
    pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
if len(failData):
    pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)
