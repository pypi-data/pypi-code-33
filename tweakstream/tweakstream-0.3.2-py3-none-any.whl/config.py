from pathlib import Path

from appdirs import user_data_dir


save_dir = user_data_dir(appname="tweakstream")
filename = "cookies.pkl"
stored_cookies_path = Path(save_dir) / filename
