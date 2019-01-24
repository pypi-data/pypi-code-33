
from path import Path
import fantail
from kea3 import kmeta
import collections
from kea3.models import KTransactionIO

@fantail.hook('load_kfile')
def check_archive(app, kfile):
    fn = kfile.filename
    session = app.db_session

    if not fn.endswith(('.tar.bz2', 'tar.gz', 'tar')):
        return

    #only tar for now
    import tarfile


    with tarfile.open(fn, mode='r') as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue

            mname = Path(member.name)
            content = tar.extractfile(member)
            mhash = kmeta.get_khash_filehandle(
                app, content,
                arcdata = dict(name=mname,
                               reference_path=Path(kfile.filename),
                               mtime=member.mtime,
                               size=member.size))

            tract = kmeta.get_transaction('<in archive>', hostname = kfile.hostname,
                                    time_start = kfile.mtime,
                                    time_stop = kfile.mtime,
                                    cwd = Path(kfile.filename).dirname())
            session.add(tract)
            session.add(KTransactionIO(iotype = 'input',
                                       ioname = 'file',
                                       ktransaction = tract,
                                       khash = mhash))
            session.add(KTransactionIO(iotype = 'output',
                                       ioname = 'archive',
                                       ktransaction = tract,
                                       khash = kfile.khash))
