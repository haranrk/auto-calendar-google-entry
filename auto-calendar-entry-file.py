from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import argparse as ap
import datetime
import os

SCOPES = 'https://www.googleapis.com/auth/calendar'

#1330 - today 1:30 PM
#y1330 - yesterday 1:30 PM
#09241330 - 09/24 1:30 PM
def parse_datecode(datecode, duration):
    today = datetime.datetime.now()

    if(datecode=='now'):
        start_date = today
    else:
        minutes = int(datecode[-2:])
        hours = int(datecode[-4:-2])
        start_date = datetime.datetime(today.year, today.month, today.day, hours, minutes)
        if(len(datecode)!=4):
            if (datecode[0]=='y'):
                start_date = start_date - datetime.timedelta(days=1)
    
    if(duration[-1]=='h'):
        end_date = start_date + datetime.timedelta(hours=int(duration[:-1]))
    elif(duration[-1]=='d'):
        end_date = datetime.datetime(start_date.year, start_date.month, start_date.day, int(duration[-5:-3]), int(duration[-3:-1]))
    else:
        end_date = start_date + datetime.timedelta(minutes=int(duration))
    timezone_offset = '+05:30'
    return start_date.isoformat()+timezone_offset , end_date.isoformat()+timezone_offset
        

if __name__ == '__main__':
    store = file.Storage(os.path.join(os.path.dirname(__file__), 'token.json'))
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(os.path.dirname(__file__), 'credentials.json'), SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    
    parser = ap.ArgumentParser()
    parser.add_argument('summary', type=str)
    parser.add_argument('start_time',type=str)
    parser.add_argument('duration', type=str)
    parser.add_argument('-d', '--description', type=str,help="Optional event description")


    args = parser.parse_args()
    dates = parse_datecode(args.start_time,args.duration)
    new_event = {}
    new_event["summary"] = args.summary
    if args.description:
        new_event['description'] = args.description
    new_event['start'] = {'dateTime':  dates[0]}
    new_event['end'] = {'dateTime':  dates[1]}
    created_event = service.events().insert(calendarId='primary', body=new_event).execute()
    print(f"Created event {created_event['summary']} starting at {created_event['start']['dateTime']} and ending at {created_event['end']['dateTime']}")
    if args.description:
        print(f"Description: {created_event['description']}")





    
