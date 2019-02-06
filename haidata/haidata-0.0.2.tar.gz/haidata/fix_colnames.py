



import logging
import sys

logging.disable(sys.maxsize)
logger = logging.getLogger(__name__)


def fix_colnames(df, args_dict):
    setting = "TITLE"
    if "CASE" in args_dict.keys():
        setting = str(args_dict["CASE"]).strip().upper()
    filler = "_"
    if "FILLER" in args_dict.keys():
        filler = str(args_dict["FILLER"])

    if setting == "UPPER":
        df = df.rename(columns={c: c.strip().upper().replace(' ', filler) for c in df.columns})
    elif setting == "LOWER":
        df = df.rename(columns={c: c.strip().lower().replace(' ', filler) for c in df.columns})
    elif setting == "TITLE":
        df = df.rename(columns={c: c.strip().title().replace(' ', filler) for c in df.columns})
    elif setting == "CAMEL":
        df = df.rename(columns={c: c.strip().title().replace(' ', '') for c in df.columns})
    else:
        raise ValueError("Unknown CASE {0} in fix_colnames".format(setting))

    return df
