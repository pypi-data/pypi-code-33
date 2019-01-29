import re
import time
from pathlib import Path
from datetime import timedelta
from datetime import datetime as dt
from base64 import urlsafe_b64encode

def create_basepath(path, name):
    now = dt.now()
    date = now.strftime("%Y-%m-%d")
    unixtime = int(time.mktime(now.timetuple()))
    return Path(path) / name / "logs" / date / str(unixtime)

def current_date(delta):
    return (dt.now() + timedelta(days=delta)).strftime("%Y%m%d")

def current_path(basepath, date):
    parent = Path(basepath) / dt.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
    return max(parent.iterdir(), key=lambda x: int(x.stem))

def encode_css_name(css_url):
    id_url = identify_url(css_url)
    return urlsafe_b64encode(id_url.encode("utf-8")).decode("utf-8") + ".css"

def identify_url(url):
    # 数値は日付かバージョンのことが多いので置き換える
    return re.sub(r"\d", "*", url.split("?")[0])