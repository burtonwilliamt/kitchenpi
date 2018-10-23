# kitchenpi
The core concept of this project is to try and log things as they are added or removed from a pantry, using a raspberry pi and a USB barcode reader.

## Vision
Ultimately I want to have a google sheet that logs things as they are added to the pantry when unloading groceries, and logs things as they are finished and thrown out. From this information, you can create a sheet that has the current inventory of your pantry.

This is cool because it means that while in the grocery store, you could look at google sheets on your phone, and see "Do we have X?" Additionaly it allows you to log how much you are consuming of different items. Potentially it might even allow prediction of what items you are about to run out of.

## Google sheets
In this project I chose google sheets as the location to store the log because of the pure convenience. It's really nice to access the state of the pantry remotely, and not have to worry about hosting or a web app. Additionally, this gave me a good reason to learn what the API of google docs is, which is a good project on its own. I relied heavily on the [Python Quickstart](https://developers.google.com/sheets/api/quickstart/python) for google sheets. Further documentation can be found at the [Sheet API documentation page](https://developers.google.com/sheets/api/).

## Implementation
The main goal of the project is to add rows to a google sheet. Each row would have an event type (Add or Remove), the UPC of what's being added or removed, the date of the event, the string version of the product, and any other data that's useful.

Either event type has a very similar workflow.
 1) Read barcode using USB reader to get the UPC
 2) Find the string name of the product
 3) Append a row to the google sheets

### Read barcode
This is by far the easiest part of the project. The USB reader translates barcodes into a number, and "types" it out, as if it were a keyboard. In my case, I simply have this fill a field and scrape the numbers out of the field.

### Find the string name
This is one of the hardest parts of the project. It would be awesome if there was a good, open UPC database. In my research there are some:
 * [https://upcdatabase.com/](https://upcdatabase.com/)
 * [https://upcitemdb.com/](https://upcitemdb.com/)
 * [https://www.upcindex.com/](https://www.upcindex.com/)
 * [http://upcdatabase.org/](http://upcdatabase.org/)
 
Unfortunately, none of these are perfect. Either the database doesn't offer a download, rate limits, or the database is incomplete. It seems like about a quarter of the items in my pantry can't be found by these.

To remedy these problems, I decided to create a "cache" of UPCs. This is essentially building my own database as I request UPCs from other APIs. In my case, the cache is simply another google sheet. To handle rate-limiting services, I decided to create a queue of UPCs that are to be added to the cache, and the kitchenpi should slowly scrape these from the service.

### Appending to google sheets
This part is pretty cut-and-paste from the sheets API examples. I wrapped everything in a function call to abstract it away.

## Help
This project had a lot of work put into it, but I never quite finished it. It would be awesome if someone wanted to contribute, it's like 90% of the way there. It's been a while since I worked on it, so I don't know exactly what I got stuck on.
