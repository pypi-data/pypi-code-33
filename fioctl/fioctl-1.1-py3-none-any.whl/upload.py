import concurrent.futures
import click

def upload(asset, file):
    return FrameioUploader(asset, file).upload()

class FrameioUploader(object):
  def __init__(self, asset, file):
    self.asset = asset
    self.file = file

  def _read_chunk(self, file, size):
    while True:
      data = file.read(size)
      if not data:
        break
      yield data

  def _upload_chunk(self, url, chunk):
    return requests.put(url, data=chunk, headers={
      'content-type': self.asset['filetype'],
      'x-amz-acl': 'private'
    })

  def upload(self):
    procs = []
    
    upload_urls     = self.asset['upload_urls']
    chunks          = len(upload_urls)
    chunks_uploaded = 0

    total_size = self.asset['filesize']
    size       = int(math.ceil(total_size / len(upload_urls)))

    def handle_chunk(pair):
        i, chunk = pair
        return self._upload_chunk(upload_urls[i], chunk)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for _ in executor.map(handle_chunk, enumerate(self._read_chunk(self.file, size))):
            chunks_uploaded += 1
            click.echo(f"Uploaded chunk {chunks_uploaded} of {chunks} for {self.asset['name']}")