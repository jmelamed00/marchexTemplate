from subRoutines import *
import pandas as pd
print('Can you see me?')
start_time = str(datetime.today().strftime('%H-%M-%S'))
args = processArguments()
header = {'Accept': 'text/plain', 'Content-Type': 'application/json', 'x-organization-token': args['token'], 'subscription-key': args['key']}

# Collect all Marketing Edge Entities from APIs
entities = useThreadsToCollectEntities(header)
print('All Entities collected.')

# Read data from a file that lives in the same directory as this code.
inputFile = pd.read_excel(r'testingJM2.xlsx', sheet_name='Sheet1')

# URLs to delete a number. Both require IDs appended.
numberURL = 'https://edgeapi.marchex.io/marketingedge/v5/api/numbers/'
poolURL = 'https://edgeapi.marchex.io/marketingedge/v5/api/numberpools/'
groupURL = 'https://edgeapi.marchex.io/marketingedge/v5/api/Groups/'

# Setup output storage
goodData = []
failData = []

# Read in each row from the file.
for index, row in inputFile.iterrows():
    ctn = str(row['ctn'])
    param_name = str(row['dni_type'])
    dni_type = 'static'
    if param_name[0].lower() == 'd':
        dni_type = 'dni'

    # Use the CTN from the file to find the data required to delete the CTN: ctnID for static and poolID for DNI
    ctnID = -1
    poolID = -1
    if dni_type == 'static':
        for number in entities['numbers']:
            if ctn == number.phone_number:
                ctnID = number.id
                break
    else:
        for pool in entities['numberpools']:
            for number in pool:
                if ctn == number.phone_number:
                    ctnID = number.id
                    poolID = pool.id

    if ctnID == -1:
        failData.append({'CTN': ctn})
        continue

    if dni_type == 'static':
        response = requests.delete(numberURL + str(ctnID), headers=header)
    else:
        response = requests.delete(poolURL + str(poolID) + '/numbers/' + str(ctnID), headers=header)
    if response.status_code != 200:
        failData.append({'CTN': ctn, 'Failure Response': str(response.text)})
    else:
        goodData.append({'CTN': ctn})

pd.DataFrame(goodData).to_excel('GoodResults_start_' + start_time + '.xlsx', index=False)
pd.DataFrame(failData).to_excel('FailResults_start_' + start_time + '.xlsx', index=False)

for group in entities['Groups']:
    if group.dni_type == 'None':
        response = requests.get(groupURL + str(group.id) + '/numbers', headers=header)
    else:
        response = requests.get(groupURL + str(group.id) + '/numberpools', headers=header)
