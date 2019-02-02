import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
from google.colab import files
import io
import pandas as pd
from datetime import datetime

class Toc:
  def __init__(self, title, idn):

    self.title = title
    self.id = idn
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    self.drive = GoogleDrive(gauth)


  def get(self):
    self.download_path = os.path.expanduser('~/data')
    try:
        os.makedirs(self.download_path)
    except FileExistsError:
        pass
    TOC_imported_data = os.path.join(self.download_path, self.title)
    self.file = self.drive.CreateFile({'id': self.id})
    self.file.GetContentFile(TOC_imported_data)
    self.df = pd.read_csv(TOC_imported_data, index_col = 0)

  def upload(self,df, title = 'df_', filename = False):
    filedate = datetime.now()
    if(filename == False):
      filename = title+filedate.strftime('%Y-%m-%d_%H:%M:%S')+'.txt'
    uploaded = self.drive.CreateFile({'title': filename})
    uploaded.SetContentString(df.to_csv())
    uploaded.Upload()
    file_id = uploaded.get('id')
    file_data = {'file_name':filename,
                 'date':filedate,
                 'file_id':file_id}
    self.df = self.df.append(file_data, ignore_index = True)
    self.file.SetContentString(self.df.to_csv())
    self.file.Upload()
  def getlast(self, filename = False,
              file_id = False):

    if(filename==False):
      filename = self.df.loc[self.df.index.max()]['file_name']

    if(file_id==False):
      file_id = self.df.loc[self.df.index.max()]['file_id']
    imported_data = os.path.join(self.download_path, filename)
    temp_file = self.drive.CreateFile({'id': file_id})
    temp_file.GetContentFile(imported_data)
    self.last = pd.read_csv(imported_data, index_col = 0)
  # def auth(self):
  #   auth.authenticate_user()
  #   gauth = GoogleAuth()
  #   gauth.credentials = GoogleCredentials.get_application_default()
  #   drive = GoogleDrive(gauth)

def maketoc(title):
    # import os
    # from pydrive.auth import GoogleAuth
    # from pydrive.drive import GoogleDrive
    # from google.colab import auth
    # from oauth2client.client import GoogleCredentials
    # from google.colab import files
    # import io

    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    TOC_file = drive.CreateFile({'title':title})
    TOC_file.SetContentString('file_name,date,file_id')
    TOC_file.Upload()
    TOC_id = TOC_file.get('id')
    return(Toc(title, TOC_id))

def justup(df, filename=False, id = False):

    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    if(filename==False):
        filedate = datetime.now()
        filename = 'df_'+filedate.strftime('%Y-%m-%d_%H:%M:%S')+'.txt'
    uploaded = drive.CreateFile({'title': filename})
    uploaded.SetContentString(df.to_csv())
    uploaded.Upload()
    if(id):
        return(uploaded.get('id'))

def justget(title, idn):

    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    imported_data = os.path.join(os.path.expanduser('~/data'), title)
    temp_file = drive.CreateFile({'id': idn})
    temp_file.GetContentFile(imported_data)
    return(pd.read_csv(imported_data, index_col = 0))
