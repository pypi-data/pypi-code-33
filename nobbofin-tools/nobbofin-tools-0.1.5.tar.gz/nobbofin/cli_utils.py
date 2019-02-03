import asyncio

import simplejson as json
import socket
import subprocess
import pathlib
from os import path

from datetime import timedelta, datetime
from nobbofin.downloaders import fints, dkbvisa, coba_docs, dkb_docs, congstar_docs


def mkdirs(newdir):
    pathlib.Path(newdir).mkdir(parents=True, exist_ok=True)


def recently_updated(filename, threshold=timedelta(hours=12)):
    last_modified = datetime.fromtimestamp(path.getmtime(filename))
    return datetime.now() < (last_modified + threshold)


async def run(cmd, cwd):
    proc = await asyncio.create_subprocess_shell(
        cmd, cwd=cwd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    print(f"[{cmd!r} exited with {proc.returncode}]")
    if stdout:
        print(f"[stdout]\n{stdout.decode()}")
    if stderr:
        print(f"[stderr]\n{stderr.decode()}")


async def run_append(cmd, cwd, filename):

    proc = await asyncio.create_subprocess_shell(
        cmd, cwd=cwd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode == 0:
        with open(filename, "a") as f:
            f.write(stdout.decode())
    else:
        print(f"[{cmd!r} exited with {proc.returncode}]")
        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")


async def create_temp_dir():
    proc = await asyncio.create_subprocess_shell(
        "mktemp -d", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    assert proc.returncode == 0, "mktemp -d failed"
    return stdout.decode().strip("\n")


async def dl_fints(
    url,
    username,
    password,
    blz,
    dest,
    begin=datetime.today() - timedelta(days=30),
    end=datetime.today(),
):
    mkdirs(dest)
    assert username
    assert password
    assert blz
    assert url
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(
        None, fints.read_fints, blz, username, password, url, begin, end
    )
    filename = (
        f"{data['balance']['date']} FinTS {blz} {begin.date()} - {end.date()}.json"
    )

    with open(path.join(dest, filename), "w", encoding="utf-8") as outfile:
        json.dump(
            data, outfile, use_decimal=True, default=str, indent=4, sort_keys=True
        )
    print("fetched FinTS transactions from", url)


async def dl_dkbvisa(username, password, dest):
    mkdirs(dest)
    assert username
    assert password
    loop = asyncio.get_event_loop()
    balance_date, csv_data = await loop.run_in_executor(
        None, dkbvisa.read_dkbvisa, username, password
    )
    filename = f"{balance_date} DKBVISA {username}.csv"

    with open(path.join(dest, filename), "w", encoding="utf-8") as outfile:
        outfile.write(csv_data)
    print("fetched DKBVISA transactions")


def _build_filename(date, filename):
    return date.strftime("%Y-%m-%d") + "_" + filename


async def dl_coba_docs(username, password, dest, min_date):
    mkdirs(dest)
    assert username
    assert password
    loop = asyncio.get_event_loop()
    dl = coba_docs.CobaDocDownloader()
    await loop.run_in_executor(None, dl.login, username, password)
    docs = await loop.run_in_executor(None, dl.list)

    for d in docs:
        if d["date"] < min_date:
            continue
        bc_filename = _build_filename(d["date"], d["filename"])
        bc_path = path.join(dest, bc_filename)
        if path.exists(bc_path):
            # skipping file
            continue

        content = await loop.run_in_executor(None, dl.download, d)

        with open(bc_path, "wb") as f:
            f.write(content)

        print("downloaded", d["filename"])


async def dl_dkb_docs(username, password, dest, min_date):
    mkdirs(dest)
    assert username
    assert password
    loop = asyncio.get_event_loop()
    dl = dkb_docs.DKBDocDownloader()
    await loop.run_in_executor(None, dl.login, username, password)
    docs = await loop.run_in_executor(None, dl.list_visa) + await loop.run_in_executor(
        None, dl.list_giro
    )

    for d in docs:
        if d["date"] < min_date:
            continue
        bc_filename = _build_filename(d["date"], d["filename"])
        bc_path = path.join(dest, bc_filename)
        if path.exists(bc_path):
            # skipping file
            continue

        content = await loop.run_in_executor(None, dl.download, d)

        with open(bc_path, "wb") as f:
            f.write(content)

        print("downloaded", d["filename"])


async def dl_congstar_docs(username, password, dest, min_date):
    mkdirs(dest)
    assert username
    assert password
    loop = asyncio.get_event_loop()
    dl = congstar_docs.CongstarDocDownloader()
    await loop.run_in_executor(None, dl.login, username, password)
    docs = await loop.run_in_executor(None, dl.list)

    for d in docs:
        if d["date"] < min_date:
            continue
        bc_filename = _build_filename(d["date"], d["filename"])
        bc_path = path.join(dest, bc_filename)
        if path.exists(bc_path):
            # skipping file
            continue

        content = await loop.run_in_executor(None, dl.download, d)

        with open(bc_path, "wb") as f:
            f.write(content)

        print("downloaded", d["filename"])


def tcp_open(port, host="localhost", timeout=300):
    try:
        s = socket.create_connection((host, port), timeout)
        s.close()
        return True
    except socket.error:
        pass


async def wait_n_surf(host, port):
    while not tcp_open(port, host):
        await asyncio.sleep(0.5)

    subprocess.run(["open", f"http://{host}:{port}"])
