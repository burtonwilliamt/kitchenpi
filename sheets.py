from __future__ import print_function
import httplib2
import os

from urlparse import urlparse
import json

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import pickle
from IPython import embed

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def tagRow(service, SPREADSHEETID, GRIDID, rowId, tag):
    result2 = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEETID, body={
    "responseIncludeGridData": False,
    "requests": [{
    "createDeveloperMetadata": {
          "developerMetadata": {
            "metadataValue": "UPC",
            "metadataKey": str(tag),
            "location": {
              "dimensionRange": { 
                "startIndex": rowId,
                "endIndex": rowId+1,
                "sheetId": GRIDID, 
                "dimension": "ROWS",
              },
            },
            "visibility": "DOCUMENT",
          },
        },
        }]
    }).execute()

def getRowByTag(service, SPREADSHEETID, tag):
    result = service.spreadsheets().values().batchGetByDataFilter(
        spreadsheetId=SPREADSHEETID, body={
    "dataFilters": [{
        "developerMetadataLookup": {
            "metadataValue":"UPC",
            "metadataKey":"{:012d}".format(tag),
        },
    }]
    }).execute()
    return result.get('valueRanges', [])

def formatRow(data):
    i = data[u'items'][0]
    image = u''
    if len(i[u'images']) > 0:
        image = i[u'images'][0]
    return [i[u'upc'], i[u'title'], i[u'brand'], image, i[u'highest_recorded_price'], i[u'lowest_recorded_price'], i[u'description']]

def lookupNewUPC(service, SPREADSHEETID, CACHE, CACHEID, upc):
    return [upc, 'title', 'brand', 'image', 'high price', 'low price', 'description']
    """
    headers = {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json',
              }
    ch = httplib2.Http()
    lookup = urlparse('https://api.upcitemdb.com/prod/trial/lookup?upc='+str("{:012d}".format(upc)))
    resp, content = ch.request(lookup.geturl(), 'GET', '', headers)
    print("Requests remaining: {}".format(resp['x-ratelimit-remaining']))
    data = json.loads(content)
    body = {
              'values': [[upc, pickle.dumps(data)]]
            }
    result3 = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEETID, range=CACHE,
            valueInputOption="USER_ENTERED", body=body).execute()
    rowNum = int(result3[u'updates'][u'updatedRange'].split('!A')[1].split(':')[0])
    rowID = rowNum-1
    tagRow(service, SPREADSHEETID, CACHEID, rowID, "{:012d}".format(upc))
    return formatRow(data)
    """

def append(service, SPREADSHEETID, INVENTORY, CACHE, CACHEID, upc):
    result1 = service.spreadsheets().get(
        spreadsheetId=SPREADSHEETID, ranges=CACHE).execute()
    gridProperties = result1[u'sheets'][0][u'properties'][u'gridProperties']
    #num_rows = gridProperties[u'rowCount']
    result2 = getRowByTag(service, SPREADSHEETID, upc)

    body = {}
    if len(result2) > 0:
        print("I'm using a cached UPC")
        data = pickle.loads(result2[0]['valueRange']['values'][0][1])
        body = {
                  'values': [formatRow(data)]
                }
    else:
        print("I'm fetching a new UPC")
        body = {
                  'values': [lookupNewUPC(service, SPREADSHEETID, CACHE, CACHEID, upc)]
                }

    result4 = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEETID, range=INVENTORY,
            valueInputOption="USER_ENTERED", body=body).execute()

def popRow(service, SPREADSHEETID, QUEUENAME, QUEUEID):
    rangeName = QUEUENAME+'!A1'

    import time
    start = time.time()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEETID, range=rangeName).execute()
    values = result.get('values', [])

    middle = time.time()

    body = {
             "requests": [
                 { "deleteDimension": {
                        "range": {
                            "sheetId": QUEUEID,
                            "dimension": "ROWS",
                            "startIndex": 0,
                            "endIndex": 1
                        }
                }},
             ],
             "includeSpreadsheetInResponse": True,
             "responseIncludeGridData": False,
            }

    service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEETID, body=body).execute()
    end = time.time()

    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEETID, range=rangeName).execute()
    r = result.get('values', [])
    end2 = time.time()
    from IPython import embed; embed()
    return values

def getService():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service
"""
#This will read a range
rangeName = INVENTORY+'!A2:B2'
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEETID, range=rangeName).execute()
values = result.get('values', [])
"""
