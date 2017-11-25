from sheets import *
from IPython import embed
#from graphics import *

def main():

    so = SheetsObj("kitchen.cfg")
    upc = 35200264013
    so.logAppend(upc, 1)
    # append(service, SPREADSHEETID, INVENTORYNAME, CACHENAME, CACHEID, upc)

    """
    #This will read a range
    rangeName = INVENTORY+'!A2:B2'
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEETID, range=rangeName).execute()
    values = result.get('values', [])



    from IPython import embed; embed()

    """

    """
    win = GraphWin("Kitchen Pi", 320, 200)
    e = Entry(Point(100,50), 14)
    e.draw(win)
    while True:
        win.getKey()
        text = e.getText()
        if len(text) >= 12:
            result1 = service.spreadsheets().get(
                spreadsheetId=SPREADSHEETID, ranges=INVENTORY).execute()
            gridProperties = result1[u'sheets'][0][u'properties'][u'gridProperties']
            num_rows = gridProperties[u'rowCount']
            values = [
                        [text,"=VLOOKUP(TEXT(A"+str(num_rows+1)+", \"00000000000000\"), UPC!B:E, 4, TRUE)"
                        ],
                            # Additional rows ...
                    ]

            body = {
                      'values': values
                      }
            result2 = service.spreadsheets().values().append(
                    spreadsheetId=SPREADSHEETID, range=INVENTORY,
                    valueInputOption="USER_ENTERED", body=body).execute()
            e.setText("")
    win.getMouse() # Pause to view result
    win.close()    # Close window when done
    """

if __name__ == '__main__':
    main()
