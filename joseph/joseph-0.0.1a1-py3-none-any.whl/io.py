from pathlib import Path

import jpxtime3
import numpy as np
import pandas as pd
import xarray as xr


joseph_home = Path.home() / ".joseph"
joseph_cache = joseph_home / "cache"

if not joseph_home.exists():
    joseph_home.mkdir()
if not joseph_cache.exists():
    joseph_cache.mkdir()


def make_file_path_jpx(ds):
    try:
        t0 = ds["t0"].values[-1]
    except IndexError:
        t0 = ds["t0"].values
    
    dt = jpxtime3.get_nominal_trading_day(pd.to_datetime(t0))
    file_name = f"{dt:%Y%d%m}.nc"
    return joseph_cache / file_name


def serialize_to_netcdf(ds):
    file_path = make_file_path_jpx(ds)
    ds["t0"] = ds["t0"].astype(int) / 1e9

    if file_path.exists():
        ext_ds = xr.open_dataset(str(file_path))
        ext_t0 = ext_ds["t0"].values
        if isinstance(ext_t0, np.datetime64):
            ext_t0 = np.array(ext_t0)
        diff = np.setdiff1d(ds["t0"].values, ext_ds["t0"].values)
        if len(diff) == 0:
            return
        if len(diff) == 1:
            new_ds = xr.concat([ext_ds, ds], dim="t0")
        else:
            new_ds = xr.concat([ext_ds, ds.sel(t0=diff)], dim="t0")
        new_ds.to_netcdf(str(file_path))
    else:
        ds.to_netcdf(str(file_path))
