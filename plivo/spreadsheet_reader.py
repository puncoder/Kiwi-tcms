# https://developers.google.com/sheets/api/quickstart/python

from __future__ import print_function
import os
import gspread
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

flags = tools.argparser.parse_args([])


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
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


def parse_spreadsheet(spreadsheet_id):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    print('Reading spreadsheet.')
    credentials = get_credentials()
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(spreadsheet_id)
    title = sh.title
    data_dict = {}
    print(title)

    for sheet in sh.worksheets():
        values = sheet.get_all_values()
        plan = title
        if not values:
            raise Exception('No data found.')
        else:
            values = values[1:]
            for row in values:
                test_case = ''
                note = ''
                exp_output = ''
                status = 'idle'

                if not row:
                    continue

                try:
                    if row[0]:
                        plan = row[0]
                    if plan not in data_dict:
                        data_dict[plan] = {}
                    data = row[1:]
                    if not data[0]:
                        continue

                    test_case = data[0]
                    note = data[1]
                    exp_output = data[2]
                    status = (data[3] or status)

                except IndexError:
                    pass

                data_dict[plan][test_case] = {}
                data_dict[plan][test_case]['note'] = note
                data_dict[plan][test_case]['exp_output'] = exp_output
                data_dict[plan][test_case]['status'] = status
    print(data_dict,title)
    return data_dict, title


if __name__ == '__main__':
    spreadsheet_Id = 'SpreadSheetId'
    spreadsheet_data = parse_spreadsheet(spreadsheet_Id)
