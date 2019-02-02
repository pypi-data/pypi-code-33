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


  def get(self, sep=', ', delimiter=None, header='infer', names=None, index_col=0, usecols=None, squeeze=False, prefix=None, mangle_dupe_cols=True, dtype=None, engine=None, converters=None, true_values=None, false_values=None, skipinitialspace=False, skiprows=None, skipfooter=0, nrows=None, na_values=None, keep_default_na=True, na_filter=True, verbose=False, skip_blank_lines=True, parse_dates=False, infer_datetime_format=False, keep_date_col=False, date_parser=None, dayfirst=False):
    self.download_path = os.path.expanduser('~/data')
    try:
        os.makedirs(self.download_path)
    except FileExistsError:
        pass
    TOC_imported_data = os.path.join(self.download_path, self.title)
    self.file = self.drive.CreateFile({'id': self.id})
    self.file.GetContentFile(TOC_imported_data)
    self.df = pd.read_csv(TOC_imported_data, sep, delimiter, header, names, index_col, usecols, squeeze, prefix, mangle_dupe_cols, dtype, engine, converters, true_values,
     false_values, skipinitialspace, skiprows, skipfooter, nrows, na_values, keep_default_na, na_filter, verbose, skip_blank_lines, parse_dates, infer_datetime_format,
      keep_date_col, date_parser, dayfirst)

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
              file_id = False, sep=', ', delimiter=None, header='infer', names=None, index_col=0, usecols=None, squeeze=False, prefix=None, mangle_dupe_cols=True, dtype=None, engine=None, converters=None, true_values=None, false_values=None, skipinitialspace=False, skiprows=None, skipfooter=0, nrows=None, na_values=None, keep_default_na=True, na_filter=True, verbose=False, skip_blank_lines=True, parse_dates=False, infer_datetime_format=False, keep_date_col=False, date_parser=None, dayfirst=False):

    if(filename==False):
      filename = self.df.loc[self.df.index.max()]['file_name']

    if(file_id==False):
      file_id = self.df.loc[self.df.index.max()]['file_id']
    imported_data = os.path.join(self.download_path, filename)
    temp_file = self.drive.CreateFile({'id': file_id})
    temp_file.GetContentFile(imported_data)
    self.last = pd.read_csv(imported_data, sep, delimiter, header, names, index_col, usecols, squeeze, prefix, mangle_dupe_cols, dtype, engine, converters, true_values,
     false_values, skipinitialspace, skiprows, skipfooter, nrows, na_values, keep_default_na, na_filter, verbose, skip_blank_lines, parse_dates, infer_datetime_format,
      keep_date_col, date_parser, dayfirst)
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

def justget(title, idn, sep=', ', delimiter=None, header='infer', names=None, index_col=0, usecols=None, squeeze=False, prefix=None, mangle_dupe_cols=True, dtype=None, engine=None, converters=None, true_values=None, false_values=None, skipinitialspace=False, skiprows=None, skipfooter=0, nrows=None, na_values=None, keep_default_na=True, na_filter=True, verbose=False, skip_blank_lines=True, parse_dates=False, infer_datetime_format=False, keep_date_col=False, date_parser=None, dayfirst=False):
    # if(log):
        # from pydrive.drive import GoogleDrive
        # from pydrive.auth import GoogleAuth
        # from google.colab import auth
        # from oauth2client.client import GoogleCredentials
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)
    # import os
    # from google.colab import files
    # import io
    imported_data = os.path.join(os.path.expanduser('~/data'), title)
    temp_file = drive.CreateFile({'id': idn})
    temp_file.GetContentFile(imported_data)
    return(pd.read_csv(imported_data, sep, delimiter, header, names, index_col, usecols, squeeze, prefix, mangle_dupe_cols, dtype, engine, converters, true_values,
     false_values, skipinitialspace, skiprows, skipfooter, nrows, na_values, keep_default_na, na_filter, verbose, skip_blank_lines, parse_dates, infer_datetime_format,
      keep_date_col, date_parser, dayfirst))
