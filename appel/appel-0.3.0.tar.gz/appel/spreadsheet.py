from collections import OrderedDict
from collections import defaultdict

from googleapiclient.discovery import build

from .models import Attendance
from pydrive.drive import GoogleDrive
from dateutil import parser
from datetime import datetime, timedelta

DATE_FORMAT = "%m"
RANGE_CELLS = '!A2:D'
IGNORE_SHEETS = {"INSTRUCTIONS"}
LOGIN_COL = 2
NOTES_COL = 3

requestTimes = []
REQUEST_CAP_COUNT = 50
REQUEST_CAP_TIME = timedelta(seconds=100)

def parseAllSpreadsheets(directory_id, gauth, users):
    userdict = {x.login: x for x in users}
    attendance = defaultdict(OrderedDict)

    drive = GoogleDrive(gauth)
    service = build('sheets', 'v4', http=gauth.http)

    spreadsheet_list = drive.ListFile({'q': "'%s' in parents and mimeType = 'application/vnd.google-apps.spreadsheet'" % directory_id}).GetList()
    requestTimes.append(datetime.now())
    for ss in spreadsheet_list:
        title = ss['title']
        date = parser.parse(title, ignoretz=True, dayfirst=False).date()

        user_attendance_map = _parseSpreadsheet(service, ss['id'], date)
        for user in users:
            if user.login in user_attendance_map:
                attendance[user][date] = user_attendance_map[user.login]
            else:
                attendance[user][date] = None

    return attendance

def parseSingleSpreadsheet(spreadsheet_id, gauth, users):
    drive = GoogleDrive(gauth)
    service = build('sheets', 'v4', http=gauth.http)

    date_str = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()['properties']['title']
    requestTimes.append(datetime.now())
    date = parser.parse(date_str, ignoretz=True, dayfirst=False).date()

    attendance = {}
    user_attendance_map = _parseSpreadsheet(service, spreadsheet_id, date)

    for user in users:
        if user.login in user_attendance_map:
            attendance[user] = user_attendance_map[user.login]
        else:
            attendance[user] = None

    return attendance

def _parseSpreadsheet(service, spreadsheet_id, date):
    print("Processing %s" % date)

    result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    requestTimes.append(datetime.now())

    sheets = [x['properties']['title'] for x in result['sheets']]
    attendance = {}
    for sheet in sheets:
        if sheet not in IGNORE_SHEETS:
            attendance.update(_parseSheet(service, spreadsheet_id, sheet, date))

    return attendance

def _parseSheet(service, spreadsheet_id, sheet_name, date):
    global requestTimes
    range = sheet_name + RANGE_CELLS

    rateLimit = False
    while True:
        now = datetime.now()
        requestTimes = [x for x in requestTimes if now - x <= REQUEST_CAP_TIME]

        if len(requestTimes) < REQUEST_CAP_COUNT:
            break
        else:
            if not rateLimit:
                print("Waiting for rate-limit (100 requests per 100 seconds).")
            rateLimit = True

    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range).execute()
    requestTimes.append(datetime.now())

    values = result.get('values', [])

    attendance = {}
    for row in values:
        if len(row) <= LOGIN_COL:
            continue

        login = row[LOGIN_COL]

        if login is None or len(login) == 0:
            continue

        notes = ""
        if len(row) > NOTES_COL:
            notes = row[NOTES_COL]

        timestamp = None
        try:
            timestamp = parser.parse(notes, fuzzy=True)
        except:
            pass

        attendance[login] = Attendance(sheet_name, date, notes, timestamp)

    return attendance
