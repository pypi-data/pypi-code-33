import os
import io
import sys
import zipfile
import pathlib
import requests
import pandas as pd
from . db import Base, Subject, Url, Path, PathType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def save_zip(content, save_dir):
    with zipfile.ZipFile(file=io.BytesIO(content)) as zip:
        zip.extractall(save_dir)


def check_dir(save_dir):
    if not os.path.exists(save_dir):
        pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)


def get_header(url, save_dir, file):
    req = requests.get(url)
    html = pd.read_html(req.content)
    df = html[0].transpose().iloc[:1, 1:]
    df.to_csv(path_or_buf=os.path.join(save_dir, file), index=False, header=False, sep='|')


def print_to_shell(message):
    print(message)
    sys.stdout.flush()


# QUERIES
class GetSubject:
    @classmethod
    def go(cls, session, query_param):
        return session.query(Subject).filter(Subject.subject_name == query_param).first()


class GetPath:
    @classmethod
    def go(cls, session, query_param):
        return session.query(Path, Url)\
            .join('subject').join('url').join('path_type')\
            .filter(Path.subject == query_param, PathType.path_type == 'file')\
            .all()


class GetHeaderPath:
    @classmethod
    def go(cls, session, query_param):
        return session.query(Path, Url, PathType)\
            .join('subject').join('url').join('path_type')\
            .filter(Path.subject == query_param, PathType.path_type == 'header')\
            .first()


def db_retrieve(db_engine, query, query_param):

    engine = create_engine(db_engine)
    Base.metadata.bind = engine
    db_session = sessionmaker()
    db_session.bind = engine
    session = db_session()

    try:
        output = query().go(session, query_param)
        return output
    except:
        session.rollback()
        raise
    finally:
        session.close()
