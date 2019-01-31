

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

# from http://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python
def chmodX(filePath):
    st = os.stat(filePath)
    os.chmod(filePath, st.st_mode | stat.S_IEXEC)

def checkEnv(keyList):
    for key in keyList:
        if not os.environ.get(key):
            raise ValueError("Environment variable " + key + " not defined")
    return True

# emulates find unix command
def find(sType='file', **kwargs):

    patt = kwargs['name'].replace("*", ".*")
    if 'path' not in kwargs and 'name' not in kwargs:
        raise ValueError
    if sType == 'file':
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(kwargs['path']) for f in filenames if re.match(patt, f)]

    if sType == 'dir':
        result = [os.path.join(dp, d) for dp, dn, filenames in os.walk(kwargs['path']) for d in dn if re.match(patt, d)]

    return result


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
