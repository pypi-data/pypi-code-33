
import logging
import re
import os
from subprocess import check_call, check_output
import tempfile
from textwrap import dedent

import fantail

from kea3 import kmeta, util

lg = logging.getLogger(__name__)

#webdav
k3user = 'u0089478'
k3pass = '6o2EP-Yrisp-LDCgT-WpzBX-WCgq4'
k3url = "https://nextvib.gbiomed.kuleuven.be/remote.php/webdav/bds.data"

ncdlink = "https://nextvib.gbiomed.kuleuven.be/index.php/apps/files/?dir=/bds.data/{prj}/data/{exp}/"
ncflink = "https://nextvib.gbiomed.kuleuven.be/remote.php/webdav/bds.data/{prj}/data/{exp}/{short}.{filename}"

#store on project/experiment ids? Or on checksum IDs?

checksum_based_urls = False

@fantail.arg('filename', nargs='+')
@fantail.arg('-d', '--description')
@fantail.command
def upload(app, args):

    for filename in args.filename:
        kfile = kmeta.get_kfile(app, filename)

        rid = kfile['short']

        #save all known metadata
        with tempfile.NamedTemporaryFile(delete=False) as F:
            meta = F.name
            for k, v in kfile.as_items(transient=False):
                F.write(f"{k}: {v}\n".encode())

        if checksum_based_urls:
            sha256 = kfile.khash.sha256
            f1 = sha256[:2]
            f2 = sha256[2:4]
            f3 = sha256[4:6]
            furl = f'{k3url}/{f1}/{f2}/{f3}/{sha256}'
            furl_meta = f'{k3url}/{f1}/{f2}/{f3}/{sha256}.{rid}.meta'
            script = dedent(f"""
               curl -s --netrc -X MKCOL {k3url}/{f1} >> k3.upload.out
               curl -s --netrc -X MKCOL {k3url}/{f1}/{f2} >> k3.upload.out
               curl -s --netrc -X MKCOL {k3url}/{f1}/{f2}/{f3} >> k3.upload.out
               curl -s --netrc -T {filename} {furl} >> k3.upload.out
               curl -s --netrc -T {meta} {furl_meta} >> k3.upload.out
            """)

        else:

            pid = kfile['project']
            eid = kfile['experiment']

            assert pid

            if eid is None:
                eid = pid

            if args.description:
                kfile.set('description', args.description)

            desc = kfile['description']
            if not desc:
                app.error("You must proved a description for this file")
                app.error(f"Try: k3 set desc 'meaningful description' {kfile['basename']}")
                return

            furl = f'{k3url}/{pid}/data/{eid}/{rid}.{kfile["basename"]}'
            furl_meta = f'{k3url}/{pid}/data/{eid}/{rid}.{kfile["basename"]}.k3meta.tsv'
            script = dedent(f"""
               curl -s --netrc -X MKCOL {k3url}/{pid} >> k3.upload.out
               curl -s --netrc -X MKCOL {k3url}/{pid}/data/ >> k3.upload.out
               curl -s --netrc -X MKCOL {k3url}/{pid}/data/{eid} >> k3.upload.out
               curl --netrc -T {filename} {furl} >> k3.upload.out
               curl -s --netrc -T {meta} {furl_meta} >> k3.upload.out
            """)

        # simply assuming that errors indicate that the file already exists
        # TODO: better error handling!
        app.message(f"upload to: {furl}")
        os.system(script)
        kmeta.kfile_set(app, kfile, 'xlink', furl)
        app.run_hook('file_upload', kfile, furl)


@fantail.flag('-m', '--meta', help='download and apply stored metadata')
@fantail.arg('filename', nargs='?')
@fantail.arg('checksum')
@fantail.command
def download(app, args):

    csum = args.checksum

    if len(csum) == 10 and csum[0] == 'f':
        khash = kmeta.find_khash(app, short=csum)
        sha256 = khash.sha256
    elif len(csum) == 64:
        khash = kmeta.find_khash(app, sha256=csum)
        if khash is None:
            sha256 = csum
    else:
        lg.warning("Not implemented")

    if sha256 is None:
        lg.warning("Cannot find the checksum - need a sha256 attempt download")
        return

    if checksum_based_urls:

        # what is the filename to download?
        filename = None
        if args.filename:
            filename = args.filename
        elif khash is not None:
            # we know the file - see if there is a basename to use
            filename = khash['basename']

        if not filename:
            lg.warning("We have no filename to use, please provide one")
            return

        f1 = sha256[:2]
        f2 = sha256[2:4]
        f3 = sha256[4:6]

        durl = f'{k3url}/{f1}/{f2}/{f3}/'
        furl = f'{k3url}/{f1}/{f2}/{f3}/{sha256}'

        # download file
        script = dedent(f"""
           curl -s --netrc -o {filename} {furl}
        """)
        os.system(script)

        if args.meta:
            # experimental -
            script = dedent(f"""
                curl -i -s --netrc -X PROPFIND {durl} --upload-file - -H "Depth: 1" <<end
                <?xml version="1.0"?>
                <a:propfind xmlns:a="DAV:">
                <a:prop><a:resourcetype/></a:prop>
                </a:propfind>
                end
                """)

            out = check_output(script, shell=True).decode('UTF8')
            print(out)
            rex = f'({sha256}\.[^\.]+\.meta)'
            tmpdir = tempfile.mkdtemp()

            burl = 'curl -s --netrc -o {} ' + f'{k3url}/{f1}/{f2}/{f3}/' + '{}'
            script2 = []
            mdfiles = []
            for hit in re.finditer(rex, out):
                hit = hit.groups()[0]
                outfile = tmpdir + '/' + hit
                mdfiles.append(outfile)

                script2.append(burl.format(outfile, hit))

            os.system("\n".join(script2))

    else:
        #depend on an xlink attribute
        xlinks = khash['xlink']
        print(xlinks)
#        if not 'xlink' in khash:
#            app.error("No record of this file uploaded")
#            return
        print('x' * 200)
        for xl in khash['xlink']:
            print(xl)

        exit()
        lg.warning("NOT IMPLEMETNED")
        args.meta = False


    # create a kfile - ie register the file
    kfile = kmeta.get_kfile(app, filename)

    if args.meta:
        for mdfile in mdfiles:
            with open(mdfile) as F:
                for line in F:
                    line = line.strip()
                    if not line: continue
                    k, v = line.split(':', 1)
                    if k in ['basename', 'xlink']:
                        continue

                    kmeta.kfile_set(app, kfile, k, v)
