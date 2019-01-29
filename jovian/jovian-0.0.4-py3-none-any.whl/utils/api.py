from requests import get, post
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from os.path import basename
from tqdm import tqdm, tqdm_notebook
from jovian.utils.credentials import read_or_request_key, write_key, CREDS, request_key
from jovian.utils.logger import log
from jovian.utils.jupyter import in_notebook, save_notebook, get_notebook_name
from time import sleep


API_URL = "https://api-staging.jovian.ai"


class ApiError(Exception):
    """Error class for web API related Exceptions"""
    pass


def _u(path):
    """Make a URL from the path"""
    return API_URL + path


def _msg(res):
    try:
        data = res.json()
        if 'errors' in data and len(data['errors'] > 0):
            return data['errors'][0]['message']
        if 'message' in data:
            return data['message']
        if 'msg' in data:
            return data['msg']
    except:
        if res.text:
            return res.text
        return 'Something went wrong'


def _pretty(res):
    """Make a human readable output from an HTML response"""
    return '(HTTP ' + str(res.status_code) + ') ' + _msg(res)


def validate_key(key):
    """Validate the API key by making a request to server"""
    res = get(_u('/user/profile'),
              headers={'Authorization': 'Bearer ' + key})
    if res.status_code == 200:
        return True
    else:
        return False
    raise ApiError(_pretty(res))


def get_key():
    """Retrieve and validate the API Key (from memory, config or user input)"""
    if 'API_KEY' not in CREDS:
        key, source = read_or_request_key()
        if not validate_key(key):
            log('The current API key is invalid or expired.', error=True)
            key, source = request_key(), 'request'
            if not validate_key(key):
                raise ApiError('The API key provided is invalid or expired.')
        write_key(key, source == 'request')
    return CREDS['API_KEY']


def _h():
    """Create authorizaiton header with API key"""
    return {"Authorization": "Bearer " + get_key()}


def _create_callback(encoder):
    """Create a callback to a progress bar for file uploads"""
    if in_notebook():
        pbar = tqdm_notebook(total=encoder.len)
    else:
        pbar = tqdm(total=encoder.len)

    def callback(monitor):
        pbar.update(monitor.bytes_read - pbar.n)
        if (monitor.bytes_read == pbar.total):
            pbar.close()

    return callback


def create_gist():
    """Upload the current notebook to create a gist"""
    if not in_notebook():
        log('Failed to detect Juptyer notebook. Skipping..', error=True)
        return
    save_notebook()
    sleep(1)
    path = get_notebook_name()
    nb_file = (basename(path), open(path, 'rb'))
    encoder = MultipartEncoder({'files': nb_file, 'public': '1'})
    callback = _create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, callback)
    res = post(url=_u('/gist/create'),
               data=monitor,
               headers={**_h(), 'Content-Type': monitor.content_type})
    if res.status_code == 200:
        return res.json()['data']
    raise ApiError('File upload failed: ' + _pretty(res))


def upload_file(gist_slug, file, progress=True):
    """Upload a file and track the progress of the upload"""
    if type(file) == str:
        file = (basename(file), open(file, 'rb'))
    encoder = MultipartEncoder({'files': file})
    callback = _create_callback(encoder) if progress else None
    monitor = MultipartEncoderMonitor(encoder, callback)
    res = post(url=_u('/gist/' + gist_slug + '/upload'),
               data=monitor,
               headers={**_h(), 'Content-Type': monitor.content_type})
    if res.status_code == 200:
        return res.json()['data']
    raise ApiError('File upload failed: ' + _pretty(res))


def get_gist(slug):
    res = get(url=_u('/gist/' + slug))
    if res.status_code == 200:
        return res.json()['data']
    raise ApiError('Failed to retrieve Gist: ' + _pretty(res))
