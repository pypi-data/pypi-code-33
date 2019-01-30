from google.colab import drive
import requests, os, zipfile, shutil

__all__ = ["mount", "download_large_file", "unzip", "zip", "openmydrive"]

def mount(path='/content/gdrive'):
    drive.mount(path)

def download_large_file(url, target_path='out.zip'):
  # Download the file if it does not exist
  if not os.path.isfile(target_path):
    response = requests.get(url, stream=True)
    handle = open(target_path, "wb")
    print('Downloading...')
    for chunk in response.iter_content(chunk_size=512):
        if chunk:  # filter out keep-alive new chunks
            handle.write(chunk)
    print('Done!')
  else:
    print('File already exists')

def unzip(zip_path, destination_path='.'):
  with zipfile.ZipFile(zip_path,"r") as zip_ref:
      zip_ref.extractall(destination_path)

def zip(filename, root_dir, extension='zip'):
    shutil.make_archive(filename, extension, root_dir)

def openmydrive():
    try:
        os.chdir("gdrive/My Drive/")
    except:
        print('My Drive folder not found')

