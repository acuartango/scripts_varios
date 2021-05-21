from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pyasn1_modules.rfc2459 import Extension, ExtensionAttribute
from apiclient import errors
import sys, getopt



# If modifying these scopes, delete the file token.json.
#SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly','https://www.googleapis.com/auth/drive']

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def main(argv):
    print()

    listfile=''
    trash=False

    try:
      opts, args = getopt.getopt(argv,"hl:t:",["list","trash"])
    except getopt.GetoptError:
      print ('test.py --list <filename>')
      print ('test.py --list "mytext PDF"')
      print ('test.py --list "mytext PDF" --trash')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print ('test.py --list <filename>')
         sys.exit()
      elif opt in ('-l', '--list'):
         listfile = arg
      elif opt in ('-t', '--trash'):
         trash = True


    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    deleteNumberFiles=100
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    comodines=listfile.split()
    q_contains="name contains '{}'".format(comodines.pop())
    if len(comodines)>=1:
        for bunch in comodines:
            q_contains=q_contains + " and name contains '{}' ".format(bunch)

    #print("q_contains={}".format(q_contains))

    # Call the Drive v3 API
    results = service.files().list(
#        q="mimeType='image/jpeg'",
#        q="name contains '.NEF' and name contains 'DSC'",
        q=q_contains,
##        pageSize=deleteNumberFiles, 
        fields="nextPageToken, files(id, name, size, modifiedTime)").execute()

    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        for item in items:
            print(item)
            if "size" in item:
                print('{0}  {2}  {3}  ID=({1})'.format(item['name'], item['id'], human_readable_size(int(item['size'])), item['modifiedTime'][0:10]))
            print()

            if trash:
                try:
                    print("Moviendo a la papelera: {}".format(item['name']))
                    print()
                    body = {'trashed': True}
                    service.files().update(fileId=item['id'], body=body).execute()
#### DELETE!                service.files().delete(fileId=item['id']).execute()
                except ValueError:
                    print ('An error occurred: ' + ValueError)
            

if __name__ == '__main__':
    main(sys.argv[1:])
