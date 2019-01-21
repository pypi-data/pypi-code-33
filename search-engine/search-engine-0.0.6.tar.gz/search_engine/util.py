
import requests

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36"
}

def get_page(url):
    resp = requests.get(url, stream=True, timeout=10, headers=headers)

    buf = b""
    size = 0
    for chunk in resp.iter_content(chunk_size=1024*100):
        if chunk:
            buf += chunk
            size += 1024*100
        else:
            break
        if size >= 1024 * 1024 * 10:
            break
    text = None
    try:
        text = buf.decode(resp.encoding)
    except:
        try:
            text = buf.decode("utf-8")
        except:
            text = str(buf)

    return text