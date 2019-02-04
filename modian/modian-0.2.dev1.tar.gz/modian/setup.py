
import json
import platform
import os
import shutil
import stat
import sys
import tarfile

try:
    from urllib.request import urlretrieve, urlopen
except:
    # Python 2
    from urllib import urlretrieve
    from urllib2 import urlopen

##
# Setup PATH env for custom modian installations
#
if platform.system() == "Windows":
    PREFIXES = [os.getenv("APPDATA"), "modian"]
    binpaths = [os.path.join(p,"bin") for p in PREFIXES] \
                + [os.path.join(p,"Library","bin") for p in PREFIXES]
else:
    PREFIXES = [os.path.join(os.path.expanduser("~"), ".local", "share", "modian")]
    binpaths = [os.path.join(p, "bin") for p in PREFIXES]

binpaths = [p for p in binpaths if os.path.exists(p)]
if binpaths:
    os.environ["PATH"] = "%s:%s" % (":".join(binpaths), os.environ["PATH"])
#
##

def conda_package_url(name, version=None, label="main"):
    system = platform.system().lower()
    machine = platform.machine()
    fd = urlopen("http://api.anaconda.org/package/{}".format(name))
    data = json.load(fd)
    fd.close()
    if version is None:
        version = data["latest_version"]
    b = None
    for f in data["files"]:
        if f["version"] != version:
            continue
        if label not in f["labels"]:
            continue
        if f["attrs"]["operatingsystem"] is not None:
            if f["attrs"]["operatingsystem"] != system:
                continue
            if f["attrs"]["machine"] != machine:
                continue
        if b is None or f["attrs"]["build_number"] > b["attrs"]["build_number"]:
            b = f
    return "http:{}".format(b["download_url"]) if b else None

def prepare_dest(dest):
    destdir = os.path.dirname(dest)
    if not os.path.exists(destdir):
        os.makedirs(destdir)

def conda_package_extract(conda_url, prefix, **opts):
    print("downloading {}".format(conda_url))
    localfile = urlretrieve(conda_url)[0]
    fmt = conda_url.split(".")[-1]
    def match_member(m):
        return m.name.split('/')[0] != 'info'
    def make_dest(prefix, m):
        return os.path.join(prefix, m.name)
    if "make_dest" in opts:
        make_dest = opts["make_dest"]
    with tarfile.open(localfile, "r:%s"%fmt) as tar:
        for m in tar:
            if match_member(m):
                dest = make_dest(prefix, m)
                print("installing %s" % dest)
                tar.extract(m, prefix, dest)
    os.unlink(localfile)

def is_installed(progname):
    if sys.version_info[0] < 3:
        paths = os.environ["PATH"].split(":")
        for p in paths:
            if os.path.exists(os.path.join(p, progname)):
                return True
        return False
    print(shutil.which(progname))
    return shutil.which(progname) is not None

def installation_prefix():
    if platform.system() == "Windows":
        return PREFIXES[0]
    if os.getuid() == 0:
        return PREFIXES[0]
    else:
        return PREFIXES[-1]

def setup(*specs):
    in_conda = os.path.exists(os.path.join(sys.prefix, 'conda-meta'))
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-f", "--force", default=False, action="store_true",
            help="Force installation")
    args = parser.parse_args()
    prefix = installation_prefix()
    for spec in specs:
        name = spec["pkg"].split('/')[-1]
        if not args.force:
            print("# checking for {}".format(name))
            skip = True
            for prog in spec.get("check_progs", []):
                if not is_installed(prog):
                    skip = False
                    break
            if skip and "check_install" in spec:
                skip = spec["check_install"]()
            if skip:
                print("# {} is already installed.".format(name))
                continue
        print("# installing {} in {}".format(spec["pkg"], prefix))
        if "install" in spec:
            spec["install"](prefix)
            continue
        if in_conda:
            subprocess.call(["conda", "install", spec["pkg"]])
            continue
        pkg = conda_package_url(spec["pkg"])
        if pkg is None:
            print("Error: no package found for your system!")
            continue
        conda_package_extract(pkg, prefix, **opts)

def nusmv_install(prefix):
    def chmod_x(filename):
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    def prepare_dest(dest):
        destdir = os.path.dirname(dest)
        if not os.path.exists(destdir):
            os.makedirs(destdir)

    def install_bin_from_tar(tar, member, dest):
        fd = tar.extractfile(member)
        print("installing %s" % dest)
        prepare_dest(dest)
        with open(dest, "wb") as o:
            o.write(fd.read())
        fd.close()
        chmod_x(dest)

    def install_from_tarurl(url, match_member, prefix):
        localfile = urlretrieve(url)[0]
        with tarfile.open(localfile, "r:gz") as t:
            for m in t:
                if match_member(m):
                    dest = os.path.join(prefix, "bin", os.path.basename(m.name))
                    install_bin_from_tar(t, m, dest)
        os.unlink(localfile)

    system = platform.system().lower()
    if system == "linux":
        system = "%s%s" % (system, platform.architecture()[0][:2])
    url_pat = "http://nusmv.fbk.eu/distrib/NuSMV-2.6.0-%s.tar.gz"
    binfile = {
        "linux64": url_pat % "linux64",
        "linux32": url_pat % "linux32",
        "darwin": url_pat % "macosx64",
        "windows": url_pat % "win32",
    }
    binfile = binfile.get(system)
    def match_entry(m):
        return m.name.endswith("bin/NuSMV") \
            or  m.name.endswith("bin/NuSMV.exe")
    install_from_tarurl(binfile, match_entry, prefix)

if __name__ == "__main__":
    setup({"pkg": "conda-forge/graphviz", "check_progs": ["dot"]},
            {"pkg": "nusmv", "check_progs": ["NuSMV"],
                "install": nusmv_install})

