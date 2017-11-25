from __future__ import print_function
import httplib2
import os

from urlparse import urlparse
import json

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import ConfigParser
import pickle
import time
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

def getService():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service

class SheetsObj:
    """
    SheetsObj:
        Member Variables:
            SheetIDString
            LogName
            LogID
            QueueName
            QueueID
            CacheName
            CacheID
            service

        Methods:
            bool cacheContains(x)
            bool queueIsEmpty()
            int  queuePeak()
            void logAppend(x, action)
            void queueAppend(x)
            void cacheAppend(x, content)
            void queuePop()

        NOT NEEDED:
            content cacheLookup(x)

        Helpers:
            result appendRow(row, gridName)
    """
    def __init__(self, configFile):
        config = ConfigParser.RawConfigParser()
        config.read('kitchen.cfg')

        self.SPREADSHEETID = config.get('General', 'spreadsheet_id')
        self.LOGNAME = config.get('General', 'log_sheet_name')
        self.LOGID = config.getint('General', 'log_grid_id')
        self.CACHENAME = config.get('General', 'cache_sheet_name')
        self.CACHEID = config.getint('General', 'cache_grid_id')
        self.QUEUENAME = config.get('General', 'queue_sheet_name')
        self.QUEUEID = config.getint('General', 'queue_grid_id')

        self.service = getService()

    def _appendRows(self, rows, gridName):
        """Append an array of rows to the end of a sheet

        While used mostly for individual rows, this can append more than one
        row at a time to support batch operations.

        Args:
            rows     ([[]]):    A list containing all of the rows, where each row 
                                    is itself a list of row elements.
            gridName (str):     The name of the grid that these rows will be
                                    appended to

        Returns:
            result: The result of the api call

        """
        body = {
                  'values': rows
                }
        result = self.service.spreadsheets().values().append(
                spreadsheetId=self.SPREADSHEETID, range=gridName,
                valueInputOption="USER_ENTERED", body=body).execute()
        return result

    def _deleteRows(self, startIndex, endIndex, gridID):
        """Delete some set of continuous rows

        While used mostly for individual rows, this can delete more than one
        row at a time to support batch operations. Also important to note: sheets
        are 0 indexed for ID, but are 1 indexed in the gui and ranges. Another
        note: startIndex is inclusive, and endIndex is exclusive

        Args:
            startIndex  (int):  The starting index of the rows to be deleted 
                                    inclusive and zero-indexed
            endIndex    (int):  The end index of the rows to be deleted 
                                    exclusive and zero-indexed
            gridID      (int):  The ID of the grid that these rows will be 
                                    deleted from

        Returns:
            result: The result of the api call

        """
        body = {
                 "requests": [
                     { "deleteDimension": {
                            "range": {
                                "sheetId": gridID,
                                "dimension": "ROWS",
                                "startIndex": startIndex,
                                "endIndex": endIndex,
                            }
                    }},
                 ],
                 "includeSpreadsheetInResponse": False,
                 "responseIncludeGridData": False,
                }

        result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.SPREADSHEETID, body=body).execute()
        return result

    def cacheContains(self, upc):
        return self.cacheLookup(upc) != None

    def cacheAppend(self, upc, content):
        result1 = self._appendRows([[upc, pickle.dumps(content)]], self.CACHENAME)
        rowNum = int(result1[u'updates'][u'updatedRange'].split('!A')[1].split(':')[0])
        rowID = rowNum-1

        result2 = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.SPREADSHEETID, body={
                "responseIncludeGridData": False,
                "requests": [{
                    "createDeveloperMetadata": {
                        "developerMetadata": {
                            "metadataValue": "UPC",
                            "metadataKey": "{:012d}".format(upc),
                            "location": {
                                "dimensionRange": { 
                                    "startIndex": rowID,
                                    "endIndex": rowID+1,
                                    "sheetId": self.CACHEID,
                                    "dimension": "ROWS",
                                },
                            },
                            "visibility": "DOCUMENT",
                        },
                    },
                }]
            }).execute()
        return

    def cacheLookup(self, upc):
        result = self.service.spreadsheets().values().batchGetByDataFilter(
            spreadsheetId=self.SPREADSHEETID,
            body={
                "dataFilters": [{
                    "developerMetadataLookup": {
                        "metadataValue":"UPC",
                        "metadataKey":"{:012d}".format(upc),
                    },
                }]
            }
        ).execute()
        test = result.get('valueRanges', None)
        if test != None:
            return test[0]['valueRange']['values'][0]
        else:
            return None

    def queueIsEmpty(self):
        sheetData = self.service.spreadsheets().get(
            spreadsheetId=self.SPREADSHEETID, ranges=self.QUEUENAME).execute()
        gridProperties = sheetData[u'sheets'][0][u'properties'][u'gridProperties']
        num_rows = gridProperties[u'rowCount']
        return num_rows < 2

    def queuePeak(self):
        result = self.service.spreadsheets().values().get(
                spreadsheetId=self.SPREADSHEETID, range=self.QUEUENAME+'!A1:A2').execute()
        if len(result['values']) >= 2:
            return result['values'][1][0]
        return None

    def queueAppend(self, upc):
        return self._appendRows([[str(upc)],], self.QUEUENAME)

    def queuePop(self):
        self._deleteRows(1, 2, self.QUEUEID)
        return None

    def logAppend(self, upc, action):
        self._appendRows([[str(upc), action, time.time(),],], self.LOGNAME)
        return


