from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient import discovery
from dataclasses import dataclass

@dataclass
class Project:
    file_id: str
    title: str
    discord_ids: list
    start_date: str
    m_names: list
    m_dates: list
    last_sent: str

@dataclass
class Event:
    time: str
    event: str
    user: str

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)



projects = []
messages = []
log = []
log_id = 0
service = discovery.build('sheets', 'v4', credentials=gauth.credentials)

# View all folders and file in your Google Drive
fileList = drive.ListFile({'q': "'INSERT FOLDER ID HERE' in parents and trashed=false"}).GetList()
for file in fileList:

    #read all project files
    if 'Project' in file['title']:
        
        values = service.spreadsheets().values().get(spreadsheetId=file['id'], range = 'A2:XX',majorDimension='COLUMNS',valueRenderOption='FORMATTED_VALUE').execute().get('values', [])
        ids = service.spreadsheets().values().get(spreadsheetId=file['id'], range = 'B2:BX',majorDimension='COLUMNS',valueRenderOption='UNFORMATTED_VALUE').execute().get('values', [])

        #extract needed data - indices are hard coded to match format of google sheet
        discord_ids = []
        for i in range(0, len(ids[0])):
            discord_ids.append(int((ids[0][i])))

        title = values[0][0]
        start_date = values[2][0]
        m_names = values[3]

        m_dates = []
        for i in range(0, len(values[4])):
            m_dates.append(int(values[4][i]))

        last_sent = values[5][0]
        p = Project(file['id'], title, discord_ids, start_date, m_names, m_dates, last_sent)
        projects.append(p)

    #read message file
    elif file['title'] == 'Messages':
        service = discovery.build('sheets', 'v4', credentials=gauth.credentials)
        values = service.spreadsheets().values().get(spreadsheetId=file['id'], range = 'A1:BX',majorDimension='COLUMNS',valueRenderOption='FORMATTED_VALUE').execute().get('values', [])
        messages = values[1]

    elif file['title'] == 'Log':
        service = discovery.build('sheets', 'v4', credentials=gauth.credentials)
        values = service.spreadsheets().values().get(spreadsheetId=file['id'], range = 'A1:CX',majorDimension='COLUMNS',valueRenderOption='FORMATTED_VALUE').execute().get('values', [])
        log_id = file['id']

        for i in range(0,len(values[0])):
            e = Event(values[0][i], values[1][i], values[2][i])
            log.append(e)

def update_file(project):
    formatted_ids = []
    for i in range(0, len(project.discord_ids)):
        formatted_ids.append(str(project.discord_ids[i]))
    formatted_ids.append('')

    values = [
        [project.title], formatted_ids, [project.start_date], project.m_names, project.m_dates
    ]
      
    request_body = {
        'values' : values,
        'majorDimension' : 'COLUMNS',
    }  

    request = service.spreadsheets().values().update(spreadsheetId=project.file_id, range='A2:XX', valueInputOption='RAW', body=request_body)
    response = request.execute()

def update_log(log):
    values = [[],[],[]]
    for i in range(0, len(log)):
        values[0].append(log[i].time)
        values[1].append(log[i].event)
        values[2].append(log[i].user)

    request_body = {
        'values' : values,
        'majorDimension' : 'COLUMNS',
    }  

    request = service.spreadsheets().values().update(spreadsheetId=log_id, range='A1:CX', valueInputOption='RAW', body=request_body)
    response = request.execute()

